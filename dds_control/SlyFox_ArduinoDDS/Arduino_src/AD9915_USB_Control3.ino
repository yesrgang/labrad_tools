/*
Arduino code to control AD9854

You can use the USB port on the Arduino to control AD9854.

Language: Arduino language.
Environment: Arduino 0021

Copyright (c) 2011 Yige Lin
Edited by Ben Bloom
Edited by Sara Campbell
Ver: 0.4
*/

#include <SPI.h>

#define SERIAL_IDLE 0
#define SERIAL_RECEIVING 1
#define DATA_NOT_READY 0
#define DATA_READY 1

#define pinMasterReset_0 12
#define pinIOReset_0 10
#define pinIOUpdate_0 11
#define pinCS_0 8


#define pinFSK_0 9

#define pinSS 1

int incomingByte;  // for incoming serial data
int checksumCalculated;  //calculated data checksum 
//unsigned long time;
byte checksumReceived;  //data checksum should be
byte serialStatus;  //idle or receiving
byte dataStatus;  //ready or not ready
byte serialInputCount; //how many bytes received
boolean DDScommand; // True if command sent was a DDS command that needs to be passed through
byte commandLength;
byte Command[20];
byte chiptoWrite;
byte i;

void setup() {
  serialStatus=SERIAL_IDLE;
  dataStatus=DATA_NOT_READY;
  Port_Init();
  Serial_Init();
  SPI_Init();
  DDS0_Init();
}

void loop() {
  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.read();
    if (incomingByte==':' && serialStatus==SERIAL_IDLE && dataStatus==DATA_NOT_READY) {\
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
        chiptoWrite=byte(incomingByte);
        serialInputCount++;
        checksumCalculated+=incomingByte;
      }
      else if(serialInputCount==1) {
        commandLength=byte(incomingByte) & 0x0f;
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
    }
    else{
      Serial.println("Checksum error!");
    }
    dataStatus=DATA_NOT_READY;
  }
    else if(dataStatus==DATA_READY){
      if (lowByte(checksumCalculated)==checksumReceived) {
        Serial.println("Roger that ArduinoCMD!");
        //Command Byte for Strobing FSK pin
        if (Command[0]==0x01) //the first command bit is the checksum for FSK signals
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
      }
      else{  
        Serial.println("NON-DDS Checksum error!");
      }
    }
    dataStatus=DATA_NOT_READY;
  }
}

void Master_Reset_0(void) {
  digitalWrite(pinMasterReset_0,LOW);
  delayMicroseconds(100);
  digitalWrite(pinMasterReset_0,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinMasterReset_0,LOW);
}

void IO_Update_0(void) {
  digitalWrite(pinIOUpdate_0,LOW);
  delayMicroseconds(100);
  digitalWrite(pinIOUpdate_0,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinIOUpdate_0,LOW);
}

void IO_Reset_0(void) {
  digitalWrite(pinIOReset_0,LOW);
  delayMicroseconds(100);
  digitalWrite(pinIOReset_0,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinIOReset_0,LOW);
}

void Serial_Init(void) {
  Serial.begin(9600);
}

void SPI_Init(void){
  SPI.setDataMode(MSBFIRST);
  SPI.setDataMode(SPI_MODE0);
  SPI.begin();
  SPI.setClockDivider(pinSS, 128);
}
 
void Port_Init(void) {
  pinMode(pinMasterReset_0, OUTPUT);
  pinMode(pinIOReset_0, OUTPUT);
  pinMode(pinIOUpdate_0, OUTPUT);
  pinMode(pinCS_0, OUTPUT);
  pinMode(pinFSK_0, INPUT);
  pinMode(pinSS, OUTPUT);
}

void DDS0_Init(void) {
  //reset ad9915
  IO_Reset_0();
  Master_Reset_0();
  //set parameters
  digitalWrite(pinCS_0,LOW);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x01);
  SPI.transfer(0x00);
  SPI.transfer(0x08);
  digitalWrite(pinCS_0,HIGH);
  //IO_Update_0();
  
  digitalWrite(pinCS_0,LOW);
  SPI.transfer(0x01);
  SPI.transfer(0x00);
  SPI.transfer(0x80);
  SPI.transfer(0x09);
  SPI.transfer(0x00);
  digitalWrite(pinCS_0,HIGH);
  //IO_Update_0();
  
  digitalWrite(pinCS_0,LOW);
  SPI.transfer(0x02);
  SPI.transfer(0x00);
  SPI.transfer(0x04);
  SPI.transfer(0x0C);
  SPI.transfer(0x1C);
  digitalWrite(pinCS_0,HIGH);
  //IO_Update_0();

  
  digitalWrite(pinCS_0,LOW);
  SPI.transfer(0x03); //all defaults why write?
  SPI.transfer(0x00);
  SPI.transfer(0x05);
  SPI.transfer(0x21);
  SPI.transfer(0x20);
  digitalWrite(pinCS_0,HIGH);
  //IO_Update_0();
  
  digitalWrite(pinCS_0,LOW);
  SPI.transfer(0x06); // ???
  SPI.transfer(0x90);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  digitalWrite(pinCS_0,HIGH);
  //IO_Update_0();
  
  digitalWrite(pinCS_0,LOW);
  SPI.transfer(0x07); // ???
  SPI.transfer(0x80);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  digitalWrite(pinCS_0,HIGH);
  //IO_Update_0();
  
  digitalWrite(pinCS_0,LOW);
  SPI.transfer(0x08); // ???
  SPI.transfer(0x80);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  digitalWrite(pinCS_0,HIGH);
  //IO_Update_0();
  
  digitalWrite(pinCS_0,LOW);
  SPI.transfer(0x0B);
  SPI.transfer(0x00); //output 200 kHz
  SPI.transfer(0x18);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  digitalWrite(pinCS_0,HIGH);
  //IO_Update_0();
  
  digitalWrite(pinCS_0,LOW);
  SPI.transfer(0x0C);
  SPI.transfer(0x00); //full amplitude
  SPI.transfer(0x00);
  SPI.transfer(0x00); //no phase offset
  SPI.transfer(0x00);
  digitalWrite(pinCS_0,HIGH);
  //IO_Update_0();
  
  digitalWrite(pinCS_0,LOW);
  SPI.transfer(0x1B); // ???
  SPI.transfer(0xA1);
  SPI.transfer(0x00);
  SPI.transfer(0x08);
  SPI.transfer(0x00);
  digitalWrite(pinCS_0,HIGH);
  //IO_Update_0();
  
  
  IO_Update_0();
}
