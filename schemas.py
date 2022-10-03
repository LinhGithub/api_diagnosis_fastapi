from typing import Dict, Optional, Any, Type, List
from bson.objectid import ObjectId
from pydantic import BaseModel
from fastapi import Form
from datetime import datetime

import pydantic
import struct
import inspect

# fix ObjectId & FastApi conflict
pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str

class Response(BaseModel):
    code: Optional[int] = None
    msg: Optional[str] = None
    total: int = None
    status: str = None
    error: str = None
    info: Dict = None
    results: List = None
    id: str = None

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        return super().dict(*args, exclude_none=True, **kwargs)