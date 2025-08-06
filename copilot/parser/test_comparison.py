#!/usr/bin/env python3
"""
Comprehensive test to compare original parser vs enhanced parser behavior.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ts_type_filter import parse as parse_original
from enhanced_parser import parse_enhanced

def compare_parsers():
    """Compare original and enhanced parser behaviors."""
    
    # Test cases that should work the same in both parsers
    compatible_cases = [
        ("// Simple comment\ntype A = B;", "Compatible: Top-level comment"),
        ("// Hint: This is a hint\ntype A = B;", "Compatible: Top-level hint comment"),
        ("type A = 123;", "Compatible: Number literal"),
        ("type A = 'hello';", "Compatible: String literal"),
        ("type A = B[];", "Compatible: Array type"),
        ("type A = B | C;", "Compatible: Union type"),
        ("type A = { field: string };", "Compatible: Struct type"),
        ("type A<T> = B<T>;", "Compatible: Generic type"),
        ("type A<T extends U> = B<T>;", "Compatible: Constrained generic"),
        ("""type A = LITERAL<'test', ['alias'], true>;""", "Compatible: LITERAL type"),
    ]
    
    # Test cases that should fail in original but work in enhanced
    enhanced_only_cases = [
        ("type A = /* comment */ B;", "Enhanced: Block comment"),
        ("type A = {\n  // field comment\n  field: string\n};", "Enhanced: Comment in struct"),
        ("type A<\n  // param comment\n  T\n> = B;", "Enhanced: Comment in type params"),
        ("type A = B |\n  // union comment\n  C;", "Enhanced: Comment in union"),
        ("""/* Multi-line
             block comment */
type A = B;""", "Enhanced: Multi-line block comment"),
        ("/* Hint: Block hint */\ntype A = B;", "Enhanced: Block hint comment"),
        ("type A = B; // trailing comment", "Enhanced: Trailing comment"),
        ("""type Complex = {
  // This is a field comment
  name: string,
  /* This is another field comment */
  age: number
};""", "Enhanced: Multiple comment types in struct"),
    ]
    
    print("=== COMPATIBLE CASES (should work in both parsers) ===")
    for source, description in compatible_cases:
        print(f"\n--- {description} ---")
        print(f"Source: {repr(source)}")
        
        # Test original parser
        try:
            original_result = parse_original(source)
            original_formatted = '\n'.join([node.format() for node in original_result])
            print(f"✅ Original: {original_formatted}")
        except Exception as e:
            print(f"❌ Original failed: {e}")
            original_formatted = None
        
        # Test enhanced parser
        try:
            enhanced_result = parse_enhanced(source)
            enhanced_formatted = '\n'.join([node.format() for node in enhanced_result])
            print(f"✅ Enhanced: {enhanced_formatted}")
        except Exception as e:
            print(f"❌ Enhanced failed: {e}")
            enhanced_formatted = None
        
        # Compare results
        if original_formatted and enhanced_formatted:
            if original_formatted == enhanced_formatted:
                print("🎯 Results match!")
            else:
                print("⚠️  Results differ!")
    
    print("\n\n=== ENHANCED-ONLY CASES (should fail in original, work in enhanced) ===")
    for source, description in enhanced_only_cases:
        print(f"\n--- {description} ---")
        print(f"Source: {repr(source)}")
        
        # Test original parser
        try:
            original_result = parse_original(source)
            original_formatted = '\n'.join([node.format() for node in original_result])
            print(f"😲 Original unexpectedly worked: {original_formatted}")
        except Exception as e:
            print(f"✅ Original failed as expected: {str(e)[:100]}...")
        
        # Test enhanced parser
        try:
            enhanced_result = parse_enhanced(source)
            enhanced_formatted = '\n'.join([node.format() for node in enhanced_result])
            print(f"✅ Enhanced works: {enhanced_formatted}")
        except Exception as e:
            print(f"❌ Enhanced failed unexpectedly: {e}")

if __name__ == "__main__":
    compare_parsers()
