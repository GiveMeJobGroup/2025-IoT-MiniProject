from flask import Flask, request, jsonify, render_template
import pymysql
import random
import requests

app = Flask(__name__, template_folder='templates')

# MySQL 연결 정보
host = 'localhost'
database = 'sleep'
username = 'root'
password = '12345'

# MySQL 연결
try:
    conn = pymysql.connect(
        host=host,
        user=username,
        passwd=password,
        db=database,
        cursorclass=pymysql.cursors.DictCursor  # 딕셔너리 형태로 결과 반환
    )
    cursor = conn.cursor()
    print("✅ MySQL 연결 성공!")

except pymysql.MySQLError as e:
    print(f"MySQL 오류 발생: {e}")
    conn = None


# HTML 페이지 렌더링
@app.route('/')
def index():
    return render_template('data_display.html')


# MySQL -> 서버로 전송 // 아두이노에서 가져감
r_idx = None  # 한 번 정한 r_idx를 유지하도록 글로벌 변수 사용

@app.route('/get_data', methods=['GET'])
def get_fixed_random_data():
    global r_idx
    try:
        with conn.cursor() as cursor:
            if r_idx is None:  # 계속 아두이노로 값 랜덤하게 보내기 방지용
                r_idx = random.randint(0, 30)

            sql = f"SELECT `ID`, `D+R`, `FS`, `RT` FROM sleepStage WHERE idx = {r_idx}"

            cursor.execute(sql)
            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "No matching data found"}), 404

            return jsonify(result)

    except Exception as e:
        print(f"SQL 오류 발생: {e}")
        return jsonify({"error": str(e)}), 500


# 아두이노 -> 서버 (POST)
sensor_data = {"temperature": -1, "humidity": -1, "light": -1}  # 초기값

@app.route('/sensor_data', methods=['POST'])
def receive_sensor_data():
    global sensor_data
    try:
        data = request.get_json()  # 아두이노 한테서 JSON 데이터 받기

        if not data or "sensorData" not in data:
            return jsonify({"error": "Invalid data format"}), 400

        receive_data = data["sensorData"].split(" ")
        
        sensor_data = {
            "temperature": float(receive_data[0]),
            "humidity": float(receive_data[1]),
            "light": float(receive_data[2]),
        }

        print(" Parsed sensor data:", sensor_data)

        return jsonify({"message": "Sensor data received!", "data": sensor_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 서버에 저장된 값을 화면에 출력
@app.route('/get_sensor_data', methods=['GET'])
def send_sensor_data():
    global sensor_data
    return jsonify(sensor_data)  # Flask에서 저장된 센서 데이터를 반환


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
