from langchain_openai import ChatOpenAI
from agents.main import doctor
from crewai import Task
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

llm = ChatOpenAI(model_name="gpt-3.5-turbo", max_tokens=100)


def doctor_convo_task(chat: list[BaseMessage]):
    print(chat)
    return llm(chat).content


def translate_to_somali(text):
    return llm(
        [
            HumanMessage(
                f"Convert the following text to somali:\nText:{text}\nTranslation:"
            )
        ]
    ).content


def get_doctor_response(chat, translate=False):
    task = doctor_convo_task(chat)
    if translate:
        task = translate_to_somali(task)
    return task
