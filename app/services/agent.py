"""Chat agent using Claude SDK with tools for vehicle maintenance analysis."""

import anthropic
from sqlalchemy.orm import Session

from app.config import settings
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import TOOL_DEFINITIONS, execute_tool
from app.models import Vehicle

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


def _build_context(db: Session, vehicle_id: int | None) -> str:
    """Build context about available vehicles for the system prompt."""
    vehicles = db.query(Vehicle).all()
    if not vehicles:
        return "\n\nAucun vehicule enregistre dans la base."

    lines = ["\n\nVehicules disponibles:"]
    for v in vehicles:
        marker = " (SELECTIONNE)" if v.id == vehicle_id else ""
        lines.append(f"  - ID {v.id}: {v.name} — {v.brand} {v.model} ({v.year or '?'}){marker}")

    if vehicle_id:
        lines.append(f"\nLa conversation porte sur le vehicule ID {vehicle_id}. Utilise cet ID dans tes appels d'outils.")
    else:
        lines.append("\nAucun vehicule selectionne. Demande a l'utilisateur quel vehicule l'interesse si necessaire.")

    return "\n".join(lines)


def chat(
    messages: list[dict],
    vehicle_id: int | None,
    db: Session,
) -> str:
    """Run a chat turn with the agent. Handles tool use loop.

    Args:
        messages: Conversation history [{"role": "user"/"assistant", "content": "..."}]
        vehicle_id: Currently selected vehicle ID (or None)
        db: Database session

    Returns:
        Assistant's text response
    """
    system = SYSTEM_PROMPT + _build_context(db, vehicle_id)

    api_messages = []
    for msg in messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    # Agentic loop: keep calling until we get a text response (max 10 rounds)
    for _ in range(10):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system,
            tools=TOOL_DEFINITIONS,
            messages=api_messages,
        )

        # Collect all content blocks
        text_parts = []
        tool_uses = []
        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_uses.append(block)

        # If no tool calls, return the text
        if not tool_uses:
            return "\n".join(text_parts)

        # Add assistant response to messages (with tool use blocks)
        api_messages.append({"role": "assistant", "content": response.content})

        # Execute tools and add results
        tool_results = []
        for tu in tool_uses:
            result = execute_tool(tu.name, tu.input, db)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu.id,
                "content": result,
            })

        api_messages.append({"role": "user", "content": tool_results})

    return "Desolé, je n'ai pas pu terminer l'analyse. Veuillez reformuler votre question."
