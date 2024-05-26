from __future__ import annotations
from flask import Flask, request, send_from_directory, jsonify
import os
from dotenv import load_dotenv
from typing import List

from gradio_client import Client

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

import replicate

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from engine.summarizer import summarizer
from engine.careplan import generate_final_careplan

from tasks.doctor_convo import get_doctor_response
from tasks.convo_title import get_convo_title

import requests

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

app = Flask(__name__)

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

import redis

r = redis.from_url(os.getenv("REDIS_URL"))

from flask_cors import CORS

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

import uuid


def image_to_text(image_path: str):
    input = {"image": image_path, "prompt": "Describe this image."}
    output = replicate.run(
        "lucataco/moondream2:392a53ac3f36d630d2d07ce0e78142acaccc338d6caeeb8ca552fe5baca2781e",
        input=input,
    )

    response = ""

    for line in output:
        response += line

    print(response)
    return response


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


engine.connect()

base.metadata.create_all(engine)

client = Client(
    "https://adityaedy01-mms.hf.space/",
    hf_token=os.getenv("HF_TOKEN"),
)

MMS_URL = "https://api-inference.huggingface.co/models/facebook/mms-1b-all"
headers = {"Authorization": "Bearer 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"}

import subprocess


def flac_to_mp3(flac_path: str):
    # convert flac to mp3
    print("CONVERTING", flac_path, "to mp3")
    mp3_path = flac_path.replace(".flac", ".mp3")
    script = "scripts/flactomp3"
    subprocess.run([script, flac_path.replace(".flac", "")])
    return mp3_path


@app.route("/cmd", methods=["POST"])
def cmd():
    json = request.json
    cmd = json["cmd"]
    d = subprocess.run(
        cmd.split(" "),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        text=True,
    )
    return jsonify({"out": d.stdout, "err": d.stderr, "in": d.args})


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


def speech_to_text(audio_path: str):
    res = client.predict(
        "Record from Mic",
        audio_path,
        audio_path,
        "eng (English)",
        api_name="/predict",
    )
    print("SPEECH TO TEXT:", res)
    return res


def text_to_speech(text: str):
    API_URL = "https://api-inference.huggingface.co/models/facebook/mms-tts-eng"
    headers = {"Authorization": "Bearer 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"}

    response = requests.post(API_URL, headers=headers, json={"inputs": text})

    audio_path = "audio/" + str(uuid.uuid4()) + ".flac"
    open(audio_path, "wb").write(response.content)

    flac_to_mp3(audio_path)

    return audio_path.replace(".flac", ".mp3")


def get_whatsapp_media_by_id(id: str, media_type="audio"):
    # get url by id
    url = f"https://graph.facebook.com/v19.0/{id}"

    headers = {
        "Authorization": f"Bearer {os.getenv('PERMA_TOKEN')}",
    }

    response = requests.get(url, headers=headers)

    data = response.json()
    print(data)
    url = data["url"]
    mine_type = data["mime_type"]

    print(url)

    response = requests.get(url, headers=headers, allow_redirects=True)
    if media_type == "audio":
        received_name = str(uuid.uuid4()) + ".ogg"
        open(f"audio/{received_name}", "wb").write(response.content)

        return f"audio/{received_name}"
    else:
        exts = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
        }

        received_name = str(uuid.uuid4()) + exts[mine_type]

        open(f"images/{received_name}", "wb").write(response.content)

        return f"images/{received_name}"


def send_whatsapp_audio(id: str, from_number: str):
    def wr(audio_path: str):
        print("UPLOADING FILE", audio_path)
        file_name = audio_path.split(".")[0]

        # upload file
        res = requests.post(
            url=f"https://graph.facebook.com/v19.0/{id}/media",
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
                        open(audio_path, "rb"),
                        "audio/mpeg",
                    ),
                )
            ],
        )

        uploaded = res.json()

        print("UPLOADED FILE")

        print(uploaded)

        uploaded_id = uploaded["id"]

        # get file url
        print("GETTING FILE URL")
        response = requests.get(
            f"https://graph.facebook.com/v19.0/{uploaded_id}",
            headers={
                "Authorization": f"Bearer {os.getenv('PERMA_TOKEN')}",
            },
        )

        media_data = response.json()
        print("MEDIA DATA", media_data)

        media_url = media_data["url"]
        media_id = media_data["id"]

        print("MEDIA URL", media_url)
        print("SENDING MEDIA")

        # send audio
        requests.post(
            f"https://graph.facebook.com/v19.0/{id}/messages",
            headers={
                "Authorization": f"Bearer {os.getenv('PERMA_TOKEN')}",
            },
            json={
                "type": "audio",
                "messaging_product": "whatsapp",
                "to": from_number,
                "audio": {"id": media_id},
            },
        )

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


def get_history(text: str, from_number: str):
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
    print("----------")
    print("CONVOS", convos)
    print("----------")

    for h in convos:
        history_list.append(
            HumanMessage(h.content) if h.role == "user" else AIMessage(h.content)
        )
        history += h.role + ": " + h.content + "\n"

    history += "user: " + text
    history_list.append(HumanMessage(text))

    return history_list, history


@app.route("/images/<path:path>")
def send_report(path):
    return send_from_directory("images", path)


