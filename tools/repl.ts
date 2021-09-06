/*
 * Copyright (C) 2021 William Stein <wstein@sagemath.com>
 * Copyright (C) 2015 Kovid Goyal <kovid at kovidgoyal.net>
 *
 * Distributed under terms of the BSD license.
 */

import { mkdirSync, readFileSync, writeFileSync } from "fs";
import { join } from "path";
import { runInThisContext } from "vm";
import { getImportDirs, colored, pathExists } from "./utils";
import completelib from "./completer";
import { create_compiler } from "./compiler";
import { clearLine, createInterface } from "readline";

const JPython = create_compiler();

const DEFAULT_HISTORY_SIZE = 1000;
const HOME =
  process.env[process.platform == "win32" ? "USERPROFILE" : "HOME"] ?? "/tmp";

function expandUser(x: string): string {
  return x.replace("~", HOME);
}

const CACHEDIR = process.env.XDG_CACHE_HOME
  ? expandUser(process.env.XDG_CACHE_HOME)
  : join(HOME, ".cache");

interface Options {
  input;
  output;
  show_js: boolean;
  ps1: string;
  ps2: string;
  console: Console;
  terminal: boolean;
  histfile: string;
  historySize: number;
  impPath: string;
  libPath: string;
}

function replDefaults(options: Partial<Options>): Options {
  if (!options.input) {
    options.input = process.stdin;
  }
  if (!options.output) {
    options.output = process.stdout;
  }
  if (options.show_js == null) {
    options.show_js = true;
  }
  if (!options.ps1) {
    options.ps1 = ">>> ";
  }
  if (!options.ps2) {
    options.ps2 = "... ";
  }
  if (!options.console) {
    options.console = console;
  }
  if (options.terminal == null) {
    options.terminal = !!options.output?.isTTY;
  }
  if (options.histfile == null) {
    const CACHE = join(CACHEDIR, "jpython");
    if (!pathExists(CACHE)) {
      mkdirSync(CACHE, { recursive: true });
    }
    options.histfile = join(CACHE, "history");
  }
  options.historySize = options.historySize ?? DEFAULT_HISTORY_SIZE;
  if (options.impPath == null) {
    throw Error("impPath must be specified");
  }
  if (options.libPath == null) {
    throw Error("libPath must be specified");
  }
  return options as Options;
}

function readHistory(options: Options): string[] {
  if (options.histfile) {
    if (!pathExists(options.histfile)) {
      return [];
    }
    try {
      return readFileSync(options.histfile, "utf-8").split("\n");
    } catch (err) {
      options.console.warn(`Error reading history file - ${err}`);
      return [];
    }
  }
  return [];
}

function writeHistory(options: Options, history: string[]): void {
  if (options.histfile) {
    try {
      return writeFileSync(options.histfile, history.join("\n"), "utf-8");
    } catch (err) {
      options.console.warn(`Error writing history file - ${err}`);
    }
  }
}

function createReadlineInterface(options: Options) {
  // See https://nodejs.org/api/readline.html#readline_readline_createinterface_options
  const completer = completelib(JPython, options);
  const history = options.terminal ? readHistory(options) : [];
  const readline = createInterface({
    input: options.input,
    output: options.output,
    completer,
    terminal: options.terminal,
    history,
    historySize: options.historySize,
    tabSize: 4,
  });
  // @ts-ignore -- needed for older node.js
  readline.history = history;
  return readline;
}

