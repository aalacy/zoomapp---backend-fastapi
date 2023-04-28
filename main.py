from fastapi import FastAPI, Header, Request, Response
from pydantic import BaseModel
import uvicorn
from functools import lru_cache
import requests
import requests.auth
import shutil
from pathvalidate import sanitize_filename
import jwt
from datetime import datetime, timedelta
import os

from config import Settings

app = FastAPI()

BASE_PATH = os.path.abspath(os.curdir)
AUDIO_DIR = os.path.join(BASE_PATH, "audios")
if not os.path.exists(AUDIO_DIR):
    os.mkdir(AUDIO_DIR)

@lru_cache()
def get_settings():
    return Settings()

app.dependency_overrides[get_settings] = get_settings

class WebhookData(BaseModel):
    event: str
    event_ts: str
    payload: object

class WebhookResponse(BaseModel):
    result: str

def generate_oauth_token():
    settings = get_settings()
    print('settings ', settings)
    client_auth = requests.auth.HTTPBasicAuth(settings.zoom_client_id, settings.zoom_client_secret)
    response = requests.post("https://zoom.us/oauth/token?grant_type=account_credentials&account_id={}".format(settings.zoom_account_id), auth=client_auth)
    token_json = response.json()
    print("[access token] ", token_json)
    return token_json["access_token"]

def jwt_token():
    '''
        Generate jwt token from api_key
        @input 
            api_key
        @output
            jwt token

    '''
    settings = get_settings()
    expire = int(datetime.timestamp(datetime.now() + timedelta(days=2))) * 1000
    payload = {
        "iss": settings.zoom_api_key,
        "exp": expire
    }
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    return jwt.encode(payload, settings.zoom_api_secret, headers=headers)

def download_recording(file_info, access_token):
    print('[downloading ]', file_info)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    filename = os.path.join(AUDIO_DIR, f"{sanitize_filename(file_info['id'])}.{file_info['file_extension']}")
    with requests.get(f"{file_info['download_url']}", stream=True, headers=headers) as r:
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    
@app.get("/")
async def root():
    file_info = {
        'meeting_id': '123',
        'file_extension': 'm4a',
        'download_url': 'https://us06web.zoom.us/rec/webho'
    }
    access_token = jwt_token()
    download_recording(file_info, access_token)
    return {"message": "Hello World"}

@app.get("/recording")
async def recording():
    return {"message": "Ok"}

@app.post("/webhook", status_code=200)
async def recording_webhook(
    webhook_input: WebhookData,
    request: Request,
    response: Response,
    content_length: int = Header(...),
    x_zm_signature: str = Header(None)
):
    print('webhook', webhook_input, x_zm_signature)
    if (webhook_input.event == 'recording.completed'):
        for recording in webhook_input.payload['object']['recording_files']:
            if recording['recording_type'] == "audio_only":
                auth_token = jwt_token()
                download_recording(recording, auth_token)
    return { "status": 200 }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000,  reload=True, log_level="info")