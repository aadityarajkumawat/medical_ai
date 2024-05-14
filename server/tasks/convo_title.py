from agents.main import convo_title_generator
from crewai import Task


def get_convo_title(chat):
    task = Task(
        agent=convo_title_generator,
        description=f"""Generate a title for the given medical conversation.
        
        --- Medical Conversation ---
        {chat}
        --- Medical Conversation ---

        --- Title ---
        """,
        expected_output="output the title of the conversation",
    )

    title = task.execute()
    return title
