#include <SoftwareSerial.h>         // 시리얼 통신
#include <ESP8266WiFi.h>            // ESP8266 라이브러리
#include <ESP8266HTTPClient.h>      // ESP8266 <-> 서버 통신 라이브러리
#include <ArduinoJson.h>            // JSON 형태 사용 라이브러리

#define TX_PIN D6               // ESP8266 TX -> arduino 2
#define RX_PIN D7               // ESP8266 RX -> arduino 3

SoftwareSerial arduSerial(RX_PIN, TX_PIN); // 수신용

const char* ssid = "와이파이이름";                // Wi-Fi SSID
const char* password = "와이파이비번";          // Wi-Fi 비밀번호
const char* serverUrl_send = "http://localhost:8000/sensor_data";  // 센서 데이터 서버에 전송
const char* serverUrl_get = "http://localhost:8000/get_data";      // 서버에서 데이터 수신

// 초기화 함수
void setup() {
    Serial.begin(115200);
    arduSerial.begin(9600);
    
    WiFi.begin(ssid, password);

    // 와이파이 연결 확인
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("WiFi 연결 중...");
    }
    Serial.println("WiFi 연결 성공!");
}

void loop() {
    // 아두이노에서 전송된 센서 데이터
    if (arduSerial.available()) {
        String sensorData = arduSerial.readString();  
        sensorData.trim();                                  // 문자열 양쪽 공백 제거
        Serial.println("수신된 센서 데이터: " + sensorData);

        // 아두이노에서 받은 센서 데이터 서버 전송 함수
        toServer(sensorData);
    }

    // 서버에서 받은 데이터 아두이노 전송 함수
    fromServer();

    delay(5000);
}

// 센서 데이터 서버 전송
void toServer(String sensorData) {
    if (WiFi.status() == WL_CONNECTED) {
        WiFiClient client;      // 인터넷 통신
        HTTPClient http;        // HTTP 프로토콜

        http.begin(client, serverUrl_send);                  // 통신할 서버 설정
        http.addHeader("Content-Type", "application/json");  // JSON 형식 지정

        String jsonData = "{\"sensorData\": \"" + sensorData + "\"}";   // 전송할 데이터 JSON 형태로 변경
        
        int httpResponseCode = http.POST(jsonData);  // 서버에 데이터 전송

        if (httpResponseCode > 0) {
            String response = http.getString();
            Serial.println("서버 응답: " + response);
        } else {
            Serial.println("XXX POST 요청 실패 XXX");
        }

        http.end();         // 연결 종료

    } else {                // 예외처리
        Serial.println("XXX WiFi 연결 오류! XXX");
    }
}

// 서버에서 수신한 데이터 아두이노로 전송
void fromServer() {
    if (WiFi.status() == WL_CONNECTED) {
        WiFiClient client;
        HTTPClient http;

        http.begin(client, serverUrl_get);
        int httpResponseCode = http.GET();      // 서버에 데이터 요청

        if (httpResponseCode > 0) {
            String payload = http.getString();   // 서버로 받은 데이터(JSON 형태) 저장
            Serial.println("서버 응답 데이터:");
            Serial.println(payload);

            StaticJsonDocument<200> doc;
            DeserializationError error = deserializeJson(doc, payload);     // JSON 객체 변환

            // 파싱 실패 시
            if (error) {
                Serial.print("XXX JSON 파싱 실패: XXX");
                Serial.println(error.f_str());
                return;
            }

            // 파싱된 데이터 저장
            int DR = doc["D+R"];
            int FS = doc["FS"];
            int RT = doc["RT"].isNull() ? -1 : doc["RT"];

            Serial.println("파싱된 데이터:");
            Serial.print("D+R: "); Serial.println(DR);
            Serial.print("FS: "); Serial.println(FS);
            Serial.print("RT: "); Serial.println(RT);

            // 아두이노로 서버에서 받은 데이터 전송
            String dataToArduino = String(DR) + " " + String(FS) + " " + String(RT);
            arduSerial.println(dataToArduino);
            Serial.println("아두이노로 전송된 데이터: " + dataToArduino);
            
            delay(1000); // 안정적인 전송을 위해 딜레이 추가
        } else {
            Serial.println("XXX 서버 요청 실패 XXX");
        }

        http.end();      // 연결 종료
    } else {
        Serial.println("XXX WiFi 연결 오류! XXX");
    }
}
