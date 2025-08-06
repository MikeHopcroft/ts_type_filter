The parser in ts_type_filter/parser.py is designed to parse a subset of Typescript type definitions.
It currently has limited support for comments as follows:

* Comments are a top-level grammar production so they can only appear on lines by themselves.
* Only // comments are supported.
* Comments starting with `// Hint:` are retained in the AST with the "Hint" stripped off.
* Other comments are not preserved in the AST.

I would like to modify the parser to support the following cases:

* /* */ comments anywhere they are legal in TypeScript
* // comments anywhere they are legal in TypeScript. This includes between lines of multi-line type declarations and to the right of declaration text.
* The comments should still retain the behavior, regarding the "Hint:" prefix.

Please put any debug scripts in the `copilot/parser` folder.
Unit test scripts can go in the `tests` folder.