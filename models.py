from pydantic import BaseModel, Field
from typing import Optional

######################################
# API 태스크 관리를 위한 클래스
######################################
class ApiRequest(BaseModel):
    task_id: int = Field(
        ...,
        ge=1, le=6, 
        description="""Task ID (1~5)<br>
        1번: 계산<br>
        2번: 번역<br>
        3번: 암호화<br>
        4번: 번역 -> 암호화<br>
        5번: 계산 -> 암호화<br>
        6번: 계산 -> 번역 -> 엔진<br>"""
    )
    direction: Optional[int] = None
    text: Optional[str] = None
    expression: Optional[str] = None

##########################################################
# API 태스크 관리 설계 전 코드 (개별 엔진 API 접근 목적)
##########################################################
# Post Method에 사용되는 BaseModel 데이터 유효성 검사
class CalcRequest(BaseModel): # POST 메서드에 사용하는 객체 선언
    expression: str = Field(
        ...,
        title="expression",
        description="Math Expression ( Support: +, - )",
        min_length=1, 
        max_length=1000
    )
    
class TransRequest(BaseModel):
    text: str
    direction: int
    
class EncryptRequest(BaseModel):
    text: str