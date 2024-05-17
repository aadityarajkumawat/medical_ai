# import os
# from dotenv import load_dotenv

# load_dotenv()

# chat = """
# Doctor-Patient Chat
# Patient: I have a sinus infection and need something to knock it out.
# Doctor: Hi melissa thank you for starting a visit. I am so sorry to hear about your sinus infection. How long have you had the symptoms for?
# Patient: Since Sunday
# Doctor: Ah I see. Which symptoms do you have at present?
# Patient: My face is swollen, my cheeks hurt, my eyelids are swollen, and I am running a slight fever, and I can feel something draining down the back of my throat
# """

# summary = summarizer(22, "Female", chat)
# print(summary)

# careplan = generate_final_careplan(22, "Female", chat)
# print(careplan)

from __future__ import annotations
import threading
from flask import Flask, request
import math, random, os
from dotenv import load_dotenv
from typing import List

from gradio_client import Client

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase

from engine.summarizer import summarizer
from engine.careplan import generate_final_careplan

from tasks.doctor_convo import get_doctor_response
from tasks.convo_title import get_convo_title

import requests

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

SYSTEM_PROMPT = """You are a Reasoning + Acting (React) Chain Bot. You have to be interactive so ask the queries one by one from the user to reach to the final answer. Please provide a single Thought and single Action to the user so that the user can search the query of the action and provide you with the observation.

For example the chain would be like this:

User: Hi, I've been experiencing persistent headaches.
Assistant: Have you been drinking plenty of water?
User: Yes, I have been drinking plenty of water.
Assistant: What is your sleep schedule like?
User: I try to get min 8 hours of sleep.
Assistant: What is your screen time like?
User: I spends long hours in front of a computer screen but doesn't report significant eye strain.
Assistant: Considering your screen time, prolonged exposure to screens could lead to digital eye strain and headaches.
User: I will try to reduce my screen time.
Assistant: [STOP]

User: Hi, I've been having knee pain lately.
Assistant: Have you recently engaged in any strenuous physical activity?
User: No, I haven't.
Assistant: Do you have any history of previous knee injuries or surgeries?
User: Yes, I injured my knee playing sports several years ago.
Assistant: Have you noticed any swelling or instability in the knee?
User: Yes, I experience occasional swelling and feelings of instability.
Assistant: Given your history of a previous knee injury and current symptoms, there may be underlying issues such as osteoarthritis or ligament damage. I advise you to consult with a healthcare professional for a proper diagnosis and treatment plan.
User: Thank you, I will schedule an appointment with my doctor.
Assistant: [STOP]

"""


import datetime
import uuid
from sqlalchemy import (
    create_engine,
    String,
    Column,
    DateTime,
    JSON,
    Integer,
    ForeignKey,
)
import datetime as dt
from sqlalchemy.orm import declarative_base, relationship, mapped_column
from sqlalchemy.orm import sessionmaker

from flask_cors import CORS

# add cors
# Add CORS
CORS(app)


def get_time():
    return datetime.datetime.now()


def gen_id() -> str:
    return str(uuid.uuid4())


import os

DB_USER = os.getenv("PGUSER")
DB_PASSWORD = os.getenv("PGPASSWORD")
DB_HOST = os.getenv("PGHOST")
DB_PORT = os.getenv("PGPORT")
DB_NAME = os.getenv("PGDATABASE")

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

base = declarative_base()

factory = sessionmaker(bind=engine)
session = factory()


