from fastapi import APIRouter

import api

router = APIRouter(
    tags=["diagnosis"]
)

mydb = api.mydb


@router.get('/')
def read_root():
    return {"code": 200, 'msg': "Api all ready!"}
