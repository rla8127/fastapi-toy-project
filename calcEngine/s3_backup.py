import os
import boto3
import logging
from datetime import datetime

# 해당 파일은 매일 00시 00분에 Corntab에서 실행하도록 설정되어 있음.

#################################
# AWS S3 설정
s3_client = boto3.client('s3', region_name='eu-north-1')
bucket_name = 'chunjae-test-donghyun-bucket'
##################################

##################################
# Logging 설정
##################################
access_log_name = os.path.join("logs", f"access_calc_log_{datetime.now().strftime('%Y%m%d')}.log")
error_log_name = os.path.join("logs", f"error_calc_log_{datetime.now().strftime('%Y%m%d')}.log")

calcLogger = logging.getLogger("")
calcLogger.setLevel(logging.INFO)

# 일반 핸들러
access_handler = logging.FileHandler(access_log_name)
access_handler.setLevel(logging.INFO)
access_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s - %(message)s')
access_handler.setFormatter(access_formatter)

# 일반 핸들러
error_handler = logging.FileHandler(error_log_name)
error_handler.setLevel(logging.ERROR)
error_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s - %(message)s')
error_handler.setFormatter(error_formatter)

calcLogger.addHandler(access_handler)
calcLogger.addHandler(error_handler)



##################################
# AWS S3 업로드 함수
##################################
def upload_log_to_s3(log_name):
    try:
        # 파일이름만 추출하도록 함. os.path.basename()
        s3_log_path = f"logs/{os.path.basename(log_name)}"
        s3_client.upload_file(log_name, bucket_name, log_name) 
        print(f"로그 파일 {log_name} 업로드 완료")
    except Exception as e:
        print(f"{log_name} 업로드 중 에러 발생: {e}")

upload_log_to_s3(access_log_name)
upload_log_to_s3(error_log_name)