from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

from tasks.chief_compaint import get_chief_complaint
from tasks.initial_summary import get_initial_summary
from tasks.corrupted_summary import corrupt_summary
from tasks.summary_researcher import summary_research
from tasks.summary_decider import summary_decider
from tasks.final_summarizer import final_summarizer

from agents.main import decider, researcher, corrupter


import os
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


def summarizer(age, sex, chat, corruption_level=5, scratchpad="", discussion=""):
    cc = get_chief_complaint(age, sex, chat)
    print("Chief Complaint: ", cc)
    summary = get_initial_summary(age, sex, cc, chat)
    print("Summary: ", summary)

    corrupted_summary = corrupt_summary(age, sex, cc, chat, summary, corruption_level)
    summary_researcher = summary_research(
        age, sex, chat, summary, scratchpad, discussion
    )
    summary_decider_ = summary_decider(age, sex, chat, summary, scratchpad, discussion)

    crew = Crew(
        tasks=[corrupted_summary, summary_researcher, summary_decider_],
        agents=[decider, researcher, corrupter],
        process=Process.sequential,
        verbose=True,
        manager_llm=ChatOpenAI(model="gpt-4-turbo", max_tokens=4096),
    )

    d = crew.kickoff()

    print(d)

    scratchpad = d[d.find("SCRATCHPAD:") + len("SCRATCHPAD:") : d.find("]")]

    final_summary = final_summarizer(age, sex, chat, summary, scratchpad)

    summary = final_summary.execute()

    return summary
