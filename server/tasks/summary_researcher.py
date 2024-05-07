from crewai import Task
from agents.main import researcher


def summary_research(age, sex, chat, summary, scratchpad, discussion):
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

    return task1


# def get_researcher_opinion(age, sex, chat, summary, scratchpad, discussion):
#     task = summary_research(age, sex, chat, summary, scratchpad, discussion)
