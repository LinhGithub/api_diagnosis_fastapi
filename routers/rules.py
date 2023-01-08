from fastapi import Request,APIRouter, Form
from schemas import Response
from fastapi.param_functions import Query
from bson.objectid import ObjectId

import schemas

import utils

router = APIRouter(
    tags=["rules"]
)

mydb = utils.mydb

# rules
@router.get("/rules")
def get_rules(page: int = Query(None), page_size: int = Query(None)):
    query = {}
    total = mydb.rules.count_documents(query)

    if page and page_size:
        rules = mydb.rules.find(query).skip((page - 1) * page_size).limit(page_size)
    else:
        rules = mydb.rules.find(query)

    response = Response(results=list(
        rules),total=total, code=200, msg="success").dict()
    return response


@router.post('/rules')
async def rules_create(req: schemas.FormRule):
    illnesses_id  = req.illnesses_id
    symptoms = req.symptoms

    rule = mydb.rules.find_one({"illnesses_id": illnesses_id, "symptoms": symptoms})
    if not rule:
        insert_data = {
            "illnesses_id": illnesses_id,
            "symptoms": symptoms,
            "created_at": utils.get_now(),
        }

        x = mydb.rules.insert_one(insert_data)

        response = Response(code=200, msg='Thêm mới thành công', id=str(x.inserted_id)).dict()
    else:
        response = Response(code=0, msg='Luật đã tồn tại').dict()
    return response


@router.put('/rules/{id}')
async def rules_update(id, req: schemas.FormRule):
    filter = {'_id': ObjectId(id)}
    illnesses_id  = req.illnesses_id
    symptoms = req.symptoms

    rule = mydb.rules.find_one({"illnesses_id": illnesses_id, "symptoms": symptoms,'_id': {'$ne': ObjectId(id)}})
    if not rule:
        checkRule = mydb.rules.count_documents(filter)
        dateNew = {
            "$set":{
                "illnesses_id": illnesses_id,
                "symptoms": symptoms,
                "updated_at": utils.get_now(),
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
