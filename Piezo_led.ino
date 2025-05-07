const int piezoPin = 8;
const int ledPins[] = {2, 3, 4, 5};

void setup() {
  Serial.begin(9600);

  pinMode(piezoPin, OUTPUT);

  for (int i = 0; i < 4; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
  }

  Serial.println("[Receiver] Ready");
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.equalsIgnoreCase("go")) {
      Serial.println("[Receiver] 'go' received. Triggering mechanism.");
      playCountdown();
    }
  }
}

void playCountdown() {
  int tones[] = {880, 880, 880, 1319};
  int durations[] = {400, 400, 400, 800};

  for (int i = 0; i < 4; i++) {
    digitalWrite(ledPins[i], HIGH);
    tone(piezoPin, tones[i]);
    delay(durations[i]);
    noTone(piezoPin);
    digitalWrite(ledPins[i], LOW);
    delay(600);
  }

  Serial.println("[Receiver] Countdown complete.");
}
