from typing import Union
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson.objectid import ObjectId

import uvicorn
import settings
import api

from routers import (
    home,
    illnesses,
    rules,
    diagnosis
)


app = FastAPI(
    title="Expert system"
)

mydb = api.mydb

@app.exception_handler(Exception)
async def validation_exception_handler(request, err):
    return JSONResponse(status_code=500, content={'code': 500, 'msg': 'fail'})

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(illnesses.router)
app.include_router(rules.router)
app.include_router(diagnosis.router)
app.include_router(home.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=8000, reload=True)