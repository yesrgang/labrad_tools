/*
Arduino code to control AD9854

You can use the USB port on the Arduino to control AD9854.

Language: Arduino language.
Environment: Arduino 0021

Copyright (c) 2011 Framework by Yige Lin
Edited by Ben Bloom
06/22/12
Ver: 1.2
*/

#include <SPI.h>
#include <EEPROM.h>

#define SERIAL_IDLE 0
#define SERIAL_RECEIVING 1
#define DATA_NOT_READY 0
#define DATA_READY 1

#define pinMasterReset_0 9
#define pinIOReset_0 7
#define pinIOUpdate_0 8
#define pinCS_0 10

#define pinMasterReset_1 A1
#define pinIOReset_1 A3
#define pinIOUpdate_1 A2
#define pinCS_1 A0

#define pinFSK_0 5
#define pinFSK_1 6

#define pinNEWSEQUENCE 2
#define pinSTEPSEQUENCE 3

int incomingByte;  // for incoming serial data
int checksumCalculated;  //calculated data checksum 
byte checksumReceived;  //data checksum should be
byte serialStatus;  //idle or receiving
byte dataStatus;  //ready or not ready
byte serialInputCount; //how many bytes received
boolean DDScommand; // True if command sent was a DDS command that needs to be passed through
volatile int currentPhaseStepIndice = 0;

//boolean readyForPhaseStepping = false; // is used to determinte whether or not phase stepping should be tried
//byte phaseSteps[30];
//byte numPhaseSteps;

boolean readyForPhaseStepping = false; // is used to determinte whether or not phase stepping should be tried
byte phaseSteps[6] = {0x00, 0x00, 0x20, 0x00, 0x10, 0x00};

byte numPhaseSteps = 3;

byte commandLength;
byte Command[30];
byte chiptoWrite;
byte i;

byte defaultAmplitude0[2];//{0x0f, 0xff};
byte defaultFrequency0[6];// = {0x00, 0x00, 0x00, 0x40, 0x6C, 0xAD};

void setup() {
  defaultAmplitude0[0] = EEPROM.read(0);
  defaultAmplitude0[1] = EEPROM.read(1);
  for (int i = 0; i < 6; i++){
    defaultFrequency0[i] = EEPROM.read(i+2);
  }
  serialStatus=SERIAL_IDLE;
  dataStatus=DATA_NOT_READY;
  Port_Init();
  Serial_Init();
  SPI_Init();
  IO_Reset_0(); //necessary for continued communication after the program is closed and opened
  IO_Reset_1(); //necessary for continued communication after the program is closed and opened
  //DDS0_Init();
  //DDS1_Init();
  attachInterrupt(0, startPhaseStep, RISING);
  attachInterrupt(1, advancePhaseStep, FALLING);
}
void startPhaseStep() {
  if(readyForPhaseStepping){
    currentPhaseStepIndice = 0;
    writeNewPhase(currentPhaseStepIndice);
    currentPhaseStepIndice++;
  }
}
void advancePhaseStep() {
  if(readyForPhaseStepping){
    writeNewPhase(currentPhaseStepIndice);
    currentPhaseStepIndice++;
  }
}
void writeNewPhase(int idx)
{
  digitalWrite(pinCS_0,LOW);
  SPI.transfer(0x00);
  SPI.transfer(phaseSteps[2*idx]);
  SPI.transfer(phaseSteps[2*idx+1]);
  digitalWrite(pinCS_0,HIGH);
  IO_Update_0();
}
void loop() {
  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.read();
    if (incomingByte==':' && serialStatus==SERIAL_IDLE && dataStatus==DATA_NOT_READY) {
      DDScommand = true;
      serialInputCount=0;
      serialStatus=SERIAL_RECEIVING;
      checksumCalculated=0;
    }
    else if (incomingByte==';' && serialStatus==SERIAL_IDLE && dataStatus==DATA_NOT_READY) {
      DDScommand = false;
      serialInputCount=0;
      serialStatus=SERIAL_RECEIVING;
      checksumCalculated=0;
    }
    else if (serialStatus==SERIAL_RECEIVING){
      if (serialInputCount==0) {
        chiptoWrite=byte(incomingByte) & 0x01;
        serialInputCount++;
        checksumCalculated+=incomingByte;
      }
      else if(serialInputCount==1) {
        commandLength=byte(incomingByte);
        serialInputCount++;
        checksumCalculated+=incomingByte;
      }
      else if(serialInputCount==commandLength+2) {
        checksumReceived=byte(incomingByte);
        serialStatus=SERIAL_IDLE;
        dataStatus=DATA_READY;
      }
      else{
        Command[serialInputCount-2]=byte(incomingByte);
        serialInputCount++;
        checksumCalculated+=incomingByte;
      }
    }
  }  
  if (DDScommand && dataStatus==DATA_READY) {
    if (lowByte(checksumCalculated)==checksumReceived) {
      Serial.println("Roger that!");
      if (chiptoWrite==0) {
        digitalWrite(pinCS_0,LOW);
        for(i=0;i<commandLength;i++) {
          SPI.transfer(Command[i]);
        }
        IO_Update_0();
        digitalWrite(pinCS_0,HIGH);
      }
      else {
        digitalWrite(pinCS_1,LOW);
        for(i=0;i<commandLength;i++) {
          SPI.transfer(Command[i]);
        }
        IO_Update_1();
        digitalWrite(pinCS_1,HIGH);
      }
    }
    else{
      Serial.println("Checksum error!");
    }
  }
    else if(dataStatus==DATA_READY){ //i.e. if this is an arduino command instead
      if (lowByte(checksumCalculated)==checksumReceived) {
//          Serial.println("Roger that ArduinoCMD!");
          //Command Byte for Strobing FSK pin
          if (Command[0]==0x01)
          {
            if(chiptoWrite == 0)
            {
                pinMode(pinFSK_0, OUTPUT);
                if(Command[1] == 0x00)
                {
                  digitalWrite(pinFSK_0, LOW);
                }
                else
                {
                  digitalWrite(pinFSK_0, HIGH);
                }
            }
            else
            {
                pinMode(pinFSK_1, OUTPUT);
                if(Command[1] == 0x00)
                {
                  digitalWrite(pinFSK_1, LOW);
                }
                else
                {
                  digitalWrite(pinFSK_1, HIGH);
                }
            }
          }
          if (Command[0] == 'p') //loading a phase stepping sequence
          {
            numPhaseSteps = 0;
            readyForPhaseStepping = false;
            for(int j = 0; j < commandLength; j += 2)
            {
              phaseSteps[j] = Command[j+1];
              phaseSteps[j+1] = Command[j+2];
              numPhaseSteps++;
            }
            readyForPhaseStepping = true;
          }
        if (Command[0] == 'D') { //sets Defaults for each DDS....kinda simplistic, maybe need something more extensible for FSK and whatnot
          for(int j = 0; j < commandLength-1; j++)
          {
                  EEPROM.write(j,Command[j+1]);
          }
          Serial.println("Defaults written to EEPROM");
        }
        if (Command[0] == 'R') { //Reinitializes the DDS Board Selected
          if (chiptoWrite == 0)
          {
            DDS0_Init();
          }
          else {
            DDS1_Init();
          }
          String sOut = "";
          sOut = "DDS " + String(chiptoWrite, DEC) + " Reinitialized";
          Serial.println(sOut);
        }
      }
      else{  
        Serial.println("NON-DDS Checksum error!");
      }
    }
    dataStatus=DATA_NOT_READY;
  }

void Master_Reset_0(void) {
  digitalWrite(pinMasterReset_0,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinMasterReset_0,LOW);
}

void Master_Reset_1(void) {
  digitalWrite(pinMasterReset_1,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinMasterReset_1,LOW);
}

void IO_Update_0(void) {
  digitalWrite(pinIOUpdate_0,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinIOUpdate_0,LOW);
}

void IO_Update_1(void) {
  digitalWrite(pinIOUpdate_1,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinIOUpdate_1,LOW);
}

