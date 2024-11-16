from flask import Flask, render_template, request, jsonify

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
