from s3_backup import *
import json

#####################
# 계산 엔진        
#####################
def calc(expression): 
    calc_list = [] 
    current_number = ""

    try:
        for char in expression:  
            # time.sleep(10000)
            if char.isdigit(): 
                current_number += char 
        
            elif char in ["+", "-"]: 
                if current_number == "":
                    raise ValueError("반복된 연산자는 불가능합니다.")
                
                calc_list.append(int(current_number)) 
                calc_list.append(char) 
                current_number = "" 
                
            else:
                raise ValueError(f"{char}는 처리할 수 없는 연산자입니다.")

        # 맨 우측의 값이 숫자일 경우 
        if current_number.isdigit(): 
            calc_list.append(int(current_number)) 

        result = calc_list[0] 

        for idx, item in enumerate(calc_list): 
            if item == "+": 
                result += calc_list[idx+1] 

            elif item == "-": 
                result -= calc_list[idx+1] 

        calcLogger.info(f"Result: {result}")
        return json.dumps({"result": result})
    
    except Exception as e:
        calcLogger.error(f"Error: {str(e)}")
        return json.dumps({"error": str(e)})