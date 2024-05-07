from crewai import Task
from agents.main import decider


def summary_decider(age, sex, chat, summary, scratchpad, discussion):
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

    return task2
