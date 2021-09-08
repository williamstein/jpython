/*
 * Copyright (C) 2021 William Stein <wstein@sagemath.com>
 * Copyright (C) 2015 Kovid Goyal <kovid at kovidgoyal.net>
 *
 * Distributed under terms of the BSD license
 */

// Thin wrapper around (release|dev)/compiler.js to setup some global facilities and
// export the compiler's symbols safely.

import { join, relative } from "path";
import { readFileSync, writeFileSync } from "fs";
import { createContext, runInContext } from "vm";
import { pathExists, sha1sum } from "./utils";

type Compiler = any; // for now

export default function createCompiler(): Compiler {
  const compiler_exports: Compiler = {};
  const compiler_context = createContext({
    console: console,
    readfile: readFileSync,
    writefile: writeFileSync,
    sha1sum: sha1sum,
    require: require,
    exports: compiler_exports,
  });

  const base = join(__dirname, "..", "..");
  let compiler_dir = join(base, "dev");
  if (!pathExists(join(compiler_dir, "compiler.js"))) {
    compiler_dir = join(base, "release");
  }
  const compiler_file = join(compiler_dir, "compiler.js");
  const compilerjs = readFileSync(compiler_file, "utf-8");
  runInContext(compilerjs, compiler_context, relative(base, compiler_file));
  return compiler_exports;
}
