from fastapi import APIRouter, Form
from fastapi.param_functions import Query
from schemas import Response
from bson.objectid import ObjectId

import api

router = APIRouter(
    tags=["illnesses"]
)

mydb = api.mydb

# illnesses
@router.get("/illnesses")
def get_illnesess(type: str = Query(None), rule: str = Query(None)):
    query = {}
    if type:
        query['type'] = type
    if rule:
        query['rule'] = rule
    if type and rule:
        query = {"$or": [{"type": type}, {"rule": rule}]}

    illnesses = mydb.illnesses.find(query)
    total = mydb.illnesses.count_documents(query)

    response = Response(results=list(
        illnesses),total=total, code=200, msg="success").dict()
    return response


@router.post('/illnesses')
async def illnesses_create(name: str = Form(None), type: str = Form(None), rule: str = Form(None)):
    illnesse = mydb.illnesses.find_one({"name": name})

    if not illnesse:
        insert_data = {
            "name": name,
            "type": type,
            "rule": rule,
            "created_at": api.get_now(),
        }

        x = mydb.illnesses.insert_one(insert_data)

        response = Response(code=200, msg='Thêm mới thành công', id=str(x.inserted_id)).dict()
    else:
        if illnesse.get('type') == "illness":
            response = Response(code=0, msg='Tên bệnh đã tồn tại').dict()
        else:
            response = Response(code=0, msg='Tên triệu chứng đã tồn tại').dict()
    return response


@router.put('/illnesses/{id}')
async def illnesses_update(id, name: str = Form(None), rule: str = Form(None)):
    filter = {'_id': ObjectId(id)}
    illnesse = mydb.illnesses.find_one({"name": name ,'_id': {'$ne': ObjectId(id)}})
    if not illnesse:
        illnesse = mydb.illnesses.find_one(filter)
        dateNew = {
            "$set":{
                'name': name,
                "rule": rule,
                "updated_at": api.get_now(),
            }
        }
        if illnesse:
            mydb.illnesses.update_one(filter, dateNew)
            response = Response(code=200, msg='Cập nhật thành công').dict()
        else:
            response = Response(code=0, msg='Không tồn tại').dict()
    else:
        if illnesse.get('type') == "illness":
            response = Response(code=0, msg='Tên bệnh đã tồn tại').dict()
        else:
            response = Response(code=0, msg='Tên triệu chứng đã tồn tại').dict()
    return response


@router.delete('/illnesses/{id}')
async def illnesses_delete(id):
    filter = {'_id': ObjectId(id)}
    
    checkRule = mydb.rules.count_documents({'illnesses_id': id}) + mydb.rules.count_documents({'symptoms': id})
    if checkRule == 0:
        illnesse = mydb.illnesses.find_one(filter)
        if illnesse:
            mydb.illnesses.delete_one(filter)
            response = Response(code=200, msg='Xóa thành công').dict()
        else:
            response = Response(code=0, msg='Không tồn tại').dict()
    else:
        response = Response(code=0, msg='Không thể xóa, nó đã được gắn kết với luật').dict()

    return response
# ===