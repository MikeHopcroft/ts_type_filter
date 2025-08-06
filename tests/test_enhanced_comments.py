import pytest

from ts_type_filter import parse, Define, Literal

# Test cases specifically for enhanced comment support
enhanced_comment_test_cases = [
    # Block comments
    ("type A = /* simple block */ B;", "type A=B;", "block comment removal"),
    ("type A = /* Hint: block hint */ B;", "// block hint\ntype A=B;", "block hint comment"),
    
    # Inline line comments (should be removed except hints)
    ("type A = B; // trailing comment", "type A=B;", "trailing line comment removal"),
    ("type A = B; // Hint: trailing hint", "type A=B;\n// trailing hint", "trailing hint comment"),
    
    # Comments in complex structures (simplified - the parser removes comments inside structures)
    (
        """type Complex = {
  // field comment
  name: string
};""", 
        "type Complex={name:string};", 
        "comments in struct"
    ),
    
    # Mixed hint and non-hint comments
    (
        """// Hint: This type represents options
type Options = {
  // This field is required
  required: string
};""",
        "// This type represents options\ntype Options={required:string};",
        "mixed hint and regular comments"
    ),
    
    # Comments with arrays
    (
        """type ArrayType = 
  string[]; // array of strings""",
        "type ArrayType=string[];",
        "comments with array types"
    ),
    
    # Comments in LITERAL types
    (
        """type LiteralWithComment = 
  /* comment before */ 
  LITERAL<'value', ['alias'], true>;""",
        'type LiteralWithComment="value";',
        "comments with LITERAL types"
    ),
]

@pytest.mark.parametrize(
    "source, expected, test_name", enhanced_comment_test_cases, ids=[x[2] for x in enhanced_comment_test_cases]
)
def test_enhanced_comment_cases(source, expected, test_name):
    """Test enhanced comment support cases."""
    tree = parse(source)
    observed = '\n'.join([node.format() for node in tree])
    assert (
        observed == expected
    ), f"❌ Test Failed: {test_name} | Observed \n{observed}\nExpected \n{expected}"

def test_comment_hint_extraction():
    """Test that hint comments are properly extracted and associated with types."""
    source = "// Hint: This is a helpful hint\ntype TestType = string;"
    tree = parse(source)
    
    assert len(tree) == 2, "Should have both comment and type definition"
    
    # First item should be the hint comment
    assert tree[0] == "// This is a helpful hint"
    
    # Second item should be the type definition
    assert isinstance(tree[1], Define)
    assert tree[1].name == "TestType"

def test_block_hint_extraction():
    """Test that block hint comments are properly extracted."""
    source = "/* Hint: Block comment hint */\ntype TestType = string;"
    tree = parse(source)
    
    assert len(tree) == 2, "Should have both comment and type definition"
    
    # First item should be the hint comment
    assert tree[0] == "// Block comment hint"
    
    # Second item should be the type definition
    assert isinstance(tree[1], Define)
    assert tree[1].name == "TestType"

def test_multiple_hint_comments():
    """Test handling of multiple hint comments."""
    source = """// Hint: First hint
// Regular comment (should be ignored)
// Hint: Second hint
type TestType = string;"""
    
    tree = parse(source)
    
    # Should have two hints and one type definition
    assert len(tree) == 3
    assert tree[0] == "// First hint"
    assert tree[1] == "// Second hint"
    assert isinstance(tree[2], Define)

def test_complex_real_world_example():
    """Test a complex real-world example with various comment types."""
    source = """// Hint: Main cart type for the ordering system
type Cart = {
  id: string,
  items: Item[],
  total: number
};

// Hint: Individual item in a cart
type Item = {
  name: string,
  price: number,
  quantity: number
};"""
    
    tree = parse(source)
    observed = '\n'.join([node.format() for node in tree])
    expected = """// Main cart type for the ordering system
type Cart={id:string,items:Item[],total:number};
// Individual item in a cart
type Item={name:string,price:number,quantity:number};"""
    
    assert observed == expected, f"Complex example failed:\nObserved:\n{observed}\nExpected:\n{expected}"

def test_backwards_compatibility():
    """Ensure the enhanced parser maintains backwards compatibility."""
    # These are test cases from the original test suite that should still work
    backwards_compat_cases = [
        ("type a='Jalapeños';", 'type a="Jalapeños";'),
        ("type a=never;", "type a=never;"),
        ("type a<A,B,C>=never;", "type a<A,B,C>=never;"),
        ("type a<A,B,C>={a:A, b:B, c:C};", "type a<A,B,C>={a:A,b:B,c:C};"),
        ("type a=123;", 'type a=123;'),
        ("type D={a:1,b:'text'};", 'type D={a:1,b:"text"};'),
        ("type A=B[];", 'type A=B[];'),
        ("type A=B|C;", 'type A=B|C;'),
    ]
    
    for source, expected in backwards_compat_cases:
        tree = parse(source)
        observed = '\n'.join([node.format() for node in tree])
        assert observed == expected, f"Backwards compatibility failed for: {source}"
