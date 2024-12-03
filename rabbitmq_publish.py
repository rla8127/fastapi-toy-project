from threading import Lock
from models import *
import pika
import uuid
import json

###########################################
#          Variable Definition            #
###########################################
HOST_NAME = "localhost"
USERNAME = "fastapi_user" 
PASSWORD = "fastapi_user"

##########################################
# RabbitMQ 싱글톤 객체 정의
##########################################
class RabbitMQSingleton:
    _instance = None 
    _lock = Lock()   
    
    def __new__(cls, host, username, password):
        if not cls._instance: 
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls) 
                    cls._instance._connect(host, username, password)
        return cls._instance
    
    def _connect(self, host, username, password):
        credentials = pika.PlainCredentials(username, password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, credentials=credentials, heartbeat=0)
            )
        
        queues = ["calc_queue", "trans_queue", "crypt_queue"]
        
        self.channel = self.connection.channel()
        
        for queue_name in queues:
            self.channel.queue_declare(
                queue="calc_queue",
                arguments={
                    'x-message-ttl': 60000 # 메시지 TTL 설정 60초(60000MS)
                },
                durable=True
            )
        
        return self.channel
    
    # 메시지 퍼블리싱
    def queue_publish(self, message, queue_name):
        self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2, # 메시지 영구 저장
                )    
        )
        
    # 장기 미사용으로 Channel이 Idel 상태로 변환 시, 재 오픈을 위해 만듬
    def open_channel(self):
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue="calc_queue", durable=True)
    
    def close(self):
        if self.channel:
            self.channel.close()
        if self.connection:
            self.connection.close()
        
##########################################
# RabbitMQ 인스턴스 생성
##########################################    
rabbitmq_instance = RabbitMQSingleton(host=HOST_NAME, username=USERNAME, password=PASSWORD)

###################################################### 
# RabbitMQ 메시지 퍼블리싱 
######################################################
def send_message(request):
    global rabbitmq_instance
    while(True):
        try:
            request_id = str(uuid.uuid4())
            
            if isinstance(request, CalcRequest):
                message = json.dumps({
                    "request_id": request_id,
                    "expression": request.expression
                }).encode()
                
            elif isinstance(request, TransRequest):
                message = json.dumps({
                    "request_id": request_id,
                    "text": request.text,
                    "direction": request.direction
                }).encode()
                
            elif isinstance(request, CryptRequest):
                message = json.dumps({
                    "request_id": request_id,
                    "text": request.text,
                }).encode()
                
            # 연결이 정상적인지 확인
            if rabbitmq_instance.connection.is_open:
                # 채널도 정상적인지 확인, 모두 정상이면 퍼블리싱
                if rabbitmq_instance.channel.is_open:
                    rabbitmq_instance.queue_publish(message, request.queue_name)
                # 채널이 열려있지 않을 경우 채널만 재연결  
                else:
                    rabbitmq_instance.open_channel()
            # 연결 비정상일 시, 인스턴스 재생성 및 커넥션 / 채널 생성
            else:
                rabbitmq_instance = RabbitMQSingleton(host=HOST_NAME, username=USERNAME, password=PASSWORD)
                rabbitmq_instance._connect(host=HOST_NAME, username=USERNAME, password=PASSWORD) 
                print(f"rabbitmq connection is reconnected !!!")   
                
            return request_id
        
        except Exception as e:
            print(f"Error: {e}")

