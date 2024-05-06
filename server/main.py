from crewai import Agent, Task, Crew, Process
import os
from dotenv import load_dotenv

load_dotenv()

from langchain.agents import load_tools

human_tools = load_tools(["human"])

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


chat = """
Doctor-Patient Chat
Patient: I have a sinus infection and need something to knock it out.
Doctor: Hi melissa thank you for starting a visit. I am so sorry to hear about your sinus infection. How long have you had the symptoms for?
Patient: Since Sunday
Doctor: Ah I see. Which symptoms do you have at present?
Patient: My face is swollen, my cheeks hurt, my eyelids are swollen, and I am running a slight fever, and I can feel something draining down the back of my throat
"""

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
You (Person A) are a very good summary writer for medical dialogues between physicians and patients.
This is the medical dialogue you summarized for a {age} and {sex} patient: -Medical Dialogue -
{chat}
-Medical Dialogue -
You are discussing the summary you wrote for this dialogue with another summary writer (Person B) whose job it is to verify your summary for correctness.
Person B will give you points for correction and it will be your job to add the points of correction to a scratchpad if you agree with them.
This is your original version of the summary: -Your Original Summary -
{summary}
-Your Original Summary -
Here is your current scratchpad of corrections to make to the summary: -Correction Scratchpad -
{scratchpad}
-Correction Scratchpad -
You are generally very confident about the summary you wrote, however, when presented with compelling arguments by the verifying summary writer, you add to the correction scratchpad. You also suggest any edits of your own in case you notice a mistake.
This is the summary discussion so far: -Summary Discussion -
{discussion}
-Summary Discussion -
Question: What do you say next? Respond to Person B in the tag [RESPONSE: "< your_response_here>"] and output any corrections to add to the scratchpad in the
tag [SCRATCHPAD: "<things_to_add_to_the_scratchpad_here>"]. Make sure to use the "[]" when outputting tags.
Answer:
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

This is the medical dialogue you will be referencing for a {age} and {sex} patient :
- Medical Dialogue -
{chat}
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
{summary}
- Person A's Original Summary -

Here is Person A's current scratchpad of corrections to make to the summary :
- Correction Scratchpad -
{scratchpad}
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
{discussion}
- Summary Discussion -

Question : What do you say next ? Respond to Person A in the tag [ RESPONSE : " <
your_response_here >"]. If you are done correcting and are satisfied , output the
"[ STOP ]" tag .
Answer :

""",
    memory=True,
    verbose=True,
    max_iter=40,
    allow_delegation=False,
)


def task1(age: int, sex: str, cc: str, chat: str) -> Task:
    # Create tasks for your agents
    task = Task(
        description=f"""
----
Below is a medical encounter between an {age}
and {sex} patient and a doctor done over chat.
Chief Complaint : "{cc}".
----
Medical Encounter
----
{chat}
----
Summary Instructions
----
Provide a summary of the medical encounter between the doctor and the {age} and {sex}
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
        expected_output=f"""a summary of the medical encounter between the doctor and the {age} and {sex}
patient in 6 sections ( Demographics and Social Determinants of Health , Patient
Intent , Pertinent Positives , Pertinent Unknowns , Pertinent Negatives , Medical
History )""",
        agent=decider,
    )

    return task


def task2(age, sex, chat, cc, corruption_level, context: Task) -> Task:
    task = Task(
        description=f"""
---
Below is a medical encounter between a {age} and {sex} patient and a doctor done over chat.
Chief complaint: "{cc}".
----
Medical Encounter
----
{chat}
----

Using the above dialogue and provided summary, corrupt the summary slightly. This
could include moving a positive symptom to be a negative symptom, making up medical history mentioned , etc.
Corruptions should only occur on the Pertinent Positives , Pertinent Unknowns , Pertinent Negative , or Medical History section.
The lower the desired corruption level, the fewer the changes made. Note that a 0 would be not changing the summary at all, and a 10 would be completely corrupting the summary.
Note that any changes/corruption should make the summary less factual.

Desired Corruption Level: {corruption_level}/10
----
Corrupted Summary of Medical Encounter
----
""",
        expected_output="output any corrections to add to the scratchpad",
        agent=decider,
        context=context,
    )

    return task


def task3(age, sex, chat, context) -> Task:
    task = Task(
        description=f"""
You (Person A) are a very good summary writer for medical dialogues between physicians and patients.
This is the medical dialogue you summarized for a {age} and {sex} patient:

-Medical Dialogue -
{chat}
-Medical Dialogue -

You are discussing the summary you wrote for this dialogue with another summary writer (Person B) whose job it is to verify your summary for correctness.
Person B will give you points for correction and it will be your job to add the points of correction to a scratchpad if you agree with them.

Here is your current scratchpad of corrections to make to the summary:
-Correction Scratchpad -

-Correction Scratchpad -

You are generally very confident about the summary you wrote, however, when presented with compelling arguments by the verifying summary writer, you add to the correction scratchpad. You also suggest any edits of your own in case you notice a mistake.
This is the summary discussion so far:
-Summary Discussion -

-Summary Discussion -

Question: What do you say next? Respond to Person B in the tag [RESPONSE: "< your_response_here>"] and output any corrections to add to the scratchpad in the
tag [SCRATCHPAD: "<things_to_add_to_the_scratchpad_here>"]. Make sure to use the "[]" when outputting tags.
Answer:
""",
        expected_output="""giving Person A points for correction based on any mistakes /
discrepancies you see between the dialogue and summary one section at a time .""",
        agent=researcher,
        context=context,
    )

    return task


def chain(age, sex, cc, chat):
    out1 = task1(age, sex, cc, chat)
    print("OUTPUT1")
    print(out1.output)
    out2 = task2(age, sex, chat, cc, 5, [out1])
    print("OUTPUT2")
    print(out2.output)
    # out3 = task3(age, sex, chat, [out1, out2])
    # print("OUTPUT3")
    # print(out3.output)

    return [out1, out2]


crew = Crew(
    agents=[decider, researcher],
    tasks=chain(21, "Female", "Sinus Infection", chat),
    verbose=True,
    process=Process.sequential,
)

# Start the process
result = crew.kickoff()

print(result)
