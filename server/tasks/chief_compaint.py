from crewai import Task
from agents.main import chief_complaint_finder


def chief_complaint_task(age, sex, chat):
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

    return task_2


def get_chief_complaint(age, sex, chat):
    task = chief_complaint_task(age, sex, chat)
    cc = task.execute()
    cc = cc[cc.find("RESPONSE") + len('RESPONSE : "') : cc.find('"]')]
    return cc
