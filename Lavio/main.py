# source ~/my_Fastapi/Fastapi_venv/bin/activate
# uvicorn main:app --reload --host 0.0.0.0 --port 8081
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
import anthropic
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
import pymysql
from transformers import pipeline
import anthropic

pipe = pipeline("text-classification", model="hun3359/klue-bert-base-sentiment")


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key = "sec")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def chat(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/mirror_iframe", response_class=HTMLResponse)
async def chat(request: Request):
    return templates.TemplateResponse("mirror.html", {"request": request})

@app.post("/select_user")
async def select_user(request: Request, username: str = Form(...)):
    request.session['username'] = username
    return {"success": True}

@app.get("/personal")
async def personal(request: Request):
    username = request.session.get('username', '')
    request.session['sensitive'] = None
    request.session['lightColor'] = None
    request.session['contents'] = None

    if username == "최비오":
        img_path = "images/sample_toilet.jpg"
        p_path = "images/user1_p.png"
    elif username == "김지엘":
        img_path = "images/jiel_toilet.jpg"
        p_path = "images/jiel_p.png"
    elif username == "이라경":
        img_path = "images/lak_toilet.jpg"
        p_path = "images/user3.png"
    elif username == "박성일":
        img_path = "images/si_toilet.jpg"
        p_path = "images/user4.png"
    else:
        img_path = "images/user1.png"
        p_path = "images/user1_p.png"



    return templates.TemplateResponse("sample.html", {"request": request, "username": username, "img_path":img_path, "p_path":p_path})
    # return JSONResponse(content={"username":username,'session':request.session})

@app.post("/logout")
async def logout(request: Request):
    if request.session:
        request.session.clear()
    return RedirectResponse(url="/", status_code=303)

@app.get("/check_session")
async def set_biglight(request: Request):
    return JSONResponse(content={'session':request.session})

@app.get("/voice")
async def voice(request: Request):
    return templates.TemplateResponse("form.html",{'request':request})




client = anthropic.Anthropic(
    api_key=API_KEY,
)



def gonggam(text:str):
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        system=f"""넌 사용자의 감정을 이해해 줘야 해, 사용자의 감정 분류 결과와, 점수를 알려줄게, 
        감정분류 결과와 점수를 직접 말하지 않으면서 짧은 문장으로 사용자에게 공감해줘""",
        max_tokens=1000,
        temperature=0,
        messages=[
            {"role": "user", "content": text}
        ]
    )
    return message.content[0].text







@app.post("/voice_inp")
async def voice_inp(request: Request, voiceinput:str = Form(...)):
    senti = pipe(voiceinput)[0]['label']
    score = pipe(voiceinput)[0]['score']
    query = f"사용자 입력 텍스트:{voiceinput}, 입력 텍스트 감정분석 결과:{senti}, 감정분석 점수:{score}"
    message = gonggam(query)

    return JSONResponse(content={'voice_text': voiceinput, 'senti': senti, 'score': score, 'message':message})

