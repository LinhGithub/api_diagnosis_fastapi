from fastapi import Request,APIRouter, Form
from fastapi.param_functions import Query
from fastapi.responses import FileResponse
from schemas import Response
from bson.objectid import ObjectId
import utils
from typing import Union
import os

import schemas

router = APIRouter(
    tags=["illnesses"]
)

mydb = utils.mydb
# illnesses
@router.get("/illnesses")
def get_illnesess(type: str = Query(None), rule: str = Query(None), page: int = Query(None), page_size: int = Query(None)):
    query = {}
    if type:
        query['type'] = type
    if rule:
        query['rule'] = rule
    if type and rule:
        query = {"$or": [{"type": type}, {"rule": rule}]}

    if page and page_size:
        illnesses = mydb.illnesses.find(query).skip((page - 1) * page_size).limit(page_size)
    else:
        illnesses = mydb.illnesses.find(query)

    total = mydb.illnesses.count_documents(query)

    response = Response(results=list(
        illnesses),total=total, code=200, msg="success").dict()
    return response


# get item by ids
@router.post('/illnesses/ids')
async def get_by_ids (req: schemas.Item):
    list_ids = req.list_ids
    queryObj = {}
    if list_ids:
        queryIll = {}
        queryObj["symptoms"] = { "$elemMatch": { "$in": list_ids } }
        rules = mydb.rules.distinct("symptoms", queryObj)
        ill_obj = []
        for r in rules:
            if r not in list_ids:
                ill_obj.append(ObjectId(r))

        queryIll["_id"] = { "$in": ill_obj }

        illnesses = mydb.illnesses.find(queryIll)
    else:
        queryObj = { "$or": [{ "type": "symptom" }, { "rule": "both" }] }
        illnesses = mydb.illnesses.find(queryObj)

    response = Response(results=list(
        illnesses), code=200, msg="success").dict()
    return response


@router.post('/illnesses')
async def illnesses_create(req: schemas.FormIllness):
    name = req.name
    type = req.type
    rule = req.rule
    illnesse = mydb.illnesses.find_one({"name": name})

    if not illnesse:
        insert_data = {
            "name": name,
            "type": type,
            "rule": rule,
            "created_at": utils.get_now(),
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
async def illnesses_update(id, req: schemas.FormIllness):
    name = req.name
    rule = req.rule
    filter = {'_id': ObjectId(id)}
    illnesse = mydb.illnesses.find_one({"name": name ,'_id': {'$ne': ObjectId(id)}})
    if not illnesse:
        illnesse = mydb.illnesses.find_one(filter)
        dateNew = {
            "$set":{
                'name': name,
                "rule": rule,
                "updated_at": utils.get_now(),
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

@router.get('/illnesses/download_file')
async def download_file(type: str = Query(None)):
    if type:
        if type in ["illness", "symptom", 'rule']:
            if type == "illness":
                name = "illnesses"
            elif type == "symptom":
                name = "symptoms"
            else:
                name = "rules"

            file_name = name + ".xlsx"
            _path = os.getcwd() + "/storage/" + file_name
            if os.path.isfile(_path):
                os.remove(_path)

            if type in ["illness", "symptom"]:
                header = ['num', "_id", "name", "rule", "type"]
                _list = []
                illnesses = mydb.illnesses.find({'type': type})
                index = 0
                for illn in illnesses:
                    index += 1
                    illness = []
                    illness.append(index)
                    illness.append(str(illn.get('_id')))
                    illness.append(str(illn.get('name')))
                    illness.append(str(illn.get('rule')))
                    illness.append(str(illn.get('type')))
                    _list.append(illness)

                _list.insert(0,header)
                utils.export_excel(name,_list)
            else:
                header = ['num', "_id", "illnesses_id", "symptoms"]
                _list = []
                rules = mydb.rules.find()
                index = 0
                for r in rules:
                    index += 1
                    rule = []
                    rule.append(index)
                    rule.append(str(r.get('_id')))
                    rule.append(str(r.get('illnesses_id')))
                    rule.append(', '.join(r.get('symptoms')))
                    _list.append(rule)

                _list.insert(0,header)
                utils.export_excel(name,_list)

            if os.path.isfile(_path):
                return Response(code=200, msg='Thành công', file_name=file_name).dict()

    return Response(code=0, msg='Thất bại').dict()