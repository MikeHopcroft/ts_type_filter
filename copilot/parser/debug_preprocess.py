#!/usr/bin/env python3
"""Debug the preprocessing step."""

import re

def debug_preprocess_for_enhanced_comments(text):
    """Debug version with print statements."""
    print(f"Input text: {repr(text)}")
    
    # Step 1: Convert block comments to line comments
    def replace_block_comment(match):
        comment_content = match.group(0)
        print(f"Found block comment: {repr(comment_content)}")
        if comment_content.startswith('/* Hint: '):
            # Convert block hint to line hint
            hint_content = comment_content[9:-2].strip()
            result = f'\n// Hint: {hint_content}\n'
            print(f"Converted to: {repr(result)}")
            return result
        else:
            # Remove non-hint block comments but preserve spacing
            # Count newlines in the comment to preserve line structure
            newline_count = comment_content.count('\n')
            if newline_count > 0:
                result = '\n' * newline_count
            else:
                result = ' '
            print(f"Removed, replaced with: {repr(result)}")
            return result
    
    # Process block comments
    after_blocks = re.sub(r'/\*[\s\S]*?\*/', replace_block_comment, text)
    print(f"After block processing: {repr(after_blocks)}")
    
    # Step 2: Handle line comments - move trailing hint comments to their own lines
    lines = after_blocks.split('\n')
    print(f"Lines: {lines}")
    result_lines = []
    
    for i, line in enumerate(lines):
        print(f"Processing line {i}: {repr(line)}")
        # Check for line comments
        comment_match = re.search(r'//.*$', line)
        if comment_match:
            comment_text = comment_match.group(0)
            line_before_comment = line[:comment_match.start()].rstrip()
            print(f"  Found comment: {repr(comment_text)}")
            print(f"  Line before: {repr(line_before_comment)}")
            
            if comment_text.startswith('// Hint: '):
                # This is a hint comment
                if line_before_comment.strip():
                    # There's TypeScript code before the comment - split them
                    result_lines.append(line_before_comment)
                    result_lines.append(comment_text)
                    print(f"  Split into: {repr(line_before_comment)} and {repr(comment_text)}")
                else:
                    # Hint comment is on its own line
                    result_lines.append(comment_text)
                    print(f"  Kept hint on own line: {repr(comment_text)}")
            else:
                # Non-hint comment - remove it
                if line_before_comment.strip():
                    result_lines.append(line_before_comment)
                    print(f"  Removed comment, kept: {repr(line_before_comment)}")
                else:
                    result_lines.append('')
                    print(f"  Removed comment, empty line")
        else:
            # No comment on this line
            result_lines.append(line)
            print(f"  No comment, kept: {repr(line)}")
    
    print(f"Result lines: {result_lines}")
    
    # Clean up extra empty lines
    cleaned_lines = []
    for line in result_lines:
        if line.strip() or (cleaned_lines and cleaned_lines[-1].strip()):
            cleaned_lines.append(line)
    
    print(f"Cleaned lines: {cleaned_lines}")
    result = '\n'.join(cleaned_lines)
    print(f"Final result: {repr(result)}")
    return result

# Test the problematic case
test_input = "type A = /* Hint: block hint */ B;"
print("=== DEBUGGING ===")
debug_preprocess_for_enhanced_comments(test_input)
