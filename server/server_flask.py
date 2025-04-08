from flask import Flask, request, jsonify, render_template
import pymysql
import random
import requests

app = Flask(__name__, template_folder='templates')

host = 'localhost'
database = 'sleep'
username = 'root'
password = '12345'

try:
    conn = pymysql.connect(
        host=host,
        user=username,
        passwd=password,
        db=database,
        cursorclass=pymysql.cursors.DictCursor  # 데이터베이스 쿼리 결과를 딕셔너리 형태로 가져오도록 설정
    )
    cursor = conn.cursor()
    print("MySQL 연결 성공")

except pymysql.MySQLError as e:
    print(f"MySQL 오류 발생: {e}")
    conn = None

# 서버 페이지에서 화면 확인
@app.route('/')
def index():
    return render_template('data_display.html')


# MySQL --> 서버로 데이터 전송
# 아두이노에서 DR, FS, RT값 가져감
r_idx = None 

@app.route('/get_data', methods=['GET'])
def DB_to_server():
    global r_idx
    try:
        with conn.cursor() as cursor:
            if r_idx is None:
                r_idx = random.randint(0, 30)

            sql = f"SELECT `ID`, `D+R`, `FS`, `RT` FROM sleepStage WHERE idx = {r_idx}"

            cursor.execute(sql)
            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "해당 데이터 없음"}), 404

            return jsonify(result)

    except Exception as e:
        print(f"SQL 오류 발생: {e}")
        return jsonify({"error": str(e)}), 500


# 아두이노 --> 서버
sensor_data = {"temperature": -1, "humidity": -1, "light": -1}  # 초기값

@app.route('/sensor_data', methods=['POST'])
def receive_sensor_data():
    global sensor_data
    try:
        data = request.get_json()  # 아두이노한테서 센서값 JSON 데이터로 받기

        if not data or "sensorData" not in data:
            return jsonify({"error": "해당 데이터 없음"}), 400

        receive_data = data["sensorData"].split(" ")
        
        sensor_data = {
            "temperature": float(receive_data[0]),
            "humidity": float(receive_data[1]),
            "light": float(receive_data[2]),
        }

        print("sensor data:", sensor_data)

        return jsonify({"message": "센서 데이터 수신완료", "data": sensor_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 서버에 저장된 온습도, 조도값을 화면에 출력
@app.route('/get_sensor_data', methods=['GET'])
def display_sensor_data():
    global sensor_data
    return jsonify(sensor_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