export default function Repl(options0: Partial<Options>) {
  const options = replDefaults(options0);
  const readline = createReadlineInterface(options);
  const ps1 = colored(options.ps1, "blue");
  const ps2 = colored(options.ps2, "green");

  initContext();

  const buffer: string[] = [];
  let more: boolean = false;
  const LINE_CONTINUATION_CHARS = ":\\";
  let toplevel;
  var importDirs = getImportDirs();

  options.console.log(
    colored(
      `Welcome to JPython.  Using Node.js ${process.version}.`,
      "green",
      true
    )
  );

  /*
  if (options.show_js) {
    options.console.log(
      colored(
        "Use show_js=False to stop the REPL from showing compiled JavaScript.",
        "green",
        true
      )
    );
  } else {
    options.console.log(
      colored(
        "Use show_js=True to have the REPL show compiled JavaScript before executing it.",
        "green",
        true
      )
    );
  }*/

  function printAST(ast, keepBaselib?: boolean) {
    const output = new JPython.OutputStream({
      omit_baselib: !keepBaselib,
      write_name: false,
      private_scope: false,
      beautify: true,
      keep_docstrings: true,
      baselib_plain: keepBaselib
        ? readFileSync(
            join(options.libPath, "baselib-plain-pretty.js"),
            "utf-8"
          )
        : undefined,
    });
    ast.print(output);
    return output.get();
  }

  function initContext() {
    // HORRIBLE TEMPORARY HACK: Install a hook so we can use js require directly from repl:
    global.__require__ = require;
    // @ts-ignore
    global.require = (name) => __require__(process.cwd() + "/" + name);

    // and get all the code and name.
    runInThisContext(printAST(JPython.parse("(def ():\n yield 1\n)"), true));
    runInThisContext('var __name__ = "__repl__"; show_js=false;');
  }

  function resetBuffer() {
    buffer.splice(0, buffer.length);
  }

  function prompt(): void {
    let leadingWhitespace = "";
    if (more && buffer.length) {
      let prev_line = buffer[buffer.length - 1];
      if (prev_line.trimRight().slice(-1) == ":") {
        leadingWhitespace = "    ";
      }
      // Add to leadingWhitespace all the blank space at the beginning of prev_line, if any.
      const match = prev_line.match(/^\s+/);
      if (match) {
        leadingWhitespace += match[0];
      }
    }
    readline.setPrompt(more ? ps2 : ps1);
    readline.prompt();
    if (leadingWhitespace) {
      readline.write(leadingWhitespace);
    }
  }

  function runJS(js: string): void {
    if (runInThisContext("show_js")) {
      options.console.log(
        colored("---------- Compiled JavaScript ---------", "green", true)
      );
      options.console.log(js);
      options.console.log(
        colored("---------- Running JavaScript ---------", "green", true)
      );
    }
    let result;
    try {
      result = runInThisContext(js);
    } catch (err) {
      if (err.stack) {
        options.console.error(err.stack);
      } else {
        options.console.error(err.toString());
      }
    }

    // TODO: very dumb temporary heuristic involving "="!
    // We don't want to print anything when the result is
    // from an assignment.  Easy to fool this of course with input "' = '".
    // Fix might be to use our AST parser :-).
    if (result != null && !js.includes(" = ") && global.ρσ_print != null) {
      // We just print out the last result using normal Python printing.
      // TODO: will move all this ρσ to a proper library.
      global.ρσ_print(result);
    }
  }

  // returns true if incomplete
  function compileAndRun(source: string): boolean {
    const classes = toplevel?.classes;
    const scoped_flags = toplevel?.scoped_flags;
    try {
      toplevel = JPython.parse(source, {
        filename: "<repl>",
        basedir: process.cwd(),
        libdir: options.impPath,
        import_dirs: importDirs,
        classes,
        scoped_flags,
      });
    } catch (err) {
      if (err.is_eof && err.line == buffer.length && err.col > 0) {
        return true;
      }
      if (err.message && err.line !== undefined) {
        options.console.log(err.line + ":" + err.col + ":" + err.message);
      } else {
        options.console.log(err.stack || err.toString());
      }
      return false;
    }
    const output = printAST(toplevel);
    if (classes) {
      const exports: { [name: string]: boolean } = {};
      for (const name in toplevel.exports) {
        exports[name] = true;
      }
      for (const name in classes) {
        if (!exports[name] && !toplevel.classes[name]) {
          toplevel.classes[name] = classes[name];
        }
      }
    }
    runJS(output);
    return false;
  }

  // returns true if incomplete
  function push(line: string): boolean {
    buffer.push(line);
    const trimmedLine = line.trimRight();
    if (
      trimmedLine &&
      LINE_CONTINUATION_CHARS.includes(trimmedLine.slice(-1))
    ) {
      // ends in continuation character after trimming whitespace
      return true;
    }
    const source = buffer.join("\n");
    if (!source.trim()) {
      // all whitespace
      resetBuffer();
      return false;
    }
    const isIncomplete = compileAndRun(source);
    if (!isIncomplete) {
      resetBuffer();
    }
    return isIncomplete;
  }

  readline.on("line", (line: string) => {
    if (more) {
      // We are in a block
      const lineIsEmpty = !line.trimLeft();
      if (
        lineIsEmpty &&
        buffer.length &&
        !buffer[buffer.length - 1].trimLeft()
      ) {
        // We have two empty lines, evaluate the block:
        more = push(line.trimLeft());
      } else {
        buffer.push(line);
      }
    } else {
      // Not in a block, evaluate line
      more = push(line);
    }
    prompt();
  });

  readline.on("history", (history) => {
    // Note -- this only exists in node >15.x.
    if (options.terminal) {
      writeHistory(options, history);
    }
  });

  readline.on("close", () => {
    const { history } = readline as any; //  deprecated in node 15...
    if (history) {
      writeHistory(options, history);
    }
    options.console.log();
    process.exit(0);
  });

  readline.on("SIGINT", () => {
    clearLine(options.output, 0);
    options.console.log("Keyboard Interrupt");
    resetBuffer();
    more = false;
    prompt();
  });

  readline.on("SIGCONT", prompt);

  prompt();
}
