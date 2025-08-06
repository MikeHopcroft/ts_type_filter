#!/usr/bin/env python3
"""Debug test 3 specifically."""

import re

def debug_test3():
    text = "type A = /* Hint: block hint */ B;"
    print(f"Input: {repr(text)}")
    
    result_lines = []
    lines = text.split('\n')
    print(f"Lines: {lines}")
    
    for line_num, line in enumerate(lines):
        print(f"\nProcessing line {line_num}: {repr(line)}")
        current_line = line
        
        # Step 1: Handle block comments on this line
        iteration = 0
        while True:
            iteration += 1
            print(f"  Block comment iteration {iteration}, current_line: {repr(current_line)}")
            block_match = re.search(r'/\*[\s\S]*?\*/', current_line)
            if not block_match:
                print(f"  No more block comments found")
                break
            
            comment_content = block_match.group(0)
            before_comment = current_line[:block_match.start()]
            after_comment = current_line[block_match.end():]
            
            print(f"  Found block comment: {repr(comment_content)}")
            print(f"  Before: {repr(before_comment)}")
            print(f"  After: {repr(after_comment)}")
            
            if comment_content.startswith('/* Hint: '):
                # Convert block hint to line hint
                hint_content = comment_content[9:-2].strip()
                print(f"  Hint content: {repr(hint_content)}")
                
                # If there's content before the comment, add it
                if before_comment.strip():
                    result_lines.append(before_comment.rstrip())
                    print(f"  Added before content: {repr(before_comment.rstrip())}")
                
                # Add the hint comment
                hint_line = f'// Hint: {hint_content}'
                result_lines.append(hint_line)
                print(f"  Added hint line: {repr(hint_line)}")
                
                # Continue processing the rest of the line
                current_line = after_comment
                print(f"  Continuing with: {repr(current_line)}")
            else:
                # Remove non-hint block comment, replace with space
                current_line = before_comment + ' ' + after_comment
                print(f"  Removed non-hint, continuing with: {repr(current_line)}")
        
        print(f"  After block processing, current_line: {repr(current_line)}")
        
        # Step 2: Handle line comments
        line_comment_match = re.search(r'//.*$', current_line)
        if line_comment_match:
            print(f"  Found line comment: {repr(line_comment_match.group(0))}")
            comment_text = line_comment_match.group(0)
            line_before_comment = current_line[:line_comment_match.start()].rstrip()
            
            if comment_text.startswith('// Hint: '):
                # This is a hint comment
                if line_before_comment.strip():
                    # There's TypeScript code before the comment - split them
                    result_lines.append(line_before_comment)
                    result_lines.append(comment_text)
                    print(f"  Split hint comment: {repr(line_before_comment)} and {repr(comment_text)}")
                else:
                    # Hint comment is on its own line
                    result_lines.append(comment_text)
                    print(f"  Hint on own line: {repr(comment_text)}")
            else:
                # Non-hint comment - remove it
                if line_before_comment.strip():
                    result_lines.append(line_before_comment)
                    print(f"  Removed non-hint comment, kept: {repr(line_before_comment)}")
                # else: empty line, skip it
        else:
            # No line comment, add the line if it has content
            if current_line.strip():
                result_lines.append(current_line)
                print(f"  No line comment, added: {repr(current_line)}")
    
    print(f"\nFinal result_lines: {result_lines}")
    result = '\n'.join(result_lines)
    print(f"Final result: {repr(result)}")
    return result

debug_test3()
