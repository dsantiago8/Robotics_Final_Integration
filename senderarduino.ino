#include <Servo.h>


Servo servoX;
Servo servoY;


int posX = 90;  // starting angle
int posY = 90;


void setup() {
 Serial.begin(9600);
 servoX.attach(9);  // X-axis servo on pin 9
 servoY.attach(10); // Y-axis servo on pin 10


 servoX.write(posX);
 servoY.write(posY);
 delay(300);
}


void loop() {
 if (Serial.available()) {
   String input = Serial.readStringUntil('\n');
   input.trim(); // remove any whitespace


   // Parse format: "X:angle" or "Y:angle"
   if (input.startsWith("X:")) {
     int angle = input.substring(2).toInt();
     moveServoSmooth(servoX, posX, angle);
     posX = angle;
   } else if (input.startsWith("Y:")) {
     int angle = input.substring(2).toInt();
     moveServoSmooth(servoY, posY, angle);
     posY = angle;
   }
 }
}


// Smooth motion function
void moveServoSmooth(Servo &servo, int from, int to) {
 int step = (to > from) ? 1 : -1;
 for (int i = from; i != to; i += step) {
   servo.write(i);
   delay(10);  // smaller delay = smoother, but slower
 }
 servo.write(to); // final write to ensure accuracy
}
