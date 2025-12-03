import asyncio
from datetime import datetime

from autogen_agentchat.ui import Console
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_ext.models.ollama import OllamaChatCompletionClient

# -------------------------
# Model client
# -------------------------
client = OllamaChatCompletionClient(model="llama3.2")

# In-memory event store
events: list[dict] = []


# -------------------------
# Tool function
# -------------------------
def user_calendar(
    event_month: int,
    event_day: int,
    event_year: int,
    event_desc: str,
) -> dict:
    """
    Create and store a calendar event.

    Args:
        event_month: Month as an integer (1-12).
        event_day: Day as an integer (1-31).
        event_year: Full year, e.g., 2025.
        event_desc: Short text description of the event.

    Returns:
        A dictionary with the stored event (JSON-serializable).
    """
    date = datetime(event_year, event_month, event_day)
    event = {
        "description": event_desc,
        "date": date.isoformat(),  # JSON-friendly
    }
    events.append(event)
    return event


# -------------------------
# Agents
# -------------------------

# Agent that owns the tool
tool_agent = AssistantAgent(
    name="tool_agent",
    model_client=client,
    system_message=(
        "You are a calendar tool agent. "
        "Use the `user_calendar` tool to create and store events. "
        "Always provide these arguments explicitly: "
        "event_month (1-12), event_day (1-31), event_year (e.g., 2025), "
        "and event_desc (string description). "
        "Return the tool result to the requesting agent."
    ),
    tools=[user_calendar],
)

# Coding agent: diagrams + code
coding_agent = AssistantAgent(
    name="coding_agent",
    model_client=client,
    system_message=(
        "You generate UML diagrams (use case, class, sequence) in PlantUML "
        "and generate runnable Python code for sequence diagrams. "
        "Use clear, syntactically correct PlantUML, and runnable Python."
    ),
)

# Observer agent: reflection/evaluation
observer_agent = AssistantAgent(
    name="observer_agent",
    model_client=client,
    system_message=(
        "You are a reflection agent. Evaluate the generated diagrams and code, "
        "identify problems, and propose improvements. "
        "Clearly list issues and provide corrected versions when possible."
    ),
)

# Manager agent: orchestrator
manager_agent = AssistantAgent(
    name="manager_agent",
    model_client=client,
    system_message=(
        "You coordinate all agents.\n\n"
        "- Use coding_agent for all UML diagram and Python code generation.\n"
        "- Use tool_agent ONLY when you need to create or store calendar events, "
        "by calling the `user_calendar` tool with arguments:\n"
        "  event_month, event_day, event_year, event_desc.\n"
        "- After coding_agent produces any output, send it to observer_agent "
        "for evaluation and incorporate the feedback.\n"
        "- Do not ask the human for input; instead infer any missing details "
        "or make reasonable assumptions.\n"
    ),
)

# -------------------------
# Build the GraphFlow
# -------------------------

builder = DiGraphBuilder()
builder.add_node(manager_agent).add_node(tool_agent).add_node(coding_agent).add_node(observer_agent)

# manager -> coding
builder.add_edge(manager_agent, coding_agent)
# coding -> observer
builder.add_edge(coding_agent, observer_agent)
# manager -> tool
builder.add_edge(manager_agent, tool_agent)

graph = builder.build()

flow = GraphFlow(
    participants=builder.get_participants(),
    graph=graph,
)

# -------------------------
# Task + runner
# -------------------------

application_summary = """
The proposed system is a Personal Calendar Event Manager that allows users to store simple date-based reminders.
Users can input an event by selecting a month and day, while the system handles year assignment automatically.
Each event consists of a description and a Date, which the system structures into an event object.
All events are stored in a centralized in-memory list that acts as a basic event repository.
The system ensures uniform formatting of stored events by converting raw user input into a proper date object.
Users can enter multiple events during a session, and each event is appended to the event collection.
The application focuses on simplicity, requiring minimal fields while still enabling meaningful reminders.
The system can later be extended to support listing, sorting, filtering, or exporting events.
This application demonstrates fundamental concepts of data collection, simple scheduling, and event management.
"""


async def main() -> None:
    task_text = (
        f"Here is a software application description:\n\n"
        f"{application_summary}\n\n"
        "Produce the following:\n"
        "1. UML Use Case Diagram with 4-5 use cases (PlantUML)\n"
        "2. Use Case Specifications (JSON)\n"
        "3. Class Diagram (PlantUML)\n"
        "4. Sequence Diagrams (PlantUML)\n"
        "5. Python code implementing each sequence diagram\n"
        "6. The observer_agent must evaluate all outputs and suggest improvements"
    )

    # Correct usage for your version:
    # Console is an async helper that takes the run_stream generator and prints it.
    result = await Console(flow.run_stream(task=task_text))

    print("\n==== Final TaskResult ====\n")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
