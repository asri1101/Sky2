#include <RadioHead.h>
#include <RH_ASK.h>

// ======== Radio (must match transmitter) ========
const uint16_t BITRATE = 1200;
#define RX_PIN 7
RH_ASK rf_driver(BITRATE, RX_PIN, -1, -1);

// ======== Motor driver pins (HW-95 / L298N style) ========
#define ENA 14   // PWM
#define IN1 10
#define IN2 11

#define ENB 15   // PWM
#define IN3 12
#define IN4 13

// ======== Failsafe ========
const uint32_t FAILSAFE_MS = 250;  // stop motors if no valid packet recently
uint32_t lastGood = 0;

static inline int clampInt(int v, int lo, int hi) {
  if (v < lo) return lo;
  if (v > hi) return hi;
  return v;
}

// Convert 0..255 (128 center) to signed -127..+127
int toSigned(uint8_t v) { return (int)v - 128; }

// Set one motor: speed -255..+255 (sign = direction)
void setMotorA(int speed) {
  speed = clampInt(speed, -255, 255);
  if (speed >= 0) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, speed);
  } else {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    analogWrite(ENA, -speed);
  }
}

void setMotorB(int speed) {
  speed = clampInt(speed, -255, 255);
  if (speed >= 0) {
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    analogWrite(ENB, speed);
  } else {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    analogWrite(ENB, -speed);
  }
}

void stopMotors() {
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
}

void setup() {
  Serial.begin(115200);
  delay(1200);
  Serial.println("=== RX: Pico + MX-RM-5V + HW-95 Motor Driver ===");

  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  stopMotors();

  if (!rf_driver.init()) Serial.println("❌ RF init failed (check DATA pin/power)");
  else                   Serial.println("✅ RF ready and listening");

  lastGood = millis();
}

void loop() {
  uint8_t buf[16];
  uint8_t len = sizeof(buf);

  if (rf_driver.recv(buf, &len)) {
    // Expect 7-byte packet
    if (len == 7 && buf[0] == 0xAB) {
      uint8_t chk = (uint8_t)((buf[0]+buf[1]+buf[2]+buf[3]+buf[4]+buf[5]) & 0xFF);
      if (chk == buf[6]) {
        lastGood = millis();

        uint8_t j1x_u = buf[1];
        uint8_t j1y_u = buf[2];
        uint8_t j2x_u = buf[3];
        uint8_t j2y_u = buf[4];
        uint8_t bmask = buf[5];

        // Tank mixing using J1 (you can change to J2 if you want)
        int x = toSigned(j1x_u);  // -127..127
        int y = toSigned(j1y_u);

        // Deadzone
        const int DZ = 12;
        if (abs(x) < DZ) x = 0;
        if (abs(y) < DZ) y = 0;

        // Mix: left = y + x, right = y - x
        // Scale from -127..127 to -255..255
        int left  = (y + x) * 2;
        int right = (y - x) * 2;

        left  = clampInt(left,  -255, 255);
        right = clampInt(right, -255, 255);

        setMotorA(left);
        setMotorB(right);

        // Debug ~5 Hz
        static uint32_t t0=0;
        if (millis() - t0 > 200) {
          Serial.print("RX J1("); Serial.print((int)j1x_u); Serial.print(","); Serial.print((int)j1y_u);
          Serial.print(") L:");   Serial.print(left);
          Serial.print(" R:");    Serial.print(right);
          Serial.print(" B:");    Serial.println(bmask, BIN);
          t0 = millis();
        }
      }
    }
  }

  // Failsafe stop
  if (millis() - lastGood > FAILSAFE_MS) {
    stopMotors();
  }
}
