#!/usr/bin/env python3
"""
Advanced enhanced parser with proper comment handling.
This implementation uses a two-pass approach:
1. Extract and catalog all comments with their positions
2. Parse the cleaned text and then reintegrate hint comments
"""

import ast
import re
from typing import List, Tuple, Dict, Any as AnyType
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

# Use the original grammar
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

class Comment:
    def __init__(self, content: str, line: int, col: int, is_hint: bool, is_block: bool):
        self.content = content
        self.line = line
        self.col = col
        self.is_hint = is_hint
        self.is_block = is_block
        
    def get_hint_text(self) -> str:
        """Extract hint text without the prefix."""
        if self.is_hint:
            if self.is_block:
                # Remove /* Hint: and */
                return self.content[9:-2].strip()
            else:
                # Remove // Hint: 
                return self.content[9:].strip()
        return ""

def extract_comments(text: str) -> Tuple[str, List[Comment]]:
    """
    Extract all comments from text and return cleaned text with comment catalog.
    """
    lines = text.split('\n')
    comments = []
    clean_lines = []
    
    for line_num, line in enumerate(lines):
        current_line = line
        line_comments = []
        
        # First, handle block comments
        block_pattern = r'/\*[\s\S]*?\*/'
        while True:
            match = re.search(block_pattern, current_line)
            if not match:
                break
            
            comment_content = match.group(0)
            is_hint = comment_content.startswith('/* Hint: ')
            col = match.start()
            
            comments.append(Comment(comment_content, line_num, col, is_hint, True))
            
            # Replace block comment with spaces to maintain column positions
            replacement = ' ' * len(comment_content)
            current_line = current_line[:match.start()] + replacement + current_line[match.end():]
        
        # Then handle line comments
        line_comment_match = re.search(r'//.*$', current_line)
        if line_comment_match:
            comment_content = line_comment_match.group(0)
            is_hint = comment_content.startswith('// Hint: ')
            col = line_comment_match.start()
            
            comments.append(Comment(comment_content, line_num, col, is_hint, False))
            
            # Remove line comment
            current_line = current_line[:line_comment_match.start()].rstrip()
        
        clean_lines.append(current_line)
    
    return '\n'.join(clean_lines), comments

def organize_comments_by_definition(text: str, comments: List[Comment]) -> Dict[int, List[Comment]]:
    """
    Organize comments by which type definition they should be associated with.
    """
    lines = text.split('\n')
    
    # Find all type definition lines
    type_def_lines = []
    for i, line in enumerate(lines):
        if re.match(r'\s*type\s+\w+', line):
            type_def_lines.append(i)
    
    # Associate comments with definitions
    comment_map = {}
    
    for comment in comments:
        if not comment.is_hint:
            continue  # Only process hint comments
            
        # Find which type definition this comment belongs to
        associated_def = None
        
        # Look for the next type definition after this comment
        for def_line in type_def_lines:
            if def_line > comment.line:
                associated_def = def_line
                break
        
        # If no definition found after, associate with the closest one before
        if associated_def is None and type_def_lines:
            associated_def = type_def_lines[-1]
        
        if associated_def is not None:
            if associated_def not in comment_map:
                comment_map[associated_def] = []
            comment_map[associated_def].append(comment)
    
    return comment_map

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

def parse_advanced(text):
    """
    Advanced parser with proper comment handling.
    """
    import lark
    
    # Extract comments first
    clean_text, comments = extract_comments(text)
    
    # Parse the clean text
    parser = get_parser()
    tree = parser.parse(clean_text)
    
    # Create transformer
    class AdvancedParseTransformer(lark.Transformer):
        def __init__(self, comments, original_text):
            self.comments = comments
            self.original_text = original_text
            self.comment_map = organize_comments_by_definition(clean_text, comments)
            self.current_line = 0
        
        def lines(self, children):
            result = []
            
            # Add any standalone hint comments that appear before any definitions
            standalone_hints = []
            for comment in self.comments:
                if comment.is_hint:
                    # Check if this is a standalone comment (not associated with a definition)
                    lines_after_comment = self.original_text.split('\n')[comment.line + 1:]
                    has_following_def = any(re.match(r'\s*type\s+\w+', line) for line in lines_after_comment[:5])
                    
                    if not has_following_def:
                        standalone_hints.append(f"// {comment.get_hint_text()}")
            
            # Add standalone hints first
            result.extend(standalone_hints)
            
            # Process children (definitions with their associated comments)
            for child in children:
                if isToken(child, "COMMENT"):
                    # This is handled by the comment extraction
                    continue
                elif isinstance(child, Define):
                    # Check if this definition has associated hint comments
                    def_line = self._find_definition_line(child.name, clean_text)
                    if def_line in self.comment_map:
                        # Add hint comments before the definition
                        for comment in self.comment_map[def_line]:
                            if comment.is_hint:
                                result.append(f"// {comment.get_hint_text()}")
                    result.append(child)
                else:
                    result.append(child)
            
            return result
        
        def _find_definition_line(self, name, text):
            """Find the line number where a type definition appears."""
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if re.search(rf'\btype\s+{re.escape(name)}\b', line):
                    return i
            return -1

        def define(self, children):
            # Original define logic
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
    
    transformer = AdvancedParseTransformer(comments, text)
    return transformer.transform(tree)

if __name__ == "__main__":
    # Test the advanced parser
    test_cases = [
        "// Hint: This is a hint\ntype A = B;",
        "type A = B; // Hint: trailing hint",
        "type A = /* Hint: block hint */ B;",
        """type A = {
  // field comment
  field: string
};""",
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test {i+1} ---")
        print(f"Input: {repr(test_case)}")
        try:
            result = parse_advanced(test_case)
            formatted = '\n'.join([str(node.format() if hasattr(node, 'format') else node) for node in result])
            print(f"✅ Success: {formatted}")
        except Exception as e:
            print(f"❌ Failed: {e}")
            import traceback
            traceback.print_exc()
