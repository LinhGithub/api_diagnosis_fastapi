from typing import Union
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from schemas import Response
from bson.objectid import ObjectId

import uvicorn
import settings
import api

from routers import (
    illnesses,
    rules
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
app. include_router(rules.router)

@app.get('/')
def read_root():
    return {"code": 200, 'msg': "Api all ready!"}


# diagnosis
@app.post('/diagnosis')
async def diagnosis(request: Request):
    json_data = await request.json()

    query={}
    facts = []
    symptoms = []
    rules = []

    for symptom in json_data.get('symptoms'):
        symptoms.append([symptom, 'person'])

    rules_db = mydb.rules.find(query)
    for rule_db in rules_db:
        d=[rule_db.get('symptoms'), rule_db.get('illnesses_id')]
        rules.append(d)

    results = api.check_assert(rules, symptoms)
    for item in results.get("facts"):
        if item not in symptoms:
            facts.append(item)
    facts_id = []
    for fact in facts:
        facts_id.append(ObjectId(fact[0]))
    
    query = {'_id': {'$in': facts_id}}
    illnesses_db = list(mydb.illnesses.find(query))

    response = Response(code=200, msg='success', results=illnesses_db).dict()
    return response
# ===


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=8000, reload=True)