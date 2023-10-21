from fastapi import FastAPI, Form, Depends
from decouple import config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import openai

from models import Conversation
from utils import get_text_from_pdf, logger, extract_media_id, download_file
from db import get_db
from ai import get_conversation_chain, chunk_text, get_embeddings
from twilio_client import send_message

app = FastAPI()
openai.api_key = config("OPENAI_API_KEY")
whatsapp_number = config("TO_NUMBER")
chat_histories = {}
conversational_chains = {}
user_keys = {}


@app.post("/message")
async def reply(Body: str = Form("give me a one paragraph summary of the document"), 
                NumMedia: int = Form(None),
                MediaContentType0: str = Form(None), 
                MediaUrl0: str = Form(None), 
                From: str = Form(...),
                db: Session = Depends(get_db)):

    chat_response = ""
    conversation_chain = None
    response = None
    if NumMedia > 0 and MediaContentType0 and MediaUrl0 and MediaContentType0 == "application/pdf":
        print(f"Media received. Type: {MediaContentType0}, URL: {MediaUrl0}")
        
        file_name = f"{extract_media_id(MediaUrl0)}.pdf"
        
        if not From in user_keys:
            user_key = f"{file_name}_{From}"
            user_keys[From] = user_key

        chat_history = chat_histories.get(user_key, [])
        conversation_chain = None
        download_file(MediaUrl0, file_name)
        with open(file_name, 'rt') as f:
            if f.readable():
                raw_text = get_text_from_pdf(file_name)
                text_chunks = chunk_text(raw_text)
                text_embeddings = get_embeddings(text_chunks)
                if not conversational_chains.get(user_key):
                    conversation_chain = get_conversation_chain(text_embeddings)
                    conversational_chains[user_key] = conversation_chain
                response = conversation_chain({"question": Body, "chat_history": chat_history})
                
                answer = response['answer']
                chat_response = answer
                chat_history.append((Body, answer))
                chat_histories[user_key] = chat_history
                conversational_chains[user_key] = conversation_chain
            else:
                logger.error(f"{file_name} could not be read")
    else:
        if not From in user_keys:
            chat_response = "send me a document first"
        else:
            user_key = user_keys[From]
            chat_history = chat_histories.get(user_key, [])
            conversation_chain = conversational_chains.get(user_key)
            response = conversation_chain({"question": Body, "chat_history": chat_history})
            answer = response['answer']
            chat_response = answer
    try:
        conversation = Conversation(
            sender=whatsapp_number,
            message=Body,
            response=chat_response
        )
        db.add(conversation)
        db.commit()
        logger.info(f"Conversation #{conversation.id} store in database")
    except Exception as e:
        db.rollback()
        logger.error(f"Error storing conversation in database: {e}")
    
    send_message(whatsapp_number, chat_response)
    return ""


@app.get("/")
async def index():
    return {"msg": "up & running"}