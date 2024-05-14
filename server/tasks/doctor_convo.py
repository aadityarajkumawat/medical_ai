from agents.main import doctor
from crewai import Task


def doctor_convo_task(chat, followup):
    task = Task(
        agent=doctor,
        description=f"""You are a doctor who is excellent at diagnosing patients based on their symptoms. You are having a conversation with a patient over chat, use the chat to understand the patient's symptoms and provide a medical diagnosis.

        --- Conversation History ---
        {chat}
        --- Conversation History ---

        --- Follow up query ---
        {followup}
        --- Follow up query ---
        """,
        expected_output="Question the patient about their symptoms and provide a medical diagnosis based on the conversation.",
    )

    return task


def get_doctor_response(chat, followup):
    print(chat, followup)
    task = doctor_convo_task(chat, followup)
    response = task.execute()
    return response
