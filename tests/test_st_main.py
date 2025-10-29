import re


def extract_think_body(full_response: str) -> tuple[str, str]:
    """Copy of the function from st_main.py for testing purposes"""
    match = re.search(r'<think>(.*?)</think>(.*)', full_response, re.DOTALL)
    if match:
        return match.group(1), match.group(2)
    return "", full_response


def test_extract_think_body_with_think_tag():
    """Test extraction when <think> tag is present"""
    response = "<think>thinking process here</think>actual response"
    think, body = extract_think_body(response)
    assert think == "thinking process here"
    assert body == "actual response"


def test_extract_think_body_with_multiline_think():
    """Test extraction with multiline content"""
    response = "<think>line1\nline2\nline3</think>final answer"
    think, body = extract_think_body(response)
    assert think == "line1\nline2\nline3"
    assert body == "final answer"


def test_extract_think_body_without_think_tag():
    """Test extraction when no <think> tag is present"""
    response = "just a regular response"
    think, body = extract_think_body(response)
    assert think == ""
    assert body == "just a regular response"


def test_extract_think_body_empty_string():
    """Test extraction with empty string"""
    response = ""
    think, body = extract_think_body(response)
    assert think == ""
    assert body == ""


if __name__ == "__main__":
    test_extract_think_body_with_think_tag()
    test_extract_think_body_with_multiline_think()
    test_extract_think_body_without_think_tag()
    test_extract_think_body_empty_string()
    print("All tests passed!")
