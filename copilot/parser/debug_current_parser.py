#!/usr/bin/env python3
"""
Debug script to understand current parser behavior with comments.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ts_type_filter import parse

def test_current_comment_behavior():
    """Test current comment parsing behavior to understand limitations."""
    
    test_cases = [
        # Current working cases
        ("// Simple comment\ntype A = B;", "Working: Top-level comment"),
        ("// Hint: This is a hint\ntype A = B;", "Working: Top-level hint comment"),
        
        # Cases that should fail with current parser
        ("type A = B; // inline comment", "Should fail: Inline comment"),
        ("type A = /* comment */ B;", "Should fail: Block comment"),
        ("type A = {\n  // field comment\n  field: string\n};", "Should fail: Comment in struct"),
        ("type A<\n  // param comment\n  T\n> = B;", "Should fail: Comment in type params"),
        ("type A = B |\n  // union comment\n  C;", "Should fail: Comment in union"),
        ("""/* Multi-line
             block comment */
type A = B;""", "Should fail: Multi-line block comment"),
    ]
    
    for source, description in test_cases:
        print(f"\n--- {description} ---")
        print(f"Source: {repr(source)}")
        try:
            result = parse(source)
            formatted = '\n'.join([node.format() for node in result])
            print(f"✅ Parsed successfully: {formatted}")
        except Exception as e:
            print(f"❌ Parse failed: {e}")

if __name__ == "__main__":
    test_current_comment_behavior()
