import requests
from app.config import settings

models = ['models/gemini-2.0-flash', 'models/gemini-flash-latest', 'models/gemini-3.5-flash']
for m in models:
    url = f"https://generativelanguage.googleapis.com/v1beta/{m}:generateContent?key={settings.gemini_api_key}"
    res = requests.post(url, json={"contents": [{"parts": [{"text": "hi"}]}]})
    print(m, res.status_code, res.json().get('error', {}).get('code'))
