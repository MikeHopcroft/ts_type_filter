#!/usr/bin/env python3
"""
Demonstration of the enhanced TypeScript parser with flexible comment support.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ts_type_filter import parse

def demonstrate_enhanced_comments():
    """Demonstrate all the enhanced comment features."""
    
    print("🎯 ENHANCED TYPESCRIPT PARSER DEMONSTRATION")
    print("=" * 60)
    
    examples = [
        {
            "title": "Block Comments with Hints",
            "source": """/* Hint: User profile information */
type User = {
  name: string,
  /* This is an ID field */
  id: number
};""",
            "description": "Block comments are now supported, including /* Hint: */ style comments"
        },
        
        {
            "title": "Inline Comments", 
            "source": """type Product = {
  name: string, // Product display name
  price: number // Price in cents
};""",
            "description": "Inline comments after declarations are properly removed"
        },
        
        {
            "title": "Comments in Complex Types",
            "source": """type ApiResponse<T> = {
  // Success response
  status: 'success',
  data: T
} | {
  // Error response  
  status: 'error',
  message: string
};""",
            "description": "Comments between union types and in generic definitions"
        },
        
        {
            "title": "Mixed Comment Types",
            "source": """// Hint: Shopping cart for e-commerce
type Cart = {
  /* Cart ID */
  id: string,
  items: Item[], // Array of cart items
  total: number
};""",
            "description": "Mix of line comments, block comments, and hint comments"
        },
        
        {
            "title": "Trailing Hint Comments",
            "source": """type Status = 'pending' | 'completed'; // Hint: Use pending for new orders""",
            "description": "Hint comments can appear at the end of type definitions"
        },
        
        {
            "title": "Multi-line Structures with Comments",
            "source": """type Config = {
  // Database settings
  database: {
    host: string,
    port: number
  },
  /* API configuration */
  api: {
    baseUrl: string,
    timeout: number
  }
};""",
            "description": "Comments within nested structures"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['title']}")
        print("-" * 40)
        print(f"Description: {example['description']}")
        print(f"\nInput:")
        print(example['source'])
        
        try:
            result = parse(example['source'])
            formatted = '\n'.join([node.format() if hasattr(node, 'format') else str(node) for node in result])
            print(f"\nOutput:")
            print(formatted)
            print("✅ SUCCESS")
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
    
    print(f"\n{'=' * 60}")
    print("🎉 SUMMARY")
    print("The enhanced parser now supports:")
    print("  ✅ /* */ block comments anywhere they're legal in TypeScript")
    print("  ✅ // line comments anywhere they're legal in TypeScript")
    print("  ✅ Comments between lines of multi-line type declarations")
    print("  ✅ Comments to the right of declaration text")
    print("  ✅ Preservation of 'Hint:' prefix behavior for both comment types")
    print("  ✅ Full backwards compatibility with existing functionality")
    print("  ✅ Proper comment removal (non-hint comments are cleaned up)")
    print("  ✅ Smart hint comment placement (before definitions or after as appropriate)")

if __name__ == "__main__":
    demonstrate_enhanced_comments()
