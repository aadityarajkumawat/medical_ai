from crewai import Task
from agents.main import editor


def final_summarizer(age, sex, chat, summary, scratchpad):
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

    return task3
