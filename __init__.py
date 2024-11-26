from pydantic import BaseModel, Field
from threading import Lock
import pika

###########################################
#          Variable Definition            #
###########################################
RABBITMQ_HOST = "localhost"

REDIS_HOST = "localhost"
REDIS_PORT = 6379

USERNAME = "fastapi_user" 
PASSWORD = "fastapi_user"

###########################################
#             Class Definition            #
###########################################
# Post Method에 사용되는 BaseModel 데이터 유효성 검사
class CalcRequest(BaseModel): # POST 메서드에 사용하는 객체 선언
    expression: str = Field(
        ...,
        title="expression",
        description="Math Expression ( Support: +, - )",
        min_length=1, 
        max_length=1000
    )

# RabbitMQ 싱글톤 객체
class RabbitMQSingleton:
    _instance = None # 유일한 클래스 인스턴스 지정
    _lock = Lock()   # 한 번에 하나의 스레드만 접근
    
    def __new__(cls, host, username, password, queue):
        if not cls._instance: # cls : 클래스 변수, self : 인스턴스 변수
            with cls._lock: # 한 번에 하나의 스레드만, 인스턴스를 생성 후 삭제할 수 있도록
                if not cls._instance:
                    cls._instance = super().__new__(cls) 
                    cls._instance._initialize(host, username, password, queue)
        return cls._instance
    
    def _initialize(self, host, username, password, queue):
        credentials = pika.PlainCredentials(username, password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, credentials=credentials, heartbeat=0)
            )
        self.channel = self.connection.channel()
        self.channel.queue_declare(
            queue=queue, 
            arguments={
                'x-message-ttl': 60000 # 메시지 TTL 설정 60초(MS 단위)
            },
            durable=True
            )
        return self.channel
    
    # Queue 선언 및 Exchange 정의
    def queue_publish(self, queue, message):
        self.channel.basic_publish(
                exchange='',
                routing_key=queue,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2, # 메시지 영구 저장
                )    
        )
        
    # 장기 미사용으로 Channel이 Idel 상태로 변환 시, 재 오픈을 위해 만듬
    def open_channel(self, queue):
        if self.channel is None or self.channel.is_closed:
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=queue, durable=True)
    
    def close(self):
        if self.channel:
            self.channel.close()
        if self.connection:
            self.connection.close()

