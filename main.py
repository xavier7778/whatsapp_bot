from fastapi import FastAPI, Request
from twilio.rest import Client
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
API_URL = os.getenv("LLM_API_URL")
headers = {
    "Content-Type": "application/json"
}

app = FastAPI()
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    # print(response)
    return response.json()


@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    form_data = await request.form()
    sender = form_data.get("From", "").strip()

    if sender.startswith("whatsapp:") and " " in sender:
        sender = sender.replace("whatsapp: ", "whatsapp:+")  # Fix formatting issue

    message_body = form_data.get("Body", "").strip()  # Message text

    # Send the reply back to the user
    output = query({
        "inputs": "<s>GPT4 Correct User: " + message_body + " <|end_of_turn|>GPT4 Correct Assistant:",
        "parameters": {
            "max_new_tokens": 1024,
        }})
    response = output['generated_text']

    client.messages.create(
        body=response,
        from_=TWILIO_WHATSAPP_NUMBER,
        to=sender,
    )

    return {"status": "success"}
