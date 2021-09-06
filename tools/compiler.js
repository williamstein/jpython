/* vim:fileencoding=utf-8
 *
 * Copyright (C) 2015 Kovid Goyal <kovid at kovidgoyal.net>
 *
 * Distributed under terms of the BSD license
 */
"use strict"; /*jshint node:true */

// Thin wrapper around (release|dev)/compiler.js to setup some global facilities and
// export the compiler's symbols safely.

var path = require("path");
var fs = require("fs");
var crypto = require("crypto");
var vm = require("vm");

function sha1sum(data) {
  var h = crypto.createHash("sha1");
  h.update(data);
  return h.digest("hex");
}

function path_exists(path) {
  try {
    fs.statSync(path);
    return true;
  } catch (e) {
    if (e.code != "ENOENT") throw e;
  }
}

function create_compiler() {
  var compiler_exports = {};
  var compiler_context = vm.createContext({
    console: console,
    readfile: fs.readFileSync,
    writefile: fs.writeFileSync,
    sha1sum: sha1sum,
    require: require,
    exports: compiler_exports,
  });

  var base = path.dirname(path.dirname(module.filename));
  var compiler_dir = path.join(base, "dev");
  if (!path_exists(path.join(compiler_dir, "compiler.js")))
    compiler_dir = path.join(base, "release");
  var compiler_file = path.join(compiler_dir, "compiler.js");
  var compilerjs = fs.readFileSync(compiler_file, "utf-8");
  vm.runInContext(
    compilerjs,
    compiler_context,
    path.relative(base, compiler_file)
  );
  return compiler_exports;
}

exports.create_compiler = create_compiler;
