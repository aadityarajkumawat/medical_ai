from crewai import Agent, Task, Crew, Process
import os
from dotenv import load_dotenv

load_dotenv()

from langchain.agents import load_tools

human_tools = load_tools(["human"])

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# You can choose to use a local model through Ollama for example. See ./docs/how-to/llm-connections.md for more information.
# from langchain_community.llms import Ollama
# ollama_llm = Ollama(model="openhermes")

# Install duckduckgo-search for this example:
# !pip install -U duckduckgo-search

# from langchain_community.tools import DuckDuckGoSearchRun
# search_tool = DuckDuckGoSearchRun()

# Define your agents with roles and goals
decider = Agent(
    role="decider",
    goal="you have access to the full medical conversation between the patient and the physician, either accept or reject discrepancies, by agreeing with the suggestion or disagreeing and responding with some reasoning.",
    backstory="""
You ( Person A ) are a very good summary writer for medical dialogues between
physicians and patients.

""",
    memory=True,
    verbose=True,
    allow_delegation=False,
    # (optional) llm=ollama_llm
)

researcher = Agent(
    role="researcher",
    goal="you have access to the full medical conversation between the patient and the physician, read the summary and point out any discrepancies.",
    backstory="""
---
You ( Person B ) are a very good summary editer for medical dialogues between
physicians and patients .

This is the medical dialogue you will be referencing for a { age } and { sex } patient :
- Medical Dialogue -
{ chat }
- Medical Dialogue -

You are discussing the summary that another summary writer ( Person A ) wrote for this
dialogue one section at a time .

You will be giving Person A points for correction based on any mistakes /
discrepancies you see between the dialogue and summary one section at a time .
Person A will add the points of correction that they agree on to a scratchpad to
later make edits .

However , you will only go through the Pertinent Positives , Pertinent Negatives ,
Pertinent Unknowns , and Medical History sections .

This is Person A's original version of the summary :
- Person A's Original Summary -
{ summary }
- Person A's Original Summary -

Here is Person A's current scratchpad of corrections to make to the summary :
- Correction Scratchpad -
{ scratchpad }
- Correction Scratchpad -

Go through each section of the summary one at a time and point out any text that
does not have a grounding in the dialogue . It must be possible to directly tie
any span of the summary to the dialogue .

Make sure to make accurate , useful suggestions for corrections .

Person A may not initially agree with you , but if you are confident there is an
error do your best to convince Person A of the mistake .

Once you have gone through each section and have confirmed each section with Person
A , and you are satisfied with all of the corrections added to the scratchpad and
/ or all of Person A's reasoning to reject additional corrections , output the tag
"[ STOP ]".

This is the summary discussion with Person A so far :
- Summary Discussion -
{ discussion }
- Summary Discussion -

Question : What do you say next ? Respond to Person A in the tag [ RESPONSE : " <
your_response_here >"]. If you are done correcting and are satisfied , output the
"[ STOP ]" tag .
Answer :

""",
    memory=True,
    verbose=True,
    max_iter=15,
    allow_delegation=False,
)

# Create tasks for your agents
task1 = Task(
    description="""
----
Below is a medical encounter between an 21
and Female patient and a doctor done over chat.
Chief Complaint : "Sinus Infection".
----
Medical Encounter
----
Patient: I have a sinus infection and need something to knock it out.
Doctor: Hi melissa thank you for starting a visit. I am so sorry to hear about your sinus infection. How long have you had the symptoms for?
Patient: Since Sunday
Doctor: Ah I see. Which symptoms do you have at present?
Patient: My face is swollen, my cheeks hurt, my eyelids are swollen, and I am running a slight fever, and I can feel something draining down the back of my throat
----
Summary Instructions
----
Provide a summary of the medical encounter between the doctor and the 21 Female
patient in 6 sections ( Demographics and Social Determinants of Health , Patient
Intent , Pertinent Positives , Pertinent Unknowns , Pertinent Negatives , Medical
History ) . The definitions of each section are listed below . Write a paragraph
under each section , not bullet points and in case a piece of information or heading cannot be extracted from chat consider it unknown.

Demographics and Social Determinants of Health :
// Definition of section

Patient Intent :
// Definition of section

Pertinent Positives :
// Definition of section

Pertinent Unknowns :
// Definition of section
Pertinent Negatives :
// Definition of section

Medical History :
// Definition of section

----
Summary of Medical Encounter
----
""",
    expected_output="""a summary of the medical encounter between the doctor and the {age_and_sex}
patient in 6 sections ( Demographics and Social Determinants of Health , Patient
Intent , Pertinent Positives , Pertinent Unknowns , Pertinent Negatives , Medical
History )""",
    agent=decider,
)


task2 = Task(
    description="""
You ( Person A ) are a very good summary writer for medical dialogues between
physicians and patients .

This is the medical dialogue you summarized for a { age } and { sex } patient :
- Medical Dialogue -
{ chat }
- Medical Dialogue -

You are discussing the summary you wrote for this dialogue with another summary
writer ( Person B ) whose job it is to verify your summary for correctness .

Person B will give you points for correction and it will be your job to add the
points of correction to a scratchpad if you agree with them .

This is your original version of the summary :
- Your Original Summary -
{ summary }
- Your Original Summary -

Here is your current scratchpad of corrections to make to the summary :
- Correction Scratchpad -
{ scratchpad }
- Correction Scratchpad -

You are generally very confident about the summary you wrote , however , when
presented with compelling arguments by the verifying summary writer , you add to
the correction scratchpad . You also suggest any edits of your own in case you
notice a mistake .

This is the summary discussion so far :
- Summary Discussion -
{ discussion }
- Summary Discussion -

Question : What do you say next ? Respond to Person B in the tag [ RESPONSE : " <
your_response_here >"] and output any corrections to add to the scratchpad in the
tag [ SCRATCHPAD : " < things_to_add_to_the_scratchpad_here >"]. Make sure to use
the "[]" when outputting tags .
Answer :
""",
    expected_output="output any corrections to add to the scratchpad",
    agent=decider,
    context=[task1],
)

crew = Crew(
    agents=[decider, researcher],
    tasks=[task1, task2],
    verbose=True,
)

# Start the process
result = crew.kickoff()

print(result)
