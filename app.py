from flask import Flask, render_template, request, jsonify
from PIL import Image
import io
import numpy as np
import cv2
import os

import openai
import base64
from openai import OpenAI
import json
from pydantic import BaseModel

from importlib.metadata import version, PackageNotFoundError

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('./index.html')

# test : 필요한 정보를 반환하는 엔드포인트 (ex. 라이브러리 버전 확인)
@app.route("/test", methods=['GET'])
def test_():
    try:
        # Get OpenAI library version
        openai_version = version("openai")
        response = {"openai_version": openai_version}
        
    except PackageNotFoundError:
        # Handle case where OpenAI library is not installed
        response = {"error": "OpenAI library is not installed"}
    return jsonify(response)
    
# test : GET 요청을 처리하는 간단한 엔드포인트
@app.route('/api/hello', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello, World!"})

# test : POST 요청을 처리하는 엔드포인트
@app.route('/api/echo', methods=['POST'])
def echo():
    data = request.json  # JSON 데이터를 받음
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    return jsonify({"received": data})

# test : 간단한 파라미터 처리
@app.route('/api/square/<int:number>', methods=['GET'])
def square(number):
    result = number ** 2
    return jsonify({"number": number, "square": result})

# test : 이미지 크기를 반환하는 엔드포인트
@app.route('/api/image-size', methods=['POST'])
def image_size():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty file"}), 400

    try:
        # 이미지를 열고 크기 반환
        image = Image.open(io.BytesIO(file.read()))
        width, height = image.size
        return jsonify({"width": width, "height": height})
    except Exception as e:
        return jsonify({"error": f"Invalid image file: {str(e)}"}), 400

# ============================================================================
# 환경변수에서 API_KEY 읽기
api_key = os.getenv("API_KEY")

if not api_key:
    raise ValueError("API_KEY environment variable is not set.")

openai.api_key = api_key
client = OpenAI(api_key=api_key)
# ============================================================================
# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
# ============================================================================      
# 음식
class Food(BaseModel):
    foodName: str
    carbohydrates: int
    protein: int
    fat: int
    sodium: int

class Food_Reasponse(BaseModel):
    resp: list[Food]

# 알약
class Exist(BaseModel):
    guess: bool

# 숫자 - 혈당
class One_Digit_Reasponse(BaseModel):
    is_detected: bool
    digit: int

# 숫자 - 혈압
class Two_Digit_Reasponse(BaseModel):
    is_detected: bool
    sys: int  # 수축 : systolic blood pressure
    dia: int  # 이완 : diastolic blood pressure
# ============================================================================
dict_type = {
    "food" : ["What food is in this image? Answer only food with Korean!", Food_Reasponse],
    "peel" : ["Is there peels in this image?", Exist],
    "glucose" : ["What is the number in this glucometer image?", One_Digit_Reasponse],
    "sphygmomanometer" : ["What is the two numbers(sys, dia) in this sphygmomanometer image?", Two_Digit_Reasponse],
}
# ============================================================================
# 이미지 파일을 Vision API에 전달
def analyze_image(image_path, types):
  response = client.beta.chat.completions.parse(    
    model="gpt-4o-mini",
    messages=[
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": dict_type[types][0],
          },
          {
            "type": "image_url",
            "image_url": {
              "url":  f"data:image/jpeg;base64,{encode_image(image_path)}"
            },
          },
        ],
      }
    ],
    response_format=dict_type[types][1],
  )

  json_data = json.loads(response.choices[0].message.content)
  return json_data
# ============================================================================
# 음식 인식 AI 추론 결과를 반환하는 엔드포인트
@app.route('/api/food', methods=['POST'])
def is_food():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty file"}), 400

    try:
        image = Image.open(io.BytesIO(file.read()))

        # 이미지를 임시 저장
        temp_path = "temp_food_image.png"
        image.save(temp_path)

        description = analyze_image(temp_path, "food")

        # 임시 파일 삭제 (안전하게 처리)
        os.remove(temp_path)

        # guess 추가
        description["guess"] = int(len(description["resp"]) == 0)

        # 결과 반환
        return jsonify(description)
    except Exception as e:
        return jsonify({"error": f"Invalid image file: {str(e)}"}), 400
# ============================================================================
# 알약 인식 AI 추론 결과를 반환하는 엔드포인트
@app.route('/api/peel', methods=['POST'])
def peel_():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty file"}), 400

    try:
        image = Image.open(io.BytesIO(file.read()))

        # 이미지를 임시 저장
        temp_path = "temp_peel_image.png"
        image.save(temp_path)

        description = analyze_image(temp_path, "peel")

        # 임시 파일 삭제 (안전하게 처리)
        os.remove(temp_path)

        # guess -> int
        description["guess"] = 1-int(description["guess"])

        # 결과 반환
        return jsonify(description)
    except Exception as e:
        return jsonify({"error": f"Invalid image file: {str(e)}"}), 400
# ============================================================================
# 혈당계 숫자 인식 AI 추론 결과를 반환하는 엔드포인트
@app.route('/api/glucose_digit', methods=['POST'])
def glucose_digit_():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty file"}), 400

    try:
        image = Image.open(io.BytesIO(file.read()))

        # 이미지를 임시 저장
        temp_path = "temp_glucose_digit_image.png"
        image.save(temp_path)

        description = analyze_image(temp_path, "glucose")

        # 임시 파일 삭제 (안전하게 처리)
        os.remove(temp_path)
        
        # guess 추가
        description["guess"] = 1-int(description["is_detected"])
        
        # 결과 반환
        return jsonify(description)
    except Exception as e:
        return jsonify({"error": f"Invalid image file: {str(e)}"}), 400
# ============================================================================
# 혈압계 숫자 인식 AI 추론 결과를 반환하는 엔드포인트
@app.route('/api/sphygmomanometer_digit', methods=['POST'])
def sphygmomanometer_digit_():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty file"}), 400

    try:
        image = Image.open(io.BytesIO(file.read()))

        # 이미지를 임시 저장
        temp_path = "temp_sphygmomanometer_digit_image.png"
        image.save(temp_path)

        description = analyze_image(temp_path, "sphygmomanometer")

        # 임시 파일 삭제 (안전하게 처리)
        os.remove(temp_path)
        
        # guess 추가
        description["guess"] = 1-int(description["is_detected"])
        
        # 결과 반환
        return jsonify(description)
    except Exception as e:
        return jsonify({"error": f"Invalid image file: {str(e)}"}), 400
        
