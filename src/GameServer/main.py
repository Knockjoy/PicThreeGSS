# copyright (c) 2025 Yuuki Furuta

import uvicorn
from fastapi import FastAPI
# from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
import socketio

app =FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:19009","http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token", "Access-Control-Allow-Origin"]
)
sio=socketio.AsyncServer(cors_allow_origins='*',async_mode='asgi')
socket_app=socketio.ASGIApp(sio)
app.mount("/connect",socket_app)

@app.get("/")
async def root():
    return {"message":"Hello World"}

@app.get("/home")
async def home():
    return "<div>sample</div>"

@app.post("/uplaodfile")
async def uploadfile():
    
    pass

@sio.on("connect")
async def connect(sid,env):
    print(f"New Client Connected to this is : {str(sid)}")
    await sio.emit("send_msg", "Hello from Server")

@sio.on("disconnect")
async def disconnect(sid):
    print(f"Client Disconnect: {str(sid)}")


if __name__=="__main__":
    uvicorn.run("main:app",host="localhost",port=19009,lifespan="on",reload=True)
    pass