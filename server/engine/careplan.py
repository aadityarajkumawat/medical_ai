from tasks.initial_careplan import initial_careplan
from tasks.careplan_researcher import careplan_research
from tasks.careplan_decider import careplan_decider
from tasks.final_careplan import final_careplan

import os
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


def generate_final_careplan(age, sex, chat, scratchpad="", discussion=""):
    initial_careplan_task = initial_careplan(age, sex, chat)
    careplan = initial_careplan_task.execute()

    researcher_task = careplan_research(
        age, sex, chat, careplan, scratchpad, discussion
    )
    research_output = researcher_task.execute()

    research_out = research_output[
        research_output.find("RESEARCH") + len("RESEARCH:") : research_output.find("]")
    ]
    discussion = research_out

    decisions = careplan_decider(age, sex, chat, careplan, scratchpad, discussion)
    decisions_output = decisions.execute()

    decisions_scratchpad = decisions_output[
        decisions_output.find("SCRATCHPAD:")
        + len("SCRATCHPAD:") : decisions_output.find("]")
    ]
    scratchpad = decisions_scratchpad

    final_careplan_task = final_careplan(age, sex, chat, careplan, scratchpad)
    final_plan = final_careplan_task.execute()

    # clean up the final summary
    index_of_medication = final_plan.find("Medications")
    # remove stuff before this index
    final_plan = final_plan[index_of_medication:]

    final_plan = final_plan.replace("[STOP]", "")

    return final_plan