class UserProfile(base):
    __tablename__ = "user_profile"
    id = Column("id", String, primary_key=True)
    age = Column("age", Integer, nullable=False)
    gender = Column("gender", String, nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class MedicalConvo(base):
    __tablename__ = "medical_convo"
    id = Column("id", String, primary_key=True, default=gen_id)
    user_id = Column("user_id", String)
    convo_name = Column("convo_name", String)
    created_at = Column("created_at", DateTime, default=get_time)
    updated_at = Column("updated_at", DateTime, default=get_time)
    convo: Mapped[List["Convo"]] = relationship(back_populates="medical_convo")
    summary: Mapped[List["Summary"]] = relationship(back_populates="medical_convo")
    care_plan: Mapped[List["CarePlan"]] = relationship(back_populates="medical_convo")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Convo(base):
    __tablename__ = "convo"
    id = Column("id", String, primary_key=True, default=gen_id)
    user_id = Column("user_id", String)
    convo_id = mapped_column(ForeignKey("medical_convo.id"))
    role = Column("role", String)
    content = Column("content", String)
    medical_convo: Mapped["MedicalConvo"] = relationship(
        "MedicalConvo", back_populates="convo"
    )
    created_at = Column("created_at", DateTime, default=get_time)
    updated_at = Column("updated_at", DateTime, default=get_time)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Summary(base):
    __tablename__ = "summary"
    id = Column("id", String, primary_key=True, default=gen_id)
    convo_id = mapped_column(ForeignKey("medical_convo.id"))
    summary = Column("summary", String, default="")
    medical_convo: Mapped["MedicalConvo"] = relationship(
        "MedicalConvo", back_populates="summary"
    )
    created_at = Column("created_at", DateTime, default=get_time)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class CarePlan(base):
    __tablename__ = "care_plan"
    id = Column("id", String, primary_key=True, default=gen_id)
    convo_id = mapped_column(ForeignKey("medical_convo.id"))
    careplan = Column("careplan", String, default="")
    medical_convo: Mapped["MedicalConvo"] = relationship(
        "MedicalConvo", back_populates="care_plan"
    )
    created_at = Column("created_at", DateTime, default=get_time)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class WhatsApp(base):
    __tablename__ = "whatsapp"
    id = Column("id", String, primary_key=True, default=gen_id)
    from_number = Column("from_number", String)
    gender = Column("gender", String)
    age = Column("age", Integer)
    content = Column("content", String)
    role = Column("role", String)
    created_at = Column("created_at", DateTime, default=get_time)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class WhatsappCareplan(base):
    __tablename__ = "whatsapp_careplan"
    id = Column("id", String, primary_key=True, default=gen_id)
    from_number = Column("from_number", String)
    created_at = Column("created_at", DateTime, default=get_time)
    careplan = Column("careplan", String)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class WhatsappSummary(base):
    __tablename__ = "whatsapp_summary"
    id = Column("id", String, primary_key=True, default=gen_id)
    from_number = Column("from_number", String)
    created_at = Column("created_at", DateTime, default=get_time)
    summary = Column("summary", String)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# class TechnicianRequest(base):
#     __tablename__ = "TechnicianRequest"
#     id = Column("id", String, primary_key=True)
#     name = Column("name", String)
#     email = Column("email", String)
#     phone = Column("phone", String)
#     zipcode = Column("zipcode", String)
#     timestamp = Column("timestamp", DateTime)


engine.connect()

base.metadata.create_all(engine)

client = Client(
    "https://adityaedy01-mms.hf.space/",
    hf_token=os.getenv("HF_TOKEN"),
)


@app.route("/")
def hello_world():
    # mp.track("some form of id", "homepage", {"some": "property"})
    return "<p>Hello, World!</p>"


@app.route("/get-convo/<convo_id>")
def get_convo(convo_id):
    medical_convo = (
        session.query(MedicalConvo).where(MedicalConvo.id == convo_id).first()
    )
    # order by created_at desc
    convo = (
        session.query(Convo)
        .where(Convo.convo_id == medical_convo.id)
        .order_by(Convo.created_at.asc())
        .order_by(Convo.role.desc())
        .all()
    )

    convo = [c.as_dict() for c in convo]

    return {"convo": convo}


@app.route("/get-care-plan/<convo_id>")
def get_care_plan(convo_id):
    careplan = (
        session.query(CarePlan)
        .where(CarePlan.convo_id == convo_id)
        .order_by(CarePlan.created_at.desc())
        .first()
    )

    convo = session.query(MedicalConvo).where(MedicalConvo.id == convo_id).first()
    user_id = convo.user_id
    user = session.query(UserProfile).where(UserProfile.id == user_id).first()
    convos = (
        session.query(Convo)
        .where(Convo.convo_id == convo_id)
        .order_by(Convo.created_at.asc())
        .order_by(Convo.role.desc())
        .all()
    )

    last_chat = convos[-1]

    def generate_new_careplan():
        # generate summary
        chat = ""
        for con in convos:
            chat += con.role + ": " + con.content
        print(chat)
        care_plan_content = generate_final_careplan(user.age, user.gender, chat)
        cp = CarePlan(convo_id=convo_id, careplan=care_plan_content)
        session.add(cp)
        session.commit()
        return cp

    if careplan != None:
        careplan_is_stale = (last_chat.as_dict()["created_at"]).timestamp() > (
            careplan.as_dict()["created_at"]
        ).timestamp()
        if careplan_is_stale:
            cp = generate_new_careplan()
            return {"careplan": cp.as_dict()}
        else:
            return {"careplan": careplan.as_dict()}
    else:
        summ = generate_new_careplan()
        return {"careplan": summ.as_dict()}


@app.route("/get-summary/<convo_id>")
def get_summary(convo_id):
    summary = (
        session.query(Summary)
        .where(Summary.convo_id == convo_id)
        .order_by(Summary.created_at.desc())
        .first()
    )

    convo = session.query(MedicalConvo).where(MedicalConvo.id == convo_id).first()
    user_id = convo.user_id
    user = session.query(UserProfile).where(UserProfile.id == user_id).first()
    convos = (
        session.query(Convo)
        .where(Convo.convo_id == convo_id)
        .order_by(Convo.created_at.asc())
        .order_by(Convo.role.desc())
        .all()
    )

    last_chat = convos[-1]

    def generate_new_summary():
        # generate summary
        chat = ""
        for con in convos:
            chat += con.role + ": " + con.content
        print(chat)
        summary_content = summarizer(user.age, user.gender, chat)
        summ = Summary(convo_id=convo_id, summary=summary_content)
        session.add(summ)
        session.commit()
        return summ

    if summary != None:
        print("COOL", last_chat.as_dict()["created_at"].timestamp())
        summary_is_stale = (last_chat.as_dict()["created_at"]).timestamp() > (
            summary.as_dict()["created_at"]
        ).timestamp()
        if summary_is_stale:
            summ = generate_new_summary()
            return {"summary": summ.as_dict()}
        else:
            return {"summary": summary.as_dict()}
    else:
        summ = generate_new_summary()
        return {"summary": summ.as_dict()}


@app.route("/medical-convo/<user_id>")
def medical_convo(user_id):
    medical_convo = (
        session.query(MedicalConvo).where(MedicalConvo.user_id == user_id).all()
    )
    medical_convos = [mc.as_dict() for mc in medical_convo]
    return {"medical_convos": medical_convos}


@app.route("/get-medical-convo/<convo_id>")
def get_medical_convo(convo_id):
    medical_convo = (
        session.query(MedicalConvo).where(MedicalConvo.id == convo_id).first()
    )
    return {"medical_convo": medical_convo.as_dict()}


@app.route("/medical-convo", methods=["POST"])
def create_medical_convo():
    json = request.json
    print(json)

    medical_convo = MedicalConvo(
        user_id=json["user_id"],
        convo_name="Untitled",
    )

    session.add(medical_convo)

    session.commit()

    return {"status": "success", "id": medical_convo.id}


@app.route("/convo-chat", methods=["POST"])
def convo_chat():
    json = request.json

    convo_id = json["convo_id"]
    role = "user"
    content = json["content"]
    user_id = json["user_id"]
    history = json["history"]
    convo_length = json["len"]

    convo_name = "Untitled"

    if convo_length < 3:
        title = get_convo_title(history)
        convo_name = title

        session.query(MedicalConvo).where(MedicalConvo.id == convo_id).update(
            {MedicalConvo.convo_name: convo_name}
        )
        session.commit()

    print("HISTORY", history)

    convo = Convo(
        user_id=user_id,
        convo_id=convo_id,
        role=role,
        content=content,
    )

    response = get_doctor_response(history, content)

    response_convo = Convo(
        user_id=user_id,
        convo_id=convo_id,
        role="assistant",
        content=response,
    )

    session.add(convo)
    session.add(response_convo)

    session.commit()

    return {"status": "success", "response": response}


@app.route("/user-profile/<user_id>")
def user_profile(user_id):
    user_profile = session.query(UserProfile).where(UserProfile.id == user_id).first()
    if not user_profile:
        return {"user": None}
    return {"user": user_profile.as_dict()}


@app.route("/onboard-user", methods=["POST"])
def onboard_user():
    json = request.json

    age = json["age"]
    gender = json["gender"]
    user_id = json["user_id"]

    user_profile = UserProfile(age=age, gender=gender, id=user_id)

    session.add(user_profile)
    session.commit()

    return {"status": "success"}


def send_whatsapp_msg(id: str, from_number: str):
    def wr(msg: str):
        requests.post(
            f"https://graph.facebook.com/v19.0/{id}/messages",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.getenv('PERMA_TOKEN')}",
            },
            json={
                "messaging_product": "whatsapp",
                "to": from_number,
                "text": {"body": msg},
            },
        )

    return wr


