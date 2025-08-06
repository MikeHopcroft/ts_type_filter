#!/usr/bin/env python3
"""
Enhanced TypeScript parser with flexible comment support.

This module contains an enhanced version of the TypeScript parser that supports:
- /* */ block comments anywhere they're legal in TypeScript
- // line comments anywhere they're legal in TypeScript
- Comments between lines of multi-line type declarations
- Comments to the right of declaration text
- Preservation of "Hint:" prefix behavior
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

# Enhanced grammar - we'll use the original grammar but preprocess comments
enhanced_grammar = r"""
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

def preprocess_text(text):
    """
    Preprocess text to extract and handle comments properly.
    This function removes comments from the text but preserves hint comments.
    """
    # Step 1: Handle block comments first
    def process_block_comment(match):
        comment_content = match.group(0)
        # Check if it's a hint comment
        if comment_content.startswith('/* Hint: '):
            # Extract hint content, removing /* Hint: and */
            hint_content = comment_content[9:-2].strip()
            return f'// Hint: {hint_content}\n'
        else:
            # Replace with equivalent whitespace to maintain positions
            lines_in_comment = comment_content.count('\n')
            return '\n' * lines_in_comment + ' ' * (len(comment_content.split('\n')[-1]))
    
    # Process block comments
    block_comment_pattern = r'/\*[\s\S]*?\*/'
    text_after_blocks = re.sub(block_comment_pattern, process_block_comment, text)
    
    # Step 2: Handle line comments
    lines = text_after_blocks.split('\n')
    result_lines = []
    
    for line in lines:
        # Find line comments
        line_comment_match = re.search(r'//.*$', line)
        if line_comment_match:
            comment_text = line_comment_match.group(0)
            line_before_comment = line[:line_comment_match.start()].rstrip()
            
            # Check if it's a hint comment
            if comment_text.startswith('// Hint: '):
                # If the line has TypeScript content before the comment, split it
                if line_before_comment.strip():
                    result_lines.append(line_before_comment)
                    result_lines.append(comment_text)
                else:
                    # This is a hint comment on its own line
                    result_lines.append(comment_text)
            else:
                # Non-hint comment - remove it but keep any content before it
                if line_before_comment.strip():
                    result_lines.append(line_before_comment)
                else:
                    # Empty line
                    result_lines.append('')
        else:
            # No comment on this line
            result_lines.append(line)
    
    return '\n'.join(result_lines)

# Lazy initialization of enhanced parser
_enhanced_parser = None

def get_enhanced_parser():
    global _enhanced_parser
    if _enhanced_parser is None:
        import lark
        _enhanced_parser = lark.Lark(enhanced_grammar, start="start")
    return _enhanced_parser

def isToken(node, type_name):
    import lark
    return isinstance(node, lark.Token) and node.type == type_name

def parse_enhanced(text):
    """
    Enhanced parse function with flexible comment support.
    """
    import lark
    
    # Preprocess to handle comments
    clean_text = preprocess_text(text)
    
    # Create Enhanced Transformer class - mostly the same as original
    class EnhancedParseTransformer(lark.Transformer):
        def lines(self, children):
            result = []
            for child in children:
                if isToken(child, "COMMENT"):
                    if child.value.startswith("// Hint: "):
                        result.append("// " + child.value[9:])
                    # Note: Non-hint comments are ignored by the preprocessing step
                else:
                    result.append(child)
            return result

        def define(self, children):
            hint = None
            while isToken(children[0], "COMMENT"):
                comment_value = children.pop(0).value
                if comment_value.startswith("// Hint: "):
                    hint = comment_value[9:].strip()  # Strip `// Hint: ` from comment token
                else:
                    hint = comment_value[2:].strip()  # Strip `// ` from comment token

            name = children.pop(0).value  # Get the name of the type
            params = (
                children.pop(0) if type(children[0]) == list else []
            )  # Get type parameters if any
            value = children.pop()  # The type definition itself
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
            if isToken(items[0], "QUESTION"):
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
    
    parser = get_enhanced_parser()
    tree = parser.parse(clean_text)
    return EnhancedParseTransformer().transform(tree)

if __name__ == "__main__":
    # Test the enhanced parser
    test_cases = [
        "// Hint: This is a hint\ntype A = B;",
        "type A = B; // inline comment",
        "type A = /* comment */ B;",
        "/* Hint: Block hint */\ntype A = B;",
        """type A = {
  // field comment
  field: string
};""",
        """type A<
  // param comment
  T
> = B;""",
        """type A = B |
  // union comment
  C;""",
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test {i+1} ---")
        print(f"Input: {repr(test_case)}")
        try:
            result = parse_enhanced(test_case)
            formatted = '\n'.join([node.format() for node in result])
            print(f"✅ Success: {formatted}")
        except Exception as e:
            print(f"❌ Failed: {e}")
