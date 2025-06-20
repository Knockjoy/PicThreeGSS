# copyright (c) 2025 Yuuki Furuta

import uvicorn
from fastapi import FastAPI
# from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket,WebSocketDisconnect
from typing import List


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

@app.websocket("/ws")
async def websocket_endpoint(websocket:WebSocket):
    await websocket.accept()
    try:
        while True:
            data=await websocket.receive_text()
            print(data)
            await websocket.send_text(f"your msg is {data}")
    except WebSocketDisconnect:
        websocket.close()

async def GameRouter(routeCommand,data):
    if routeCommand=="battle_in":
        pass
    pass

async def MatchManager():
    
    pass

if __name__=="__main__":
    uvicorn.run("main:app",host="localhost",port=19009,lifespan="on",reload=True)
    pass