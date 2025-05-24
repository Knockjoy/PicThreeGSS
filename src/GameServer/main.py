# copyright (c) 2025 Yuuki Furuta

from fastapi import FastAPI

app =FastAPI()

@app.get("/")
async def root():
    return {"message":"Hello World"}