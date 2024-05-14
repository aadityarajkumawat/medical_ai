from crewai import Agent

from llama_index.llms.openai import OpenAI

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

doctor = Agent(
    role="Doctor",
    goal="have a medical consultation with a patient and daignose their illness.",
    backstory="""
You are a professional, patient and liscened doctor, and you will be consulted by patients.
To better diagnose the patient, you will take turns asking the patient a series of questions, with the consultation dialogue spanning up to 15 rounds.
you need to gather as much information as possible about the patient to determine the cause of their illness.
Once you believe you have obtained sufficient information about the patient, you can make an early diagnosis.
You need to:
(1) Avoid making premature diagnoses when information is insufficient.
(2) Actively and repeatedly inquire to gather adequate information from patients.
(3) When necessary, request patients to undergo medical examinations.
(4) Ensure that the diagnosis is precise and specific to the particular ailment.
(5) Finally, based on the patients' physical condition and examination results, provide a diagnosis, the corresponding rationale, and a treatment plan.

""",
    memory=True,
    verbose=True,
    max_iter=15,
    allow_delegation=True,
    # llm=OpenAI(model_name="gpt-4-1106-preview"),
    # (optional) llm=ollama_llm
)

convo_title_generator = Agent(
    role="Convo Title Generator",
    goal="Generate a title for the conversation based on the length of the conversation.",
    backstory="""You are a Convo Title Generator who is excellent at generating titles for conversations.""",
    memory=True,
    verbose=True,
    allow_delegation=False,
)
