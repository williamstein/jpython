# Hacking the JPython compiler

The JPython compiler is written in JPython itself and uses theJPython import system to modularize its code. The compiler source code isin the `src` directory. The compiled compiler is by default in the `release`directory. The compiler itself _**only takes a few seconds**_ to build from source and bootstrap itself.

In order to start hacking on the compiler, run the command

```sh
npm run test
```

This will generate a build of the compiler in the `dev` directory. Now, the`jpython` command will automatically use this build, rather than the one inrelease. If you want to go back to the release build, simply delete the `dev`directory.

## Code organization

The way the compiler works, given some JPython source code:

- The source code is lexed into a stream of tokens (`src/tokenzier.py`)
- The tokens are parsed into a Abstract Syntax Tree (`src/parse.py and src/ast.py`)
- During parsing any import statement are resolved (this is different frompython, where imports happen at runtime, not compile time).
- The Abstract Syntax Tree is transformed into the output JavaScript (`src/output/*.py`)
- Various bits of functionality in JPython depend upon the _Base Library_
  (`src/baselib*.py`). This includes things like the basic container types
  (list/set/dict) string functions such as `str.format()`, etc. The baselib
  is automatically inserted into the start of the output JavaScript.

The JPython standard library can be found in `src/lib`. The various tools,
such as the linter, gettext support, the REPL, etc. are in the `tools`
directory.

## Tests

The tests are in the test directory and can be run using the command:

```
rapydscript test
```

You can run individual test files by providing the name of the file, as

```
rapydscript test classes
```

## Modifying the compiler

Edit the files in the `src` directory to make your changes, then use the`./try.py` script to test them. This script will compile an updated version ofthe compiler with your changes, if any, and use it to run the snippet of codeyou pass to it.

For example:

```sh
~/jpython$ ./try.py 'print("Hello world")'
```

will compile `print ("Hello world")` and show you the output on stdout. You can
tell it to omit the baselib, so you can focus on the output, with the `-m`
switch, like this:

```sh
~/jpython$ ./try.py -m 'print("Hello world")'
There are changes to the source files of the compiler, rebuilding
Compiler built in 0.899 seconds

(function(){
    "use strict";
    (function(){
        var __name__ = "__main__";
        print("Hello world");
    })();
})();
```

You can also have it not print out the JavaScript, instead directly executing the output
JavaScript with the `-x` switch, like this

```sh
~/jpython$ ./try.py -x 'print("Hello world")'
```

If you want to test longer sections of code, you can use the `-f` switch to
pass in the path to a JPython file to compile, like this:

```sh
~/jpython$ ./try.py -f myfile.py
```

Once you are happy with your changes, you can build the compiler and run the
test suite, all with a single command:

```sh
~/jpython$ npm run test
```

This will build the compiler with the updated version of itself and then runthe test suite.
