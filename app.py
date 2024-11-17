from flask import Flask, render_template, request, jsonify
from PIL import Image
import io
import cv2
import numpy as np
import tensorflow as tf

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('./index.html')
    
@app.route("/test")
def test():
    return render_template('./index.html')

# GET 요청을 처리하는 간단한 엔드포인트
@app.route('/api/hello', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello, World!"})

# POST 요청을 처리하는 엔드포인트
@app.route('/api/echo', methods=['POST'])
def echo():
    data = request.json  # JSON 데이터를 받음
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    return jsonify({"received": data})

# 간단한 파라미터 처리
@app.route('/api/square/<int:number>', methods=['GET'])
def square(number):
    result = number ** 2
    return jsonify({"number": number, "square": result})

# 이미지 크기를 반환하는 엔드포인트
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

# def foodModel():
#     model = tf.keras.Sequential([
#                tf.keras.layers.ZeroPadding2D(padding=3, input_shape = (64,64,3)),
#                tf.keras.layers.Conv2D(64, (11,11), strides=1),
#                tf.keras.layers.BatchNormalization(axis = 3),
#                tf.keras.layers.ReLU(),
#                tf.keras.layers.MaxPool2D(),

#                tf.keras.layers.Conv2D(64, (2,2), strides=1),
#                tf.keras.layers.BatchNormalization(axis = 3),
#                tf.keras.layers.ReLU(),
#                tf.keras.layers.MaxPool2D(),


#                tf.keras.layers.Conv2D(64, (2,2), strides=1),
#                tf.keras.layers.BatchNormalization(axis = 3),
#                tf.keras.layers.ReLU(),
#                tf.keras.layers.MaxPool2D(),

#                tf.keras.layers.Flatten(),
#                tf.keras.layers.Dense(1, activation="sigmoid")
#     ])
#     return model

# food_model = foodModel()
# weights_path = "my_food_model(88_99).h5"
# food_model.load_weights(weights_path)

# # 음식 인식 AI 추론 결과를 반환하는 엔드포인트
# @app.route('/api/food', methods=['POST'])
# def is_food():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400
    
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "Empty file"}), 400

#     try:
#         image = Image.open(io.BytesIO(file.read()))
#         image_array = np.array(image)
#         image_array = cv2.resize(image_array, (64, 64))  # (64, 64, 3)
#         image_array = np.expand_dims(image_array, axis=0)  # (1, 64, 64, 3)
        
#         guess = food_model(image_array)
#         guess = round(float(guess[0][0])) # Food = 0 / Non-Food = 1
#         return jsonify({"guess": guess})
#     except Exception as e:
#         return jsonify({"error": f"Invalid image file: {str(e)}"}), 400
