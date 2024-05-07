from engine.summarizer import summarizer
from engine.careplan import generate_final_careplan

import os
from dotenv import load_dotenv

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

chat = """
Doctor-Patient Chat
Patient: I have a sinus infection and need something to knock it out.
Doctor: Hi melissa thank you for starting a visit. I am so sorry to hear about your sinus infection. How long have you had the symptoms for?
Patient: Since Sunday
Doctor: Ah I see. Which symptoms do you have at present?
Patient: My face is swollen, my cheeks hurt, my eyelids are swollen, and I am running a slight fever, and I can feel something draining down the back of my throat
"""

summary = summarizer(22, "Female", chat)
print(summary)

careplan = generate_final_careplan(22, "Female", chat)
print(careplan)
