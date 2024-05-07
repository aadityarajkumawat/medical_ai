from crewai import Task
from agents.main import corrupter


def corrupt_summary(age, sex, cc, chat, summary, corruption_level):
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

    return task0


def get_corrupted_summary(age, sex, cc, chat, summary, corruption_level):
    task = corrupt_summary(age, sex, cc, chat, summary, corruption_level)
    summary = task.execute()
    return summary
