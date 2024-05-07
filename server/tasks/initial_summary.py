from crewai import Task
from agents.main import summary_writer


def initial_summary(age, sex, cc, chat):
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

    return task_1


def get_initial_summary(age, sex, cc, chat):
    task = initial_summary(age, sex, cc, chat)
    summary = task.execute()
    return summary