from pydub import AudioSegment


def convert_wav_to_mp3(wav_file_path, mp3_file_path):
    # Load the WAV file
    audio = AudioSegment.from_wav(wav_file_path)

    # Export as MP3
    audio.export(mp3_file_path, format="mp3")
    print(f"Converted {wav_file_path} to {mp3_file_path}")


def convert_ogg_to_mp3(ogg_file_path, mp3_file_path):
    # Load the WAV file
    audio = AudioSegment.from_ogg(ogg_file_path)

    # Export as MP3
    audio.export(mp3_file_path, format="mp3")
    print(f"Converted {ogg_file_path} to {mp3_file_path}")


def speech_to_text(audio_path: str):
    res = client.predict(
        "Record from Mic",
        audio_path,
        audio_path,
        "som (Somali)",
        api_name="/predict",
    )
    print("SPEECH TO TEXT:", res)
    return res


import uuid
import urllib.request


def get_whatsapp_media_by_id(id: str):
    # get url by id
    url = f"https://graph.facebook.com/v19.0/{id}"

    headers = {
        "Authorization": f"Bearer {os.getenv('PERMA_TOKEN')}",
    }

    response = requests.get(url, headers=headers)

    data = response.json()
    url = data["url"]

    print(url)

    # urllib.request.urlretrieve("http://www.example.com/songs/mp3.mp3", "mp3.mp3")

    response = requests.get(url, headers=headers, allow_redirects=True)
    received_name = str(uuid.uuid4()) + ".ogg"
    print(response.content)
    open(f"audio/{received_name}", "wb").write(response.content)

    convert_ogg_to_mp3(f"audio/{received_name}", f"audio/{received_name}.mp3")

    return f"audio/{received_name}.mp3"


