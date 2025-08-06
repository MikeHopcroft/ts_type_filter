#!/usr/bin/env python3
"""
Script to apply the enhanced parser to the main codebase.
This will backup the original parser and replace it with the enhanced version.
"""

import sys
import os
import shutil
from datetime import datetime

def backup_and_replace_parser():
    """Backup original parser and replace with enhanced version."""
    
    original_parser_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ts_type_filter', 'parser.py')
    enhanced_parser_path = os.path.join(os.path.dirname(__file__), 'enhanced_parser.py')
    backup_path = os.path.join(os.path.dirname(__file__), f'parser_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py')
    
    # Read the original parser
    with open(original_parser_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Create backup
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(original_content)
    print(f"✅ Original parser backed up to: {backup_path}")
    
    # Read the enhanced parser implementation parts
    with open(enhanced_parser_path, 'r', encoding='utf-8') as f:
        enhanced_content = f.read()
    
    # Extract the preprocessing function and updated parse logic from enhanced parser
    import re
    
    # Extract the preprocess_text function
    preprocess_match = re.search(r'def preprocess_text\(text\):.*?(?=\ndef|\nclass|\n# |$)', enhanced_content, re.DOTALL)
    if not preprocess_match:
        raise ValueError("Could not find preprocess_text function in enhanced parser")
    preprocess_function = preprocess_match.group(0)
    
    # We need to add the regex import
    regex_import = "import re\n"
    
    # Create the new parser content
    new_parser_content = original_content
    
    # Add regex import after ast import
    new_parser_content = new_parser_content.replace(
        "import ast",
        "import ast\nimport re"
    )
    
    # Add the preprocessing function before the existing get_parser function
    insertion_point = new_parser_content.find("# Lazy initialization of parser")
    if insertion_point == -1:
        insertion_point = new_parser_content.find("_parser = None")
    
    new_parser_content = (
        new_parser_content[:insertion_point] + 
        preprocess_function + "\n\n" +
        new_parser_content[insertion_point:]
    )
    
    # Update the parse function to use preprocessing
    old_parse_function = re.search(r'def parse\(text\):.*?(?=\ndef|\n\n[a-zA-Z]|\Z)', new_parser_content, re.DOTALL)
    if not old_parse_function:
        raise ValueError("Could not find parse function in original parser")
    
    # Replace the parse function with enhanced version
    enhanced_parse = '''def parse(text):
    import lark
    
    # Preprocess to handle comments flexibly
    clean_text = preprocess_text(text)
    
    # Create Transformer class dynamically to avoid import-time dependency
    # Transformer class converts the parse tree into AST nodes.
    class ParseTransformer(lark.Transformer):
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

        def pair(self, items):
            return (items[0].value, items[1])

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
    tree = parser.parse(clean_text)
    return ParseTransformer().transform(tree)
'''
    
    new_parser_content = new_parser_content.replace(old_parse_function.group(0), enhanced_parse)
    
    # Write the new parser
    with open(original_parser_path, 'w', encoding='utf-8') as f:
        f.write(new_parser_content)
    
    print(f"✅ Enhanced parser applied to: {original_parser_path}")
    print("🎯 The parser now supports:")
    print("   - /* */ block comments anywhere they're legal in TypeScript")
    print("   - // line comments anywhere they're legal in TypeScript") 
    print("   - Comments between lines of multi-line type declarations")
    print("   - Comments to the right of declaration text")
    print("   - Preservation of 'Hint:' prefix behavior")

if __name__ == "__main__":
    backup_and_replace_parser()
