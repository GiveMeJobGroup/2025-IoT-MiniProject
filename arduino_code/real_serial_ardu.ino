#include "DHT.h"                  // 온습도 센서
#include <LiquidCrystal_I2C.h>    // LCD 
#include <SoftwareSerial.h>       // 시리얼 통신

#define DHTTYPE DHT11             // 온습도 센서
#define TX 3 // arduino 3 -> ESP8266 RX
#define RX 2 // arduino 2 -> ESP8266 TX

SoftwareSerial nodeSerial(RX, TX); // 시리얼 통신


#define C 262 // 도 
#define D 294 // 레 
#define E 330 // 미 
#define F 349 // 파 
#define G 392 // 솔 
#define A 440 // 라 
#define B 494 // 시 

// LED
int RED = 9;
int GREEN = 10;
int BLUE = 11;

// 부저
int buzzer = 13;

// 알람
int tempo[] = {200, 300, 200, 300, 200, 300, 200, 300, 200, 300, 200, 300, 200, 300, 200, 300, 200, 300, 200, 300, 200, 300, 200, 300}; // duration 옵션 값 설정 
int notes[] = { G, G, A, A, G, G, E, G, G, E, E, D, G, G, A, A, G, G, E, G, E, D, E, C };

// 자장가
int melody[] = {262, 330, 392, 523, 392, 330, 262}; // 도, 미, 솔, 높은 도, 솔, 미, 도
int noteDurations[] = {1000, 1200, 1400, 1600, 1400, 1200, 1000};

// 온습도센서
int DTH = A1;
DHT dht(DTH, DHTTYPE); 

// LCD객체 생성
LiquidCrystal_I2C lcd(0x27,20,4);  

// 초기화 함수
void setup()
{
  Serial.begin(115200);         // 시리얼 모니터
  nodeSerial.begin(9600);       // ESP8266 모듈 수신 속도

  // LED 출력 설정
  pinMode(RED, OUTPUT);     
  pinMode(GREEN, OUTPUT);
  pinMode(BLUE, OUTPUT);

  // 부저 출력 설정
  pinMode(buzzer, OUTPUT);  

  // DHT 센서 초기화
  dht.begin();              

  // lcd 초기화 
  lcd.init();
  lcd.backlight();  
}
  
void loop()
{
  // 조도, 온도, 습도
  int lux = analogRead(A0);
  float temperature = dht.readTemperature();  
  float humidity = dht.readHumidity(); 
   
  // 센서 데이터 ESP8266으로 전송
  char info[20] = {};
  snprintf(info, sizeof(info), "%d %d %d", (int)temperature, (int)humidity, lux);
  nodeSerial.print(info);
  Serial.print("ESP8266으로 전송된 센서 데이터: ");
  Serial.println(info);

  // ESP8266에서 데이터 수신
  // DR: Deep+Rem, FS: 6이상 수면, RT: 수면 설정 시간 - (DR&FS -> 1 충족시간)
  int DR = 0, FS = 0, RT = 0; 
  String receivedData = "";

  if(nodeSerial.available()) {
    String getInfo = nodeSerial.readString();
    getInfo.trim();
    Serial.println("ESP8266에서 수신된 수면 데이터: " + getInfo);
    sscanf(getInfo.c_str(), "%d %d %d", &DR, &FS, &RT);
  }
  
  // LCD 제어
  char lcdPrint[20] = {};
  snprintf(lcdPrint, sizeof(lcdPrint), "Temp:%dC RH:%d%%", (int)temperature, (int)humidity);

  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print(lcdPrint);

  if ((DR == 1)&&(FS == 1)){
    lcd.setCursor(2,1);
    lcd.print("wake up");

    //서서히 밝아지게
    for(int bright=0;bright<=255;bright++){
      analogWrite(RED, bright);
      analogWrite(GREEN, bright);
      analogWrite(BLUE, bright);
      // 실제로 구현시 delay(RT/255) 를 해야하나 실제로 보기 위해서 밑에 임의의 값을 사용함.
      delay(100);

      // 알람 (깨우는 용도)
      if (bright == 255){
          for (int i = 0; i < 12; i++) { 
            tone (buzzer, notes[ i ], tempo[ i ]); 
            delay (tempo[ i ]); 
          } 
          delay(100); // 멜로디 중간에 짧게 멈추는 용도 

          for (int i = 12; i < 25; i++) { 
            tone (buzzer, notes[ i ], tempo[ i ]); 
            delay(tempo[ i ]); 
          } 
      }
    }
  }

  else if ((DR == 1)&&(FS == 0)){
    lowLight();

    lcd.setCursor(2,1);
    lcd.print("more sleep");    
  }

  else if ((DR == 0)&&(FS == 1)){
    lowLight();

    lcd.setCursor(0,1);
    lcd.print("control Temp, RH");   

    playSleepSong();
  }

  else if ((DR == 0)&&(FS == 0)){
    lowLight();

    lcd.setCursor(0,1);
    lcd.print("cool Temp");  

    // 자장가
    playSleepSong();
  }
  delay(5000);
}

// 자장가 출력 기능
void playSleepSong() {
  for (int i = 0; i < 7; i++) {
    tone(buzzer, melody[i]);
    delay(noteDurations[i]);
    noTone(buzzer);
    delay(300);
  }
}

// LED 종료 기능
void lowLight(){
    analogWrite(RED, LOW);
    analogWrite(GREEN, LOW);
    analogWrite(BLUE, LOW);
}
