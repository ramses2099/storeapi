from src.app import index

def test_index():
    assert index() == "<p>Hello, World!</p>"
