#include <WiFi.h>
#include <HTTPClient.h>
#include <TinyGPSPlus.h>
#include <HardwareSerial.h>

// ========== CHANGE THESE ==========
const char* WIFI_SSID = "sakib";
const char* WIFI_PASS = "password";

// Put your PC IPv4 here (example: 192.168.0.10)
const char* BASE_URL  = "http://10.169.116.105:8000";
// ==================================

// Must match what you created in backend
const char* DEVICE_ID  = "device-001";
const char* DEVICE_KEY = "device001";

// Pins (based on your setup)
#define GPS_RX 16
#define GPS_TX 17
#define SOS_PIN 27

TinyGPSPlus gps;
HardwareSerial GPSSerial(2);

// Send interval
unsigned long lastSendMs = 0;
const unsigned long SEND_INTERVAL_MS = 5000;

// SOS debounce
volatile bool sosEvent = false;
volatile unsigned long lastPressMs = 0;
const unsigned long DEBOUNCE_MS = 800;

void IRAM_ATTR onSosPress() {
  unsigned long now = millis();
  if (now - lastPressMs > DEBOUNCE_MS) {
    sosEvent = true;
    lastPressMs = now;
  }
}

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  Serial.print("Connecting WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi connected");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());
}

bool postJson(const String& url, const String& jsonBody) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️ WiFi disconnected. Reconnecting...");
    connectWiFi();
  }

  Serial.println("----- SENDING TO BACKEND -----");
  Serial.print("URL: ");
  Serial.println(url);
  Serial.print("JSON: ");
  Serial.println(jsonBody);

  HTTPClient http;
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Key", DEVICE_KEY);

  int code = http.POST(jsonBody);
  String resp = http.getString();
  http.end();

  Serial.print("HTTP Code: ");
  Serial.println(code);
  Serial.print("Backend Response: ");
  Serial.println(resp);
  Serial.println("------------------------------");

  return code >= 200 && code < 300;
}

void sendLive(double lat, double lng) {
  String url = String(BASE_URL) + "/devices/" + DEVICE_ID + "/location";
  String body = "{";
  body += "\"lat\":" + String(lat, 6) + ",";
  body += "\"lng\":" + String(lng, 6) + ",";
  body += "\"timestamp\":" + String((unsigned long)(millis() / 1000));
  body += "}";

  postJson(url, body);
}

void sendSos(double lat, double lng) {
  String url = String(BASE_URL) + "/devices/" + DEVICE_ID + "/sos";
  String body = "{";
  body += "\"lat\":" + String(lat, 6) + ",";
  body += "\"lng\":" + String(lng, 6) + ",";
  body += "\"timestamp\":" + String((unsigned long)(millis() / 1000));
  body += "}";

  postJson(url, body);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Button
  pinMode(SOS_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(SOS_PIN), onSosPress, FALLING);

  // GPS UART2
  GPSSerial.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);

  // WiFi
  connectWiFi();

  Serial.println("✅ ESP32 GPS + SOS + REST API READY");
}

void loop() {
  // Read GPS stream
  while (GPSSerial.available()) {
    gps.encode(GPSSerial.read());
  }

  bool hasFix = gps.location.isValid();
  double lat = hasFix ? gps.location.lat() : 0.0;
  double lng = hasFix ? gps.location.lng() : 0.0;

  unsigned long now = millis();

  // LIVE every 5 seconds (only if fix)
  if (now - lastSendMs >= SEND_INTERVAL_MS) {
    lastSendMs = now;

    if (hasFix) {
      Serial.print("LIVE | Lat: ");
      Serial.print(lat, 6);
      Serial.print(" | Lng: ");
      Serial.println(lng, 6);

      sendLive(lat, lng);
    } else {
      Serial.println("LIVE | NO FIX (not sending)");
    }
  }

  // SOS immediate
  if (sosEvent) {
    sosEvent = false;

    Serial.print("🚨 DANGER (SOS) | Lat: ");
    Serial.print(lat, 6);
    Serial.print(" | Lng: ");
    Serial.println(lng, 6);

    sendSos(lat, lng);
  }

  delay(10);
}
