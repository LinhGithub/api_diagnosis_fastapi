from fastapi import APIRouter, Request
from fastapi.param_functions import Query
from schemas import Response
from bson.objectid import ObjectId
from schemas import Response

import api

router = APIRouter(
    tags=["diagnosis"]
)

mydb = api.mydb


@router.get('/')
def read_root():
    return {"code": 200, 'msg': "Api all ready!"}

# diagnosis
@router.post('/diagnosis')
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
