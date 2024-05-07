from crewai import Agent

import os
from dotenv import load_dotenv

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


decider = Agent(
    role="decider",
    goal="Either accept or reject discrepancies, by agreeing with the suggestion or disagreeing and responding with some reasoning.",
    backstory="""You are excellent at decerning discrepancies suggested by others and providing reasoning for your decisions.""",
    memory=True,
    verbose=True,
    allow_delegation=False,
)

researcher = Agent(
    role="Researcher",
    goal="Read the summary and point out any discrepancies.",
    backstory="""You are a Medical Researcher who is excellent at finding errors in medical summaries.""",
    memory=True,
    verbose=True,
    allow_delegation=False,
)

editor = Agent(
    role="Medical Document Editor",
    goal="Generate a corrected version of the summary based on points mentioned in the scratchpad.",
    backstory="""You are a Medical Document Editor who is excellent at correcting medical summaries.""",
    memory=True,
    verbose=True,
    allow_delegation=False,
)

summary_writer = Agent(
    role="Summary Writer",
    goal="Write a summary of the medical encounter between the doctor and the patient in 6 sections.",
    backstory="""You are a Medical Summary Writer who is excellent at writing summaries of medical encounters.""",
    memory=True,
    verbose=True,
    allow_delegation=False,
)

corrupter = Agent(
    role="Corrupter",
    goal="Corrupt the summary slightly.",
    backstory="""You are a Corrupter who is excellent at corrupting summaries.""",
    memory=True,
    verbose=True,
    allow_delegation=False,
)

chief_complaint_finder = Agent(
    role="Chief Complaint Finder",
    goal="Find the chief complaint in the chat.",
    backstory="""You are a Chief Complaint Finder who is excellent at finding chief complaints.""",
    memory=True,
    verbose=True,
    allow_delegation=False,
)

physician = Agent(
    role="Physician",
    goal="Provide a medical diagnosis based on the chat.",
    backstory="""You are a Physician who is excellent at providing medical diagnoses.""",
    memory=True,
    verbose=True,
    allow_delegation=False,
)

editor_careplan = Agent(
    role="Medical Document Editor",
    goal="Generate a corrected version of the care plan based on points mentioned in the scratchpad.",
    backstory="""You are a Medical Document Editor who is excellent at correcting medical care plans.""",
    memory=True,
    verbose=True,
    allow_delegation=False,
)
