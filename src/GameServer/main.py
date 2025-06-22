# copyright (c) 2025 Yuuki Furuta

import sys
import json
import base64
from io import BytesIO

from PIL import Image
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket,WebSocketDisconnect
from typing import List
# add import path
sys.path.append("/root/picthree/PicThreeGSS/src/GameServer")
sys.path.append("/root/picthree/PicThreeAI/src/AI")
sys.path.append("/root/picthree/PicThreeGSS/src/GameSys")
from loadImage import *
import RoleAnalyze
import StatusAnalyze

# TODO:userIdの複雑化

connectionID:int=0
cardid:int=0


app =FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:19009","http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token", "Access-Control-Allow-Origin"]
)

# TODO:List[Battle]
BattleMatchs:List=[]

@app.get("/")
async def root():
    return {"message":"Hello World"}

@app.get("/home")
async def home():
    return "<div>sample</div>"

@app.post("/uplaodfile")
async def uploadfile():
    
    pass


def createid():
    global connectionID
    connectionID+=1
    return connectionID

@app.websocket("/ws")
async def websocket_endpoint(websocket:WebSocket):
    await websocket.accept()
    try:
        while True:
            data=await websocket.receive_json()
            status=data["status"]
            print(data)
            if(status=="::connect::"):
                await websocket.send_json({"status":"firstConnect","userid":createid()})
            if(status=="usersetup"):
                pass
            if(status=="createCard"):
                sketch= Image.open(BytesIO(base64.b64decode(data["sketch"].split(",")[1])))
                userid=data["userID"]
                charaname=data["charaname"]
                imgid=await saveImg(userid,sketch)
                imgpath=f"/root/picthree/PicThreeGSS/src/GameServer/db/imgs/sketch{imgid}.png"
                role=RoleAnalyze.analyze(imgpath)
                if role=="attack":role=0
                if role=="guard":role=1
                if role=="healer":role=2
                if role=="speeder":role=3
                if role=="magician":role=4
                hp,attack,defence,speed=StatusAnalyze.analyze(imgpath)
                hp*=1000
                attack*=100
                defence*=100
                speed*=100
                hp=int(hp)
                attack=int(attack)
                defence=int(defence)
                speed=int(speed)
                
                cardid=createCard(userid,imgid,charaname,role,hp,attack,defence,speed)
                print((userid,imgid,charaname,role,hp,attack,defence,speed))
                # await websocket.send_json({"status":"test","data":role})
                await websocket.send_json({"status":"cardCreated","careateStatus":"success","cardid":cardid,"charaname":charaname,"sketch":data["sketch"],"cardstatus":{"role":role,"hp":hp,"attack":attack,"defence":defence,"speed":speed}})
            # await websocket.send_text(f"your msg is {data}")
    except WebSocketDisconnect:
        websocket.close()

async def GameRouter(routeCommand,data):
    
    if routeCommand=="battle_in":
        pass
    
    pass

async def MatchManager():
    
    pass

if __name__=="__main__":
    print(RoleAnalyze.analyze("/root/picthree/PicThreeAI/Apple.png"))
    wakeupDB()
    uvicorn.run("main:app",host="0.0.0.0",port=19004,lifespan="on",reload=True)
    pass