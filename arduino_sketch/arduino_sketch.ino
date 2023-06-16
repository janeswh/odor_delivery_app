/* Written by Beichen Liu for Dr. Claire Cheetham's Lab
 *  Uses millis() to keep track of time for odor release and delay times
 *  1000 ms = 1s
 */

int triggerTime = 400; //how long you've set the Arduino to receive a trigger and how long the arduino waits for it -- for timing purposes only

// Initiate the solenoid pins, with offsets of 1 because pins 0 and 1 cannot be used
const int analogInPin = 15; //set up digital input on pin 14
const int solenoidPin1 = 2;
const int solenoidPin2 = 3;
const int solenoidPin3 = 4;
const int solenoidPin4 = 5;
const int solenoidPin5 = 6;
const int solenoidPin6 = 7;
const int solenoidPin7 = 8;
const int solenoidPin8 = 9;
// Initiate the output trigger for the microscope
const int microscopeTrigger = 10;

//Receive trigger from microscope
int ardTrigger = 0; //0=false, 1=true
int receivedSignal = 0; //1 = triggered
int signalTimes = 0; //counts signaltimes

// set the delay between triggering the microscope and starting the first odor so that the changes in fluorescence can be seen
int delayMicroscopeTrigger = 0; //4 seconds between microscope trigger and the start of the first odor (Changed to 0- delay in thorimage)


int odorSec = 0;
int delaySec = 0;

// set the variables to hold the length of the odor release, and the amount of delay before the next odor, as well as which pin to set/odor
int pinSet = 0;
long odorTime = 0;
long delayTime = 0;

// check if the first odor has been set and if the delayMicroscopeTrigger has been implemented
int odorAlready = 0; //0=false, 1=true
int delayAlready = 0; //0=false, 1=true
int delayedFirstOdor = 0; //if the ttl signal has been sent to the microscope
int microscopeTriggerAlready = 0; //0=false, 1=true

//keeps track of the timing using millis()
unsigned long startMillis = 0;
unsigned long currentMillis = 0;

void setup() {
  pinMode(solenoidPin1, OUTPUT); //set pins for output or input
  pinMode(solenoidPin2, OUTPUT);
  pinMode(solenoidPin3, OUTPUT);
  pinMode(solenoidPin4, OUTPUT);
  pinMode(solenoidPin5, OUTPUT);
  pinMode(solenoidPin6, OUTPUT);
  pinMode(solenoidPin7, OUTPUT);
  pinMode(solenoidPin8, OUTPUT);
  pinMode(microscopeTrigger, OUTPUT);

  //start the serial with a baud rate of 9600--higher amounts receive data faster, but can cause back-up in the queue, so stick with 9600!
  Serial.begin(9600);
}


//reset the variables after each trial set of running odors
void resetFunction(){
  pinSet = 0;
  odorTime = 0;
  delayTime = 0;
  odorSec = 0;
  delaySec = 0;
  pinSet = 0;
  odorTime = 0;
  delayTime = 0;
  odorAlready = 0; //0=false, 1=true
  delayAlready = 0; //0=false, 1=true
  delayedFirstOdor = 0; //if the ttl signal has been sent to the microscope
  microscopeTriggerAlready = 0; //0=false, 1=true
  startMillis = 0;
  currentMillis = 0;

}

//4s delay after the microscope has been triggered to establish the baseline
void delayMillis(){
  //if (delayedFirstOdor == 1){
  currentMillis = millis(); //get the millis() value
  startMillis = currentMillis; //set the millis() value and subtract this from each millis() to get an elapsed time value
  while (microscopeTriggerAlready == 0){
    currentMillis = millis();
    if (currentMillis-startMillis >= delayMicroscopeTrigger){
      microscopeTriggerAlready += 1;
    }
  }
  microscopeTriggerAlready = 0;
  //} 
}

//Turns the odor on for a specified time
void odorOn(){ //turns on the solenoid for an odor
  currentMillis = millis();
  startMillis = currentMillis;
  //digitalWrite(pinSet, HIGH); //delete this line or the other line
  while (odorAlready == 0){ //if the odor has not been turned on
    currentMillis = millis();
    //Serial.println(odorTime); //delete this
    digitalWrite(pinSet, HIGH); //turn the odor pin on to deliver odor
    //Serial.println(currentMillis-startMillis); //delete this
    if (currentMillis-startMillis >= odorTime){ //check to see if enough time has elapsed
      digitalWrite(pinSet, LOW); //if yet, then turn off the pin and indicate the the odor was turned on
      odorAlready = 1;
    }
  }
  odorAlready = 0; //reset odorAlready for the next odor
}

