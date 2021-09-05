/*
 * test.js
 * Copyright (C) 2015 Kovid Goyal <kovid at kovidgoyal.net>
 *
 * Distributed under terms of the BSD license.
 */
"use strict"; /*jshint node:true */
var path = require("path");
var fs = require("fs");
var JPython = require("./compiler").create_compiler();
var utils = require("./utils");
var colored = utils.safe_colored;

module.exports = function (argv, base_path, src_path, lib_path) {
  // run all tests and exit
  var assert = require("assert");
  var os = require("os");
  var failures = [];
  var vm = require("vm");
  var compiler_dir = path.join(base_path, "dev");
  if (!utils.path_exists(path.join(compiler_dir, "compiler.js")))
    compiler_dir = path.join(base_path, "release");
  var test_path = path.join(base_path, "test");
  var baselib = fs.readFileSync(
    path.join(lib_path, "baselib-plain-pretty.js"),
    "utf-8"
  );
  var files;
  var deep_eq = assert.deepEqual;
  assert.deepEqual = function (a, b, message) {
    // Compare array objects that have extra properties as simple arrays
    if (Array.isArray(a) && Array.isArray(b)) {
      if (a === b) return;
      if (a.length !== b.length)
        throw new assert.AssertionError({
          actual: a,
          expected: b,
          operator: "deepEqual",
          stackStartFunction: assert.deepEqual,
        });
      for (var i = 0; i < a.length; i++) assert.deepEqual(a[i], b[i], message);
    } else if (
      a !== undefined &&
      a !== null &&
      typeof a.__eq__ === "function"
    ) {
      if (!a.__eq__(b))
        throw new assert.AssertionError({
          actual: a,
          expected: b,
          operator: "deepEqual",
          stackStartFunction: assert.deepEqual,
        });
    } else return deep_eq(a, b, message);
  };

  if (argv.files.length) {
    files = [];
    argv.files.forEach(function (fname) {
      files.push(fname + ".py");
    });
  } else {
    files = fs.readdirSync(test_path).filter(function (name) {
      return /^[^_].*\.py$/.test(name);
    });
  }
  files.forEach(function (file) {
    const t0 = new Date();
    var ast;
    var filepath = path.join(test_path, file);
    var failed = false;
    try {
      ast = JPython.parse(fs.readFileSync(filepath, "utf-8"), {
        filename: file,
        toplevel: ast,
        basedir: test_path,
        libdir: path.join(src_path, "lib"),
      });
    } catch (e) {
      failures.push(file);
      failed = true;
      console.log(colored(file, "red") + ": " + e + "\n\n");
      return;
    }

    // generate output
    var output = new JPython.OutputStream({
      baselib_plain: baselib,
      beautify: true,
      keep_docstrings: true,
    });
    ast.print(output);

    // test that output performs correct JS operations
    var jsfile = path.join(os.tmpdir(), file + ".js");
    var code = output.toString();
    try {
      vm.runInNewContext(
        code,
        {
          assrt: assert,
          __name__: jsfile,
          require: require,
          fs: fs,
          RapydScript: JPython, // todo...
          JPython,
          console,
          compiler_dir,
          test_path,
          Buffer: Buffer,
        },
        { filename: jsfile }
      );
    } catch (e) {
      failures.push(file);
      failed = true;
      fs.writeFileSync(jsfile, code);
      console.error("Failed running: " + colored(jsfile, "red"));
      if (e.stack)
        console.error(colored(file, "red") + ":\n" + e.stack + "\n\n");
      else console.error(colored(file, "red") + ": " + e + "\n\n");
    }
    console.log(
      `${colored(file, "green")}: test ${
        failed ? "FAILED" : "completed successfully"
      } (${new Date().valueOf() - t0}ms)`
    );
  });

  if (failures.length) {
    console.log(
      colored("There were " + failures.length + " test failure(s):", "red")
    );
    console.log.apply(console, failures);
  } else console.log(colored("All tests passed!", "green"));
  process.exit(failures.length ? 1 : 0);
};