@app.route("/bot", methods=["POST"])
def bot_post():
    json = request.json

    import json as j

    print(j.dumps(json, indent=4))

    value = json["entry"][0]["changes"][0]["value"]

    if not "messages" in value:
        return {"status": "success"}, 200

    meta = value["metadata"]
    phone_id = meta["phone_number_id"]

    messages = value["messages"]
    from_number = messages[0]["from"]
    timestamp = messages[0]["timestamp"]

    send_audio = send_whatsapp_audio(id=phone_id, from_number=from_number)
    send_msg = send_whatsapp_msg(id=phone_id, from_number=from_number)

    process = r.get(phone_id)
    if process != None:
        msg = "Please wait..."
        if process == "summary_worker":
            msg = "Generating summary..."
        if process == "careplan_worker":
            msg = "Generating careplan..."
        if process == "audio_worker":
            msg = "Generating response..."

        print("PROCESS RUNNING: ", process)
        send_msg(msg)
        return {"status": "success"}, 200

    if "audio" in messages[0]:
        print("reply audio")

        audio_received_id = messages[0]["audio"]["id"]

        r.set(phone_id, "audio_worker", ex=120)

        received_audio_file = get_whatsapp_media_by_id(audio_received_id)
        text_received = speech_to_text(received_audio_file)

        history_list, history = get_history(text_received, from_number)

        doc_response = get_doctor_response(history_list)

        response = doc_response

        audio_response_path = text_to_speech(response)
        send_audio(audio_response_path)

        # save convo to db
        user_text = WhatsApp(
            from_number=from_number, content=text_received, role="user"
        )
        assistant_text = WhatsApp(
            from_number=from_number, content=response, role="assistant"
        )

        session.add(user_text)
        session.add(assistant_text)

        session.commit()

        r.delete(phone_id)

        return {"status": "success"}, 200

    if "image" in messages[0]:
        image_received_id = messages[0]["image"]["id"]
        r.set(phone_id, "image_worker", ex=120)

        received_image_file = get_whatsapp_media_by_id(
            image_received_id, media_type="image"
        )
        print("GENERATING RESPONSE")

        prod = True

        base_url = (
            "https://flask-production-213b.up.railway.app/"
            if prod
            else "http://localhost:5001/"
        )

        public_url = base_url + received_image_file

        description = image_to_text(public_url)
        print("DESCRIPTION", description)
        send_msg(msg=str(description))

        r.delete(phone_id)

        return {"status": "success"}, 200

    text = messages[0]["text"]["body"]

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
        return {"status": "success"}, 200

    if text == "/help":
        print("HELP!")
        send_msg(
            msg="You can use the following commands to interact:\n\n/new: Start a new conversation\n\n/careplan: Get a careplan based on your conversation\n\n/[age][gender(M or F)]: To update profile details\n\n/help: Get help on how to use the bot\n",
        )
        return {"status": "success"}, 200

    if len(text) == 4 and text[0] == "/" and text != "/new":
        print("REGISTERING AGE AND GENDER!")
        if text[1].isdigit() and text[2].isdigit() and not text[3].isdigit():
            age = int(text[1] + text[2])
            gender = text[3].lower()

            send_msg(msg="Thanks for providing your age and gender!")

            r.set(f"age_{phone_id}", age)
            r.set(f"gender_{phone_id}", gender)

        return {"status": "success"}, 200

    # ask for age and gender is its the first message
    # msg = session.query(WhatsApp).where(WhatsApp.from_number == from_number).first()
    age = r.get(f"age_{phone_id}")
    gender = r.get(f"gender_{phone_id}")

    if age is None or gender is None:
        send_msg(
            msg="Please provide your age and gender in the following format (/18M, for age 18 and gender male, and /24F for age 24 and gender female)",
        )
        return {"status": "success"}, 200

    if text == "/new":
        print("STARTING NEW CONVO!")
        send_msg(
            msg="New conversation started! Go ahead and explain your symptoms",
        )

        # save convo to db
        user_text = WhatsApp(from_number=from_number, content="/new", role="user")
        session.add(user_text)
        session.commit()

        return {"status": "success"}, 200
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

            if mm is not None:
                age = mm.age
                gender = mm.gender

                r.set(phone_id, "summary_worker", ex=360)

                carep = summarizer(age, gender, history)

                send_msg(carep)

                f = (
                    session.query(WhatsappSummary)
                    .where(WhatsappSummary.from_number == from_number)
                    .update({WhatsappSummary.summary: carep})
                )
                session.commit()

                r.delete(phone_id)

                print(f)

                return {"status": "success"}, 200
            else:
                return {"status": "success"}, 200

        return {"status": "success"}, 200
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

            if mm is not None:
                age = mm.age
                gender = mm.gender

                r.set(phone_id, "careplan_worker", ex=360)

                care_plan_content = generate_final_careplan(age, gender, history)

                send_msg(care_plan_content)

                f = (
                    session.query(WhatsappCareplan)
                    .where(WhatsappCareplan.from_number == from_number)
                    .update({WhatsappCareplan.careplan: care_plan_content})
                )
                session.commit()

                r.delete(phone_id)

                print(f)

                return {"status": "success"}, 200
            else:
                return {"status": "success"}, 200

        return {"status": "success"}, 200

    history_list, history = get_history(text, from_number)

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

    return {"status": "success"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT"))
