# AI Sprint StrawHats Backend

model: https://huggingface.co/Ultralytics/YOLO11
move model to models/yolo11x.pt

## IV cam

install IV cam and connect to the phone
https://www.e2esoft.com/ivcam/

## env

SEARCH_API_KEY=from <https://www.searchapi.io/>
SESSION_SECRET_KEY=e867970cb91e811bc4fe9accab3cb8ce87f89aef542b8167deba741ae9499f85
OPENAI_API_KEY=sk-<https://platform.openai.com/api-keys>

## Commands

env : `python -m venv .venv`
activate : `.\.venv\Scripts\activate`

install fastAPI : `pip install "fastapi[standard]"`
install : `pip install -r requirements.txt`
run : `fastapi dev .\app\main.py  `
