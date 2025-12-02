from autogenstudio.teammanager import TeamManager
from autogen_agentchat.ui import Console
from autogen_agentchat.agents import AssistantAgent, ToolAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from datetime import datetime

from autogen_ext.models.ollama import OllamaChatCompletionClient
client = OllamaChatCompletionClient(model="llama3.2",)

events = []

def user_calendar():
    """
    The function Ask the user for the month, day, and year of an event to be saved, which will be stored in a list
    that will can be 
    """
    event_month = int(input("Select Month : "))
    event_day = int(input("Select Day : "))
    event_year = 2025
    event_desc = input("Describe the event to be saved: ")
    date = datetime(event_year, event_month, event_day)
    event = {
        "description": event_desc,
        "date": date
    }
    events.append(event)
    return event


tool_agent = ToolAgent(
    name="tool_agent",
    description="Simple Calendar Tracking tool agent for demo purpose.",
    functions=[user_calendar],
)


coding_agent = AssistantAgent(
    name="coding_agent",
    model_client=client,
    system_message=(
        "You generate UML diagrams (use case, class, sequence) in plantUML "
        "and generate runnable Python code for sequence diagrams."
    ),
)

observer_agent = AssistantAgent(
    name="observer_agent",
    model_client=client,
    system_message=(
        "You are a reflection agent. Evaluate the generated diagrams and code, "
        "identify problems, and propose improvements. Output corrections clearly."
    ),
)

manager_agent = AssistantAgent(
    name="manager_agent",
    model_client=client,
    system_message=(
        "You coordinate all agents. Use tool_agent only for numeric computation. "
        "Use coding_agent for all diagram/code generation. "
        "Send all outputs to observer_agent for evaluation."
    ),
)

graph = (
    DiGraphBuilder()
    .add_agent(manager_agent)
    .add_agent(tool_agent)
    .add_agent(coding_agent)
    .add_agent(observer_agent)
    .add_edge("manager_agent", "coding_agent")
    .add_edge("coding_agent", "observer_agent")
    .add_edge("manager_agent", "tool_agent")
    .build()
)

team = TeamManager(
    team_graph=graph,
    flow=GraphFlow.RECURSIVE,
    max_turns = 15,
)

application_summary = """
Application Summary
"""

console = Console()

result = team.run(
    task=(
        f"Here is a software application description:\n\n"
        f"{application_summary}\n\n"
        "Produce the following:\n"
        "1. UML Use Case Diagram (plantUML)\n"
        "2. Use Case Specifications (JSON)\n"
        "3. Class Diagram (plantUML)\n"
        "4. Sequence Diagrams (plantUML)\n"
        "5. Python code implementing each sequence diagram\n"
        "6. Observer agent must evaluate all outputs and suggest improvements"
    ),
    ui=console,
)

print("Output: \n")
print(result)