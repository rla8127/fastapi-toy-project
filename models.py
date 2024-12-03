from pydantic import BaseModel, Field
# Post Method에 사용되는 BaseModel 데이터 유효성 검사
class CalcRequest(BaseModel): # POST 메서드에 사용하는 객체 선언
    expression: str = Field(
        ...,
        title="expression",
        description="Math Expression ( Support: +, - )",
        min_length=1, 
        max_length=1000
    )
    queue_name: str = "calc_queue"
    
class TransRequest(BaseModel):
    text: str
    direction: int
    queue_name: str = "trans_queue"
    
class CryptRequest(BaseModel):
    text: str
    queue_name: str = "crpyt_queue"
