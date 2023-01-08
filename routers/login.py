from fastapi import APIRouter, Form
from fastapi.param_functions import Query
from schemas import Response
from bson.objectid import ObjectId
import bcrypt

import schemas

import utils

router = APIRouter(
    tags=["login"]
)

mydb = utils.mydb

# illnesses
@router.post("/login")
def get_illnesess(req: schemas.Item):
    username = req.username
    password = req.password
    print(username,password)
    if username and password:
        user = mydb.accounts.find_one({"username": username})

        if not user:
            response = Response(code=0, msg="Tên đăng nhập không tồn tại.").dict()
            return response
        
        # generating the salt
        salt = bcrypt.gensalt()

        user_pass = bytes(user.get('password'), 'utf-8')
        isValidPass = bcrypt.checkpw(password.encode('utf-8'), user_pass)
        if not isValidPass:
            response = Response(code=0, msg="Mật khẩu không chính xác.").dict()
            return response
        
        accessToken = "ASsljdgksGGwetetjog.sadgljl!aksg.dslkjsgd#"
        refreshToken = "ASsljdgksGGwetetjog.sadgljl!aksg.dslkjsgd#"
        response = Response(code=200,accessToken=accessToken, refreshToken=refreshToken, msg="Thành công.", role=user.get('role')).dict()
        return response

    response = Response(code=0, msg="Vui lòng điền đầy đủ thông tin.").dict()
    return response