def send_whatsapp_audio(id: str, from_number: str):
    def wr(audio_path: str):
        # first upload the file
        file_name = str(uuid.uuid5()) + ".mp3"
        file_path = f"audio/{file_name}"

        convert_wav_to_mp3(audio_path, file_name)

        # upload file
        res = requests.post(
            url=f"https://graph.facebook.com/v19.0/{id}/messages",
            headers={
                "Authorization": f"Bearer {os.getenv('PERMA_TOKEN')}",
            },
            data={
                "type": "audio/mp3",
                "messaging_product": "whatsapp",
            },
            files=[
                (
                    "file",
                    (
                        file_name,
                        open(file_path, "rb"),
                        "audio/mpeg",
                    ),
                )
            ],
        )

        uploaded = res.json()

        print(uploaded)

        # get file url
        # res = requests.get(f"https://graph.facebook.com/v19.0/1155544232454984")

        # send audio

    return wr


@app.route("/bot")
def bot():
    query_params = request.args

    mode = query_params.get("hub.mode")
    challenge = query_params.get("hub.challenge")
    verify_token = query_params.get("hub.verify_token")

    if mode == "subscribe" and verify_token == VERIFY_TOKEN:
        return challenge

    return "Invalid Request"


@app.route("/bot", methods=["POST"])
def bot_post():
    print("cool")
    json = request.json

    import json as j

    print(j.dumps(json, indent=4))

    value = json["entry"][0]["changes"][0]["value"]

    if not "messages" in value:
        return {"status": "success"}

    messages = value["messages"]
    meta = value["metadata"]

    phone_id = meta["phone_number_id"]

    from_number = messages[0]["from"]
    timestamp = messages[0]["timestamp"]

    send_audio = send_whatsapp_audio(id=phone_id, from_number=from_number)

    if "audio" in messages[0]:
        print("reply audio")

        audio_received_id = messages[0]["audio"]["id"]

        received_audio_file = get_whatsapp_media_by_id(audio_received_id)
        text_received = speech_to_text(received_audio_file)

        # send_audio()
        return {"status": "success"}

    text = messages[0]["text"]["body"]

    send_msg = send_whatsapp_msg(id=phone_id, from_number=from_number)

    # find if there's any response after this timestamp

    msg_t = dt.datetime.fromtimestamp(int(timestamp))

    g = (
        session.query(WhatsApp)
        .where(WhatsApp.from_number == from_number)
        .where(WhatsApp.created_at > msg_t)
        .first()
    )
    if g is not None:
        print("DUPLICATE MESSAGE!")
        return {"status": "success"}

    print(text)

    # check if careplan is being generated!
    ca = (
        session.query(WhatsappCareplan)
        .where(WhatsappCareplan.from_number == from_number)
        .where(WhatsappCareplan.careplan == "generating")
        .first()
    )
    if ca is not None:
        print("CAREPLAN GENERATING!")
        return {"status": "success"}

    cs = (
        session.query(WhatsappSummary)
        .where(WhatsappSummary.from_number == from_number)
        .where(WhatsappSummary.summary == "generating")
        .first()
    )

    if cs is not None:
        print("SUMMARY GENERATING!")
        return {"status": "success"}

    if text == "/help":
        print("HELP!")
        send_msg(
            msg="You can use the following commands to interact:\n\n/new: Start a new conversation\n\n/careplan: Get a careplan based on your conversation\n\n/[age][gender(M or F)]: To update profile details\n\n/help: Get help on how to use the bot\n",
        )
        return {"status": "success"}

    if len(text) == 4 and text[0] == "/" and text != "/new":
        print("REGISTERING AGE AND GENDER!")
        if text[1].isdigit() and text[2].isdigit() and not text[3].isdigit():
            age = int(text[1] + text[2])
            gender = text[3].lower()

            send_msg(msg="Thanks for providing your age and gender!")

            wh = WhatsApp(
                from_number=from_number,
                content="Thanks for providing your age and gender!",
                role="assistant",
                gender=gender,
                age=age,
            )

            session.add(wh)
            session.commit()

        return {"status": "success"}

    history = ""

    # get a message
    msg = session.query(WhatsApp).where(WhatsApp.from_number == from_number).first()

    if msg is not None:
        print("CHECK IF AGE AND GENDER ARE SET!")
        # check
        mm = (
            session.query(WhatsApp)
            .where(WhatsApp.from_number == from_number)
            .where(WhatsApp.age != None)
            .where(WhatsApp.gender != None)
            .first()
        )
        if mm is None:
            print("ASKING FOR AGE AND GENDER!")
            send_msg(
                msg="Please provide your age and gender in the following format (/18M, for age 18 and gender male, and /24F for age 24 and gender female)",
            )
            return {"status": "success"}

    if text == "/new":
        print("STARTING NEW CONVO!")
        send_msg(
            msg="New conversation started! Go ahead and explain your symptoms",
        )

        # save convo to db
        user_text = WhatsApp(from_number=from_number, content="/new", role="user")
        session.add(user_text)
        session.commit()

        return {"status": "success"}
    elif text == "/summary":
        print("GETTING SUMMARY!")
        # get history
        last_checkpoint = (
            session.query(WhatsApp)
            .where(WhatsApp.from_number == from_number)
            .where(WhatsApp.content == "/new")
            .order_by(WhatsApp.created_at.desc())
            .first()
        )
        if last_checkpoint is None:
            history_list = []
            history = ""
            send_msg(msg="Not enough information to generate summary")
        else:
            print(last_checkpoint.as_dict())
            # find all convos with this user after this checkpoint
            convos = (
                session.query(WhatsApp)
                .where(WhatsApp.from_number == from_number)
                .where(WhatsApp.created_at > last_checkpoint.created_at)
                .order_by(WhatsApp.created_at.asc())
                .order_by(WhatsApp.role.desc())
                .all()
            )
            history_list = [c.as_dict() for c in convos]
            history = ""

            for h in history_list:
                history += h["role"] + ": " + h["content"] + "\n"

            # get gender, age and chat
            mm = (
                session.query(WhatsApp)
                .where(WhatsApp.from_number == from_number)
                .where(WhatsApp.age != None)
                .where(WhatsApp.gender != None)
                .first()
            )

            print(history)

            if mm is not None:
                age = mm.age
                gender = mm.gender

                s = WhatsappSummary(from_number=from_number, summary="generating")
                session.add(s)
                session.commit()

                carep = summarizer(age, gender, history)

                send_msg(carep)

                f = (
                    session.query(WhatsappSummary)
                    .where(WhatsappSummary.from_number == from_number)
                    .update({WhatsappSummary.summary: carep})
                )
                session.commit()

                print(f)

                return {"status": "success"}
            else:
                return {"status": "success"}

        return {"status": "success"}
    elif text == "/careplan":
        print("GETTING CAREPLAN!")
        # get history
        last_checkpoint = (
            session.query(WhatsApp)
            .where(WhatsApp.from_number == from_number)
            .where(WhatsApp.content == "/new")
            .order_by(WhatsApp.created_at.desc())
            .first()
        )
        if last_checkpoint is None:
            history_list = []
            history = ""

            send_msg(msg="Not enough information to generate careplan")

        else:
            print(last_checkpoint.as_dict())
            # find all convos with this user after this checkpoint
            convos = (
                session.query(WhatsApp)
                .where(WhatsApp.from_number == from_number)
                .where(WhatsApp.created_at > last_checkpoint.created_at)
                .order_by(WhatsApp.created_at.asc())
                .order_by(WhatsApp.role.desc())
                .all()
            )
            history_list = [c.as_dict() for c in convos]
            history = ""

            for h in history_list:
                history += h["role"] + ": " + h["content"] + "\n"

            # get gender, age and chat
            mm = (
                session.query(WhatsApp)
                .where(WhatsApp.from_number == from_number)
                .where(WhatsApp.age != None)
                .where(WhatsApp.gender != None)
                .first()
            )

            print(history)

            if mm is not None:
                age = mm.age
                gender = mm.gender

                s = WhatsappCareplan(from_number=from_number, careplan="generating")
                session.add(s)
                session.commit()

                care_plan_content = generate_final_careplan(age, gender, history)

                send_msg(care_plan_content)

                f = (
                    session.query(WhatsappCareplan)
                    .where(WhatsappCareplan.from_number == from_number)
                    .update({WhatsappCareplan.careplan: care_plan_content})
                )
                session.commit()

                print(f)

                return {"status": "success"}
            else:
                return {"status": "success"}

        return {"status": "success"}

    latest_start = (
        session.query(WhatsApp)
        .where(WhatsApp.from_number == from_number)
        .where(WhatsApp.content == "/new")
        .order_by(WhatsApp.created_at.desc())
        .first()
    )
    convos = (
        session.query(WhatsApp)
        .where(WhatsApp.from_number == from_number)
        .where(WhatsApp.created_at > latest_start.created_at)
        .order_by(WhatsApp.created_at.asc())
        .order_by(WhatsApp.role.desc())
        .all()
    )

    history = ""
    history_list = [
        SystemMessage(
            "You are a doctor, which that diagnoses patients by asking questions one at a time. Please ask the user questions to diagnose them. Users will start by describing their problem or symptoms."
        )
    ]
    i = 0
    print("----------")
    print("CONVOS", convos)
    print("----------")
    for h in convos:
        history_list.append(
            HumanMessage(h.content) if h.role == "user" else AIMessage(h.content)
        )
        history += h.role + ": " + h.content + "\n"
        i += 1

    history += "Patient: " + text
    history_list.append(HumanMessage(text))
    # else:
    #     history_list.append(HumanMessage(SYSTEM_PROMPT + f"\nUser: {text}"))

    print("HISTORY", history)

    doc_response = get_doctor_response(history_list)

    response = doc_response

    send_msg(response)

    # save convo to db
    user_text = WhatsApp(from_number=from_number, content=text, role="user")
    assistant_text = WhatsApp(
        from_number=from_number, content=response, role="assistant"
    )

    session.add(user_text)
    session.add(assistant_text)

    session.commit()

    return {"status": "success"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
