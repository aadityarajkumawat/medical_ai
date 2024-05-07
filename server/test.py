from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

import os
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

age = "50"
sex = "Female"

chat = """
Doctor-Patient Chat
Patient: I have a sinus infection and need something to knock it out.
Doctor: Hi melissa thank you for starting a visit. I am so sorry to hear about your sinus infection. How long have you had the symptoms for?
Patient: Since Sunday
Doctor: Ah I see. Which symptoms do you have at present?
Patient: My face is swollen, my cheeks hurt, my eyelids are swollen, and I am running a slight fever, and I can feel something draining down the back of my throat
"""

scratchpad = """
"""

discussion = """
"""

corruption_level = 5

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

task_2 = Task(
    description=f"""
----
Below is a medical encounter between a {age}
and {sex} patient and a doctor done over chat.
----
Medical Encounter
----
{chat}
----

Using the above dialogue, find the chief complaint of the patient.
Respond in the tag [RESPONSE : "<chief_complaint_here>"]. Make sure to use the "[]" when outputting tags.
----
Chief Complaint
----

""",
    expected_output="output the chief complaint",
    agent=chief_complaint_finder,
)

cc = task_2.execute()
cc = cc[cc.find("RESPONSE") + len('RESPONSE : "') : cc.find('"]')]
print(cc)

task_1 = Task(
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
    agent=summary_writer,
)

summary = task_1.execute()

task0 = Task(
    description=f"""
---
Below is a medical encounter between a {age} and {sex} patient and a doctor done over chat.
Chief complaint: "{cc}".
----
Medical Encounter
----
{chat}
----

Below is a summary of the conversation that was written using the following
instructions:
// Definition of medical summary (same as in initial summarization prompt)
----
Summary of Medical Encounter
----
{summary}
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
    expected_output="output the corrupted summary",
    agent=corrupter,
)

task1 = Task(
    description=f"""
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
    expected_output="Changes to be done in summary in the expected format",
    agent=researcher,
    verbose=True,
)

task2 = Task(
    description=f"""
You (Person A) are a very good summary writer for medical dialogues between physicians and patients.
This is the medical dialogue you summarized for a {age} and {sex} patient:
-Medical Dialogue -
{chat}
-Medical Dialogue -

You are discussing the summary you wrote for this dialogue with another summary writer (Person B) whose job it is to verify your summary for correctness.
Person B will give you points for correction and it will be your job to add the points of correction to a scratchpad if you agree with them.
This is your original version of the summary:
-Your Original Summary -
{summary}
-Your Original Summary -

Here is your current scratchpad of corrections to make to the summary:
-Correction Scratchpad -
{scratchpad}
-Correction Scratchpad -

You are generally very confident about the summary you wrote, however, when presented with compelling arguments by the verifying summary writer, you add to the correction scratchpad.
You also suggest any edits of your own in case you notice a mistake.
This is the summary discussion so far:
-Summary Discussion -
{discussion}
-Summary Discussion -

Question: What do you say next? Respond to Person B in the tag [RESPONSE: "<your_response_here>"] and output any corrections to add to the scratchpad in the
tag [SCRATCHPAD: "<things_to_add_to_the_scratchpad_here>"]. Make sure to use the "[]" when outputting tags.
Answer:
""",
    expected_output="Explain your decision in the expected format",
    agent=decider,
    verbose=True,
)

task3 = Task(
    description=f"""
---
You are a very good summary writer for medical dialogues between physicians and
patients.
This is the medical dialogue you summarized for a {age} and {sex} patient: -Medical Dialogue -
{chat}
-Medical Dialogue -
This is your original version of the summary:
-Original Summary -
{summary}
-Original Summary -
Here is your current scratchpad of corrections to make to the summary: -Correction Scratchpad -
{scratchpad}
-Correction Scratchpad -
Make all changes mentioned in the scratchpad to the original summary to output the corrected summary.
Output the tag "[STOP]" when finished writing the corrected summary. -Corrected Summary -
""",
    expected_output="Corrected summary",
    agent=editor,
)


crew = Crew(
    tasks=[task0, task1, task2],
    agents=[decider, researcher],
    process=Process.sequential,
    verbose=True,
    manager_llm=ChatOpenAI(model="gpt-4-turbo", max_tokens=4096),
)

d = crew.kickoff()

print(d)

scratchpad = d[d.find("SCRATCHPAD:") + len("SCRATCHPAD:") : d.find("]")]

# scratchpad = """
# 1. Correct the patient's demographics to '50-year-old female'.
# 2. Modify the 'Pertinent Positives' section to state 'slight fever' instead of 'high fever'.
# 3. Remove the information about smoking, alcohol consumption, and over-the-counter medications from the 'Pertinent Unknowns' section.
# 4. Revise the 'Pertinent Negatives' section to reflect the actual dialogue.
# 5. The 'Medical History' should only include information provided in the dialogue.
# """

# crew = Crew(
#     tasks=[task3],
#     verbose=True,
#     manager_llm=ChatOpenAI(model="gpt-4-turbo", max_tokens=4096),
# )

# d = crew.kickoff()

# print(d)

d = task3.execute()
print(d)
