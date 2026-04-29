"""
agents/_base.py
Shared model factory and agent builder for skill-backed agents.
Supports per-agent model configuration with MiniMax prompt caching.
"""

from agno.agent import Agent
from skills_loader import load_skills, get_skill_content
from mail_agent.model_factory import build_model, get_model_config

# ── skills registry (loaded once) ─────────────────────────────────────────────
SKILLS = load_skills()


def build_agent(skill_name: str, agent_type: str = "parser") -> Agent:
    """
    Return an Agent wired to the named skill with configured model.

    Args:
        skill_name: Name of the skill to load (e.g., "email-parser")
        agent_type: Type of agent for model config ("parser", "triage", "reply")

    Returns:
        Configured Agno Agent instance
    """
    skill = SKILLS[skill_name]
    config = get_model_config(agent_type)

    model = build_model(
        model_id=config["model_id"],
        enable_caching=config["enable_caching"],
        fallback_models=config["fallback_models"],
    )

    return Agent(
        name=skill_name,
        model=model,
        description=skill["description"],
        instructions=[
            f"You are executing the '{skill_name}' skill. Follow these instructions exactly:",
            get_skill_content(SKILLS, skill_name),
            "CRITICAL: Return ONLY raw JSON. No markdown fences, no extra text.",
        ],
        markdown=False,
    )