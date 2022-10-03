from fastapi import Request,APIRouter, Form
from schemas import Response
from bson.objectid import ObjectId

import api

router = APIRouter(
    tags=["rules"]
)

mydb = api.mydb

# rules
@router.get("/rules")
def get_rules():
    query = {}
    rules = mydb.rules.find(query)
    total = mydb.rules.count_documents(query)

    response = Response(results=list(
        rules),total=total, code=200, msg="success").dict()
    return response


@router.post('/rules')
async def rules_create(request: Request):
    json_data = await request.json()
    illnesses_id  = json_data.get('illnesses_id')
    symptoms = json_data.get("symptoms")

    rule = mydb.rules.find_one({"illnesses_id": illnesses_id, "symptoms": symptoms})
    if not rule:
        insert_data = {
            "illnesses_id": illnesses_id,
            "symptoms": symptoms,
            "created_at": api.get_now(),
        }

        x = mydb.rules.insert_one(insert_data)

        response = Response(code=200, msg='Thêm mới thành công', id=str(x.inserted_id)).dict()
    else:
        response = Response(code=0, msg='Luật đã tồn tại').dict()
    return response


@router.put('/rules/{id}')
async def rules_update(id, request: Request):
    filter = {'_id': ObjectId(id)}
    json_data = await request.json()
    illnesses_id  = json_data.get('illnesses_id')
    symptoms = json_data.get("symptoms")

    rule = mydb.rules.find_one({"illnesses_id": illnesses_id, "symptoms": symptoms,'_id': {'$ne': ObjectId(id)}})
    if not rule:
        checkRule = mydb.rules.count_documents(filter)
        dateNew = {
            "$set":{
                "illnesses_id": illnesses_id,
                "symptoms": symptoms,
                "updated_at": api.get_now(),
            }
        }
        if checkRule == 1:
            mydb.rules.update_one(filter, dateNew)
            response = Response(code=200, msg='Cập nhật thành công').dict()
        else:
            response = Response(code=0, msg='Luật không tồn tại').dict()
    else:
        response = Response(code=0, msg='Luật đã tồn tại').dict()
    return response


@router.delete('/rules/{id}')
async def rules_delete(id):
    filter = {'_id': ObjectId(id)}
    
    rule = mydb.rules.find_one(filter)
    if rule:
        mydb.rules.delete_one(filter)
        response = Response(code=200, msg='Xóa thành công').dict()
    else:
        response = Response(code=0, msg='Luật không tồn tại').dict()

    return response
# ===
