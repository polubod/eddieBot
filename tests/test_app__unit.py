from src.app import build_prompt

def test_build_prompt_includes_system_context():
    prompt = build_prompt("Where is tutoring?")
    assert "freshman" in prompt.lower()

def test_build_prompt_includes_domain_context():
    prompt = build_prompt("Where is tutoring?")
    assert "campus resources" in prompt.lower()

def test_build_prompt_includes_user_input():
    prompt = build_prompt("Where is tutoring?")
    assert "where is tutoring" in prompt.lower()
