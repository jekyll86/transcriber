"""Tests for LLM prompts and summary level constructions."""

from llm.prompts import get_polish_prompt, get_summary_prompt


def test_get_polish_prompt():
    transcript = "Um, like, hello everyone. We, uh, started the project."
    sys_prompt, user_prompt = get_polish_prompt(transcript)
    assert "verbatim proofreader" in sys_prompt
    assert transcript in user_prompt


def test_get_summary_prompt_levels():
    transcript = "The committee decided to allocate $50,000 to the software refactoring initiative."

    # TL;DR
    sys_tldr, user_tldr = get_summary_prompt(transcript, level="tldr")
    assert "TL;DR" in sys_tldr
    assert transcript in user_tldr

    # Bullet Points
    sys_bullets, user_bullets = get_summary_prompt(transcript, level="bullets")
    assert "bullet points" in sys_bullets

    # Detailed
    sys_detailed, user_detailed = get_summary_prompt(transcript, level="detailed")
    assert "Overview" in sys_detailed
    assert "Conclusion" in sys_detailed

    # Action Items
    sys_actions, user_actions = get_summary_prompt(transcript, level="action_items")
    assert "checklist" in sys_actions

    # Custom
    sys_custom, user_custom = get_summary_prompt(transcript, level="custom", custom_instruction="Translate to French")
    assert "Translate to French" in user_custom