//keeps track of the delay between odors (4 seconds before the first odor and a set delay afterwards
void delayOn() {//delay between odors
  currentMillis = millis();
  startMillis = currentMillis;
  while (delayAlready == 0){
    currentMillis = millis();
    //Serial.println(currentMillis-startMillis);
    if (currentMillis-startMillis >= delayTime){
      delayAlready = 1;
    }
  }
  delayAlready = 0;
}

void checkTrigger() {
  ardTrigger = 0; //reset checkTrigger -- should wait for a trigger before each odor delivery
  if (ardTrigger == 0){
    while (ardTrigger == 0){
      delay(50); //100 ms delay between reading trigger
      receivedSignal = digitalRead(analogInPin);
      //Serial.println("current signal = ");
      //Serial.print(receivedSignal);
      if (receivedSignal == 1){
        //Serial.println("GETTING SIGNAL");
        if (signalTimes <3){
          signalTimes += 1; //add to counter
          //Serial.print(signalTimes);
        }
        else if (signalTimes >= 3){
          //Serial.print(signalTimes);
          //Serial.println("done with triggering");
          ardTrigger = 1;
        }
      }
      else if (receivedSignal == 0){
        signalTimes = 0;
      }
    }
  }
}

void newcheckTrigger() {
  ardTrigger = 0; //reset checkTrigger -- should wait for a trigger before each odor delivery
  if (ardTrigger == 0){
    while (ardTrigger == 0){
      delay(50); //100 ms delay between reading trigger
      Serial.println("no scope signal");
      receivedSignal = digitalRead(analogInPin);

     
      if (receivedSignal == 1){
          ardTrigger = 1;
          Serial.println("scope signal received");
        }
      }

      }
    }

//executes the solenoid order
void executeSolenoids() {
  if (Serial.available()>1){ //check if there is input available
    pinSet = Serial.parseInt()+1; //get the pin to output
    odorSec = Serial.parseInt();
    delaySec = Serial.parseInt()-1;
    //Serial.println(pinSet); //remove
    //Serial.println(odorSec); //remove
    //Serial.println(delaySec);//remove
    odorTime = (odorSec)*1000L; //convert seconds to milliseconds, L after 1000 to indicate unsigned long and needed for delays longer than 30s because of the way arduino handles numbers in 8-bit
    //Serial.println(odorTime);
    delayTime = (delaySec)*1000L-(delayMicroscopeTrigger+100)-triggerTime; //convert to milliseconds, but subtract the time it needs to trigger the microscope (100 milliseconds) and establish the baseline (4000ms)
    //Serial.println(delayTime);
    //Python sends two scenarios: 0,0,0 which signals end of a procedure, and #,#,#, which is a sequence to be executed
    
    //if(pinSet == 1 && odorTime == 0 && delayTime == 0){ //added 1 to pinSet = 0, so it should be 1 now
      //if python sends (1,0,0), this signals the end of the sequence      
      //resetFunction();
    //}
    //deleted else if
    if (pinSet > 1){
      //delayedFirstOdor += 1;
      //Serial.println(delayedFirstOdor);
      newcheckTrigger(); //wait for microscope trigger
      Serial.println("9"); //tells python when the microscope has been triggered
      digitalWrite(microscopeTrigger, HIGH); //trigger the microscope
      delay(100);
      digitalWrite(microscopeTrigger, LOW); 
      delayMillis(); //wait 4 seconds after the microscope has been triggered to establish baseline
      Serial.println("1"); //tells python the odor has been released
      odorOn(); //releases the odor for a certain time
      Serial.println("2"); //tells python the odor has been stopped
      delayOn(); //delay occurs after the odor
      Serial.println("3"); //tells python the delay has been finished, to send the next set of numbers
    }
  }
  else {
    ardTrigger = 0;
  }
}


void loop() {
  // put your main code here, to run repeatedly:
  delay(50);
  Serial.println("y"); //tells python that the arduino is connected and running
  executeSolenoids(); //run the code
}
