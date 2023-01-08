from fastapi import APIRouter

import utils

router = APIRouter(
    tags=["home"]
)

mydb = utils.mydb


@router.get('/')
def read_root():
    return {"code": 200, 'msg': "Api all ready!"}
