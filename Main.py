from autogenstudio.teammanager import TeamManager
from autogen_agentchat.ui import Console
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from datetime import datetime

from autogen_ext.models.ollama import OllamaChatCompletionClient
client = OllamaChatCompletionClient(model="llama3.2",)

def user_calendar(date: int, event: str ):
    """
    The function Ask the user for the month, day, and year of an event to be saved, which will be stored in a list
    that will can be 
    """
    events = []
    event_month = int(input('Select Month: '))
    event_day = int(input('Select Day: '))
    event_year = 2025
    event_desc = input('Describe the Event to be saved: ')
    date = datetime(event_year, event_month, event_day)
    events = [event_desc, date]
    return events