void IO_Reset_0(void) {
  digitalWrite(pinIOReset_0,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinIOReset_0,LOW);
}

void IO_Reset_1(void) {
  digitalWrite(pinIOReset_1,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinIOReset_1,LOW);
}

void Serial_Init(void) {
  Serial.begin(9600);
}

void SPI_Init(void){
  SPI.setDataMode(MSBFIRST);
  SPI.setDataMode(SPI_MODE0);
  SPI.setClockDivider(SPI_CLOCK_DIV2);
  SPI.begin();
}

void Port_Init(void) {
  pinMode(pinMasterReset_0, OUTPUT);
  pinMode(pinIOReset_0, OUTPUT);
  pinMode(pinCS_0, OUTPUT);
  pinMode(pinIOUpdate_0, OUTPUT);
  
  pinMode(pinMasterReset_1, OUTPUT);
  pinMode(pinIOReset_1, OUTPUT);
  pinMode(pinCS_1, OUTPUT);
  pinMode(pinIOUpdate_1, OUTPUT);
  
  pinMode(pinFSK_0, OUTPUT);
  pinMode(pinFSK_1, OUTPUT);
  
  pinMode(pinNEWSEQUENCE, INPUT);
  pinMode(pinSTEPSEQUENCE, INPUT);
}

void DDS0_Init(void) {
  //reset ad9854
  Master_Reset_0();
  //set parameters
  pinMode(pinIOUpdate_0, INPUT);
  digitalWrite(pinCS_0,LOW);
  SPI.transfer(0x07);
  delayMicroseconds(10);
  SPI.transfer(0x10);
  delayMicroseconds(10);
  SPI.transfer(0x14);
  delayMicroseconds(10);
  SPI.transfer(0x00);
  delayMicroseconds(10);
  SPI.transfer(0x21);
  delayMicroseconds(10);
  digitalWrite(pinCS_0,HIGH);
  pinMode(pinIOUpdate_0, OUTPUT);
  IO_Update_0();
  
  //set amplitude
  digitalWrite(pinCS_0,LOW);
  SPI.transfer(0x08);
  SPI.transfer(defaultAmplitude0[0]);
  SPI.transfer(defaultAmplitude0[1]);
  digitalWrite(pinCS_0,HIGH);
  IO_Update_0();
  //set frequency
  digitalWrite(pinCS_0,LOW);
  SPI.transfer(0x02);
  SPI.transfer(defaultFrequency0[0]);
  SPI.transfer(defaultFrequency0[1]);
  SPI.transfer(defaultFrequency0[2]);
  SPI.transfer(defaultFrequency0[3]);
  SPI.transfer(defaultFrequency0[4]);
  SPI.transfer(defaultFrequency0[5]);
  digitalWrite(pinCS_0,HIGH);
  IO_Update_0();
}

void DDS1_Init(void) {
  //reset ad9854
  Master_Reset_1();
  //set parameters
  pinMode(pinIOUpdate_1, INPUT);
  digitalWrite(pinCS_1,LOW);
  SPI.transfer(0x07);
  delayMicroseconds(10);
  SPI.transfer(0x10);
  delayMicroseconds(10);
  SPI.transfer(0x14);
  delayMicroseconds(10);
  SPI.transfer(0x00);
  delayMicroseconds(10);
  SPI.transfer(0x21);
  delayMicroseconds(10);
  digitalWrite(pinCS_1,HIGH);
  pinMode(pinIOUpdate_1, OUTPUT);
  IO_Update_1();

  //set amplitude
  digitalWrite(pinCS_1,LOW);
  SPI.transfer(0x08);
  SPI.transfer(0x0f);
  SPI.transfer(0xff);
  digitalWrite(pinCS_1,HIGH);
  IO_Update_1();
  //set frequency
  digitalWrite(pinCS_1,LOW);
  SPI.transfer(0x02);
  SPI.transfer(0x80);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  digitalWrite(pinCS_1,HIGH);
  IO_Update_1();
}
