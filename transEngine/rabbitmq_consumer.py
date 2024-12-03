from transEngine import translate
from threading import Lock
from redis_set import set_result
import json
import pika
##########################################
# 변수선언
##########################################
HOST_NAME = "localhost"
USERNAME = "fastapi_user"
PASSWORD = "fastapi_user"

##########################################
# CallBack 함수
# 설명 : 계산엔진을 통해 결과값을 전달받음
##########################################
def callback(ch, method, properties, body):
    try:
        data = json.loads(body.decode())
        request_id = data.get("request_id")
        text = data.get("text")
        direction = data.get("direction")
        result = translate(text, direction)
        set_result(request_id, result)
        print({request_id})
        print(f"Result of {text}: {result}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")

    except Exception as e:
        print(f"Error {expression}: {e}") 

##########################################
# RabbitMQ 싱글톤 객체 정의 및 생성
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
            pika.ConnectionParameters(host=host, credentials=credentials)
            )
        self.channel = self.connection.channel()
        return self.channel 
    
    # 채널 비정상 종료 시 재연결을 위해 만든 함수
    def open_channel(self):
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue="trans_queue", durable=True)

##########################################
# RabbitMQ 인스턴스 생성
##########################################    
rabbitmq_instance = RabbitMQSingleton(host=HOST_NAME, username=USERNAME, password=PASSWORD)
rabbitmq_instance.channel.basic_consume(queue="trans_queue", on_message_callback=callback, auto_ack=False)  

##########################################
# Main - Start Message Consuming
##########################################
def consume_message():
    global rabbitmq_instance
    print("Comsumer Start: Waiting for messages")
    while(True):
        try:
            # 연결이 정상적인지 확인
            if rabbitmq_instance.connection.is_open:
                # 채널도 정상적인지 확인
                if rabbitmq_instance.channel.is_open:
                    rabbitmq_instance.channel.basic_consume(queue="trans_queue", on_message_callback=callback, auto_ack=False)  
                    rabbitmq_instance.channel.start_consuming()     
                # 채널이 열려있지 않을 경우 채널만 재연결  
                else:       
                    rabbitmq_instance.open_channel()       
                   
            # 연결 비정상일 시, 인스턴스 재생성 및 커넥션 / 채널 생성
            else:
                rabbitmq_instance = RabbitMQSingleton(host=HOST_NAME, username=USERNAME, password=PASSWORD)
                rabbitmq_instance._connect(host=HOST_NAME, username=USERNAME, password=PASSWORD)
                print(f"rabbitmq connection is reconnected !!!")
                
        except Exception as e:
            print(f"Error: {e}")
            
if __name__ == "__main__":
    consume_message()