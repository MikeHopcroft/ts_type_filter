#!/usr/bin/env python3
"""
Simple and robust enhanced parser.
This version uses a simple preprocessing approach that works correctly.
"""

import ast
import re
from ts_type_filter import (
    Any,
    Array,
    Define,
    Literal,
    Never,
    ParamDef,
    Struct,
    Type,
    Union,
)

# Original grammar - no changes needed
grammar = r"""
?start: lines

lines: (define | COMMENT)*

define: "type" CNAME type_params? "=" type (";")?

type_params: "<" param_def ("," param_def)* ">"
param_def: CNAME ("extends" type)?

?type: union

?union: ("|")? intersection ("|" intersection)*
?intersection: array

array: primary array_suffix*
array_suffix: "[" "]"

?primary: literal
        | literalex
        | "never"         -> never
        | "any"           -> any
        | type_ref
        | struct
        | "(" type ")"

type_ref: CNAME type_args?
type_args: "<" type ("," type)* ">"

struct: "{" [field (("," | ";") field)*] ("," | ";")? "}"
field: CNAME QUESTION? ":" type
QUESTION: "?"

literalex: "LITERAL" "<" string_literal "," string_literal_list "," boolean_literal ">"
?string_literal_list: "[" (string_literal ("," string_literal)*)? "]"
?boolean_literal: TRUE | FALSE
TRUE: "true"
FALSE: "false"

literal: numeric_literal | string_literal
numeric_literal: SIGNED_NUMBER
string_literal: ESCAPED_STRING | ESCAPED_STRING2

COMMENT: /\/\/[^\n]*/
ESCAPED_STRING2 : "'" _STRING_ESC_INNER "'"
%import common.CNAME
%import common.ESCAPED_STRING
%import common._STRING_ESC_INNER
%import common.SIGNED_NUMBER
%import common.WS
%ignore WS
"""

def preprocess_for_enhanced_comments(text):
    """
    Simple preprocessing that converts all comment types to line comments
    and moves hint comments to separate lines.
    """
    result_lines = []
    lines = text.split('\n')
    
    for line in lines:
        current_line = line
        
        # Step 1: Handle block comments on this line
        while True:
            block_match = re.search(r'/\*[\s\S]*?\*/', current_line)
            if not block_match:
                break
            
            comment_content = block_match.group(0)
            before_comment = current_line[:block_match.start()]
            after_comment = current_line[block_match.end():]
            
            if comment_content.startswith('/* Hint: '):
                # Convert block hint to line hint and put it before the type definition
                hint_content = comment_content[9:-2].strip()
                result_lines.append(f'// Hint: {hint_content}')
                
                # Remove the comment but join the before and after parts
                current_line = before_comment + after_comment
            else:
                # Remove non-hint block comment, replace with space
                current_line = before_comment + ' ' + after_comment
        
        # Step 2: Handle line comments
        line_comment_match = re.search(r'//.*$', current_line)
        if line_comment_match:
            comment_text = line_comment_match.group(0)
            line_before_comment = current_line[:line_comment_match.start()].rstrip()
            
            if comment_text.startswith('// Hint: '):
                # This is a hint comment - keep the original behavior
                if line_before_comment.strip():
                    # There's TypeScript code before the comment - split them
                    result_lines.append(line_before_comment)
                    result_lines.append(comment_text)
                else:
                    # Hint comment is on its own line
                    result_lines.append(comment_text)
            else:
                # Non-hint comment - remove it
                if line_before_comment.strip():
                    result_lines.append(line_before_comment)
                # else: empty line, skip it
        else:
            # No line comment, add the line if it has content
            if current_line.strip():
                result_lines.append(current_line)
    
    return '\n'.join(result_lines)

# Lazy initialization of parser
_parser = None

def get_parser():
    global _parser
    if _parser is None:
        import lark
        _parser = lark.Lark(grammar, start="start")
    return _parser

def isToken(node, type_name):
    import lark
    return isinstance(node, lark.Token) and node.type == type_name

def parse_simple_enhanced(text):
    """
    Simple enhanced parse function.
    """
    import lark
    
    # Preprocess to handle flexible comments
    processed_text = preprocess_for_enhanced_comments(text)
    
    # Use the original transformer logic
    class SimpleParseTransformer(lark.Transformer):
        def lines(self, children):
            result = []
            for child in children:
                if isToken(child, "COMMENT"):
                    if child.value.startswith("// Hint: "):
                        result.append("// " + child.value[9:])
                else:
                    result.append(child)
            return result

        def define(self, children):
            hint = None
            while children and isToken(children[0], "COMMENT"):
                hint = children.pop(0).value[2:].strip()

            name = children.pop(0).value
            params = children.pop(0) if children and type(children[0]) == list else []
            value = children.pop()
            return Define(name, params, value, hint)

        def type_params(self, items):
            return items

        def param_def(self, items):
            name = items[0]
            extends = items[1] if len(items) > 1 else None
            return ParamDef(name, extends)

        def type_ref(self, items):
            name = items[0].value
            params = items[1] if len(items) > 1 else None
            return Type(name, params)

        def type_args(self, items):
            return items

        def array(self, items):
            result = items[0]
            for _ in range(len(items) - 1):
                result = Array(result)
            return result

        def struct(self, items):
            return Struct(dict(items))

        def field(self, items):
            name = items.pop(0).value
            if items and isToken(items[0], "QUESTION"):
                name = name + "?"
                items.pop(0)
            value = items.pop(0)
            return [name, value]

        def literal(self, items):
            return Literal(items[0])
        
        def literalex(self, items):
            text = items.pop(0)
            temp = items.pop(0)
            aliases = [temp] if isinstance(temp, str) else temp.children
            pinned = True if items.pop(0) == "true" else False
            return Literal(text, aliases, pinned)

        def string_literal(self, items):
            return ast.literal_eval(items[0])

        def numeric_literal(self, items):
            try:
                return int(items[0])
            except ValueError:
                return float(items[0])

        def never(self, _):
            return Never()

        def any(self, _):
            return Any

        def union(self, items):
            if len(items) == 1:
                return items[0]
            return Union(*items)
    
    parser = get_parser()
    tree = parser.parse(processed_text)
    return SimpleParseTransformer().transform(tree)

if __name__ == "__main__":
    # Test the simple enhanced parser
    test_cases = [
        ("// Hint: This is a hint\ntype A = B;", "// This is a hint\ntype A=B;"),
        ("type A = B; // Hint: trailing hint", "type A=B;\n// trailing hint"),
        ("type A = /* Hint: block hint */ B;", "// block hint\ntype A=B;"),
        ("type A = B; // regular comment", "type A=B;"),
        ("type A = /* regular block */ B;", "type A=B;"),
        ("""type A = {
  // field comment
  field: string
};""", "type A={field:string};"),
    ]
    
    for i, (source, expected) in enumerate(test_cases):
        print(f"\n--- Test {i+1} ---")
        print(f"Input: {repr(source)}")
        print(f"Expected: {repr(expected)}")
        try:
            result = parse_simple_enhanced(source)
            formatted = '\n'.join([str(node.format() if hasattr(node, 'format') else node) for node in result])
            print(f"✅ Actual: {repr(formatted)}")
            if formatted == expected:
                print("🎯 Match!")
            else:
                print("⚠️  Difference!")
        except Exception as e:
            print(f"❌ Failed: {e}")
            import traceback
            traceback.print_exc()
