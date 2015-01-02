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

#define pinMasterReset_0 48
#define pinIOReset_0 42
#define pinIOUpdate_0 44
#define pinCS_0 46

#define pinMasterReset_1 40
#define pinIOReset_1 34
#define pinIOUpdate_1 36
#define pinCS_1 38

#define pinMasterReset_2 32
#define pinIOReset_2 26
#define pinIOUpdate_2 28
#define pinCS_2 30

#define pinMasterReset_3 37
#define pinIOReset_3 31
#define pinIOUpdate_3 33
#define pinCS_3 35

#define pinMasterReset_4 17
#define pinIOReset_4 14
#define pinIOUpdate_4 15
#define pinCS_4 16

#define pinMasterReset_5 21
#define pinIOReset_5 18
#define pinIOUpdate_5 19
#define pinCS_5 20

#define pinFSK_0 49
#define pinFSK_1 47
#define pinFSK_2 45
#define pinFSK_3 43
#define pinFSK_4 41
#define pinFSK_5 39


#define pinSS 53

int incomingByte;  // for incoming serial data
int checksumCalculated;  //calculated data checksum 
unsigned long time;
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
  DDS1_Init();
  DDS2_Init();
  DDS3_Init();
  DDS4_Init();
  DDS5_Init();
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
      if (chiptoWrite==1) {
        digitalWrite(pinCS_1,LOW);
        for(i=0;i<commandLength;i++) {
          SPI.transfer(Command[i]);
        }
        IO_Update_1();
        digitalWrite(pinCS_1,HIGH);
      }
            if (chiptoWrite==2) {
        digitalWrite(pinCS_2,LOW);
        for(i=0;i<commandLength;i++) {
          SPI.transfer(Command[i]);
        }
        IO_Update_2();
        digitalWrite(pinCS_2,HIGH);
      }
            if (chiptoWrite==3) {
        digitalWrite(pinCS_3,LOW);
        for(i=0;i<commandLength;i++) {
          SPI.transfer(Command[i]);
        }
        IO_Update_3();
        digitalWrite(pinCS_3,HIGH);
      }
            if (chiptoWrite==4) {
        digitalWrite(pinCS_4,LOW);
        for(i=0;i<commandLength;i++) {
          SPI.transfer(Command[i]);
        }
        IO_Update_4();
        digitalWrite(pinCS_4,HIGH);
      }
            if (chiptoWrite==5) {
        digitalWrite(pinCS_5,LOW);
        for(i=0;i<commandLength;i++) {
          SPI.transfer(Command[i]);
        }
        IO_Update_5();
        digitalWrite(pinCS_5,HIGH);
      }
    }
    else{
      Serial.println("Checksum error!");
    }
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
          if(chiptoWrite == 1)
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
          if(chiptoWrite == 2)
          {
              pinMode(pinFSK_2, OUTPUT);
              if(Command[1] == 0x00)
              {
                digitalWrite(pinFSK_2, LOW);
              }
              else
              {
                digitalWrite(pinFSK_2, HIGH);
              }
          }
          if(chiptoWrite == 3)
          {
              pinMode(pinFSK_3, OUTPUT);
              if(Command[1] == 0x00)
              {
                digitalWrite(pinFSK_3, LOW);
              }
              else
              {
                digitalWrite(pinFSK_3, HIGH);
              }
          }
         if(chiptoWrite == 4)
          {
              pinMode(pinFSK_4, OUTPUT);
              if(Command[1] == 0x00)
              {
                digitalWrite(pinFSK_4, LOW);
              }
              else
              {
                digitalWrite(pinFSK_4, HIGH);
              }
          }
         if(chiptoWrite == 5)
          {
              pinMode(pinFSK_5, OUTPUT);
              if(Command[1] == 0x00)
              {
                digitalWrite(pinFSK_5, LOW);
              }
              else
              {
                digitalWrite(pinFSK_5, HIGH);
              }
          }
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

void Master_Reset_2(void) {
  digitalWrite(pinMasterReset_2,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinMasterReset_2,LOW);
}

void Master_Reset_3(void) {
  digitalWrite(pinMasterReset_3,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinMasterReset_3,LOW);
}

void Master_Reset_4(void) {
  digitalWrite(pinMasterReset_4,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinMasterReset_4,LOW);
}

void Master_Reset_5(void) {
  digitalWrite(pinMasterReset_5,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinMasterReset_5,LOW);
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

void IO_Update_2(void) {
  digitalWrite(pinIOUpdate_2,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinIOUpdate_2,LOW);
}

void IO_Update_3(void) {
  digitalWrite(pinIOUpdate_3,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinIOUpdate_3,LOW);
}

void IO_Update_4(void) {
  digitalWrite(pinIOUpdate_4,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinIOUpdate_4,LOW);
}

void IO_Update_5(void) {
  digitalWrite(pinIOUpdate_5,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinIOUpdate_5,LOW);
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

void IO_Reset_2(void) {
  digitalWrite(pinIOReset_2,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinIOReset_2,LOW);
}

void IO_Reset_3(void) {
  digitalWrite(pinIOReset_3,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinIOReset_3,LOW);
}

void IO_Reset_4(void) {
  digitalWrite(pinIOReset_4,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinIOReset_4,LOW);
}

void IO_Reset_5(void) {
  digitalWrite(pinIOReset_5,HIGH);
  delayMicroseconds(100);
  digitalWrite(pinIOReset_5,LOW);
}


void Serial_Init(void) {
  Serial.begin(9600);
}

void SPI_Init(void){
  SPI.setDataMode(MSBFIRST);
  SPI.setDataMode(SPI_MODE0);
  SPI.setClockDivider(SPI_CLOCK_DIV4);
  SPI.begin();
}
 
void Port_Init(void) {
  pinMode(pinMasterReset_0, OUTPUT);
  pinMode(pinIOReset_0, OUTPUT);
  pinMode(pinCS_0, OUTPUT);
  
  pinMode(pinMasterReset_1, OUTPUT);
  pinMode(pinIOReset_1, OUTPUT);
  pinMode(pinCS_1, OUTPUT);
  
  pinMode(pinMasterReset_2, OUTPUT);
  pinMode(pinIOReset_2, OUTPUT);
  pinMode(pinCS_2, OUTPUT);
  
  pinMode(pinMasterReset_3, OUTPUT);
  pinMode(pinIOReset_3, OUTPUT);
  pinMode(pinCS_3, OUTPUT);
  
  pinMode(pinMasterReset_4, OUTPUT);
  pinMode(pinIOReset_4, OUTPUT);
  pinMode(pinCS_4, OUTPUT);
  
  pinMode(pinMasterReset_5, OUTPUT);
  pinMode(pinIOReset_5, OUTPUT);
  pinMode(pinCS_5, OUTPUT);
  
  
  pinMode(pinFSK_0, INPUT);
  pinMode(pinFSK_1, INPUT);
  pinMode(pinFSK_2, INPUT);
  pinMode(pinFSK_3, INPUT);
  pinMode(pinFSK_4, INPUT);
  pinMode(pinFSK_5, INPUT);
  
  pinMode(pinSS, OUTPUT);
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
  SPI.transfer(0x0f);
  SPI.transfer(0xff);
  digitalWrite(pinCS_0,HIGH);
  IO_Update_0();
  //set frequency
  digitalWrite(pinCS_0,LOW);
  SPI.transfer(0x02);
  SPI.transfer(0x40);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
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
  SPI.transfer(0x40);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  digitalWrite(pinCS_1,HIGH);
  IO_Update_1();
}

void DDS2_Init(void) {
  //reset ad9854
  Master_Reset_2();
  //set parameters
  pinMode(pinIOUpdate_2, INPUT);
  digitalWrite(pinCS_2,LOW);
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
  digitalWrite(pinCS_2,HIGH);
  pinMode(pinIOUpdate_2, OUTPUT);
  IO_Update_2();

  //set amplitude
  digitalWrite(pinCS_2,LOW);
  SPI.transfer(0x08);
  SPI.transfer(0x0f);
  SPI.transfer(0xff);
  digitalWrite(pinCS_2,HIGH);
  IO_Update_2();
  //set frequency
  digitalWrite(pinCS_2,LOW);
  SPI.transfer(0x02);
  SPI.transfer(0x40);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  digitalWrite(pinCS_2,HIGH);
  IO_Update_2();
}

void DDS3_Init(void) {
  //reset ad9854
  Master_Reset_3();
  //set parameters
  pinMode(pinIOUpdate_3, INPUT);
  digitalWrite(pinCS_3,LOW);
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
  digitalWrite(pinCS_3,HIGH);
  pinMode(pinIOUpdate_3, OUTPUT);
  IO_Update_3();

  //set amplitude
  digitalWrite(pinCS_3,LOW);
  SPI.transfer(0x08);
  SPI.transfer(0x0f);
  SPI.transfer(0xff);
  digitalWrite(pinCS_3,HIGH);
  IO_Update_3();
  //set frequency
  digitalWrite(pinCS_3,LOW);
  SPI.transfer(0x02);
  SPI.transfer(0x40);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  digitalWrite(pinCS_3,HIGH);
  IO_Update_3();
}

void DDS4_Init(void) {
  //reset ad9854
  Master_Reset_4();
  //set parameters
  pinMode(pinIOUpdate_4, INPUT);
  digitalWrite(pinCS_4,LOW);
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
  digitalWrite(pinCS_4,HIGH);
  pinMode(pinIOUpdate_4, OUTPUT);
  IO_Update_4();

  //set amplitude
  digitalWrite(pinCS_4,LOW);
  SPI.transfer(0x08);
  SPI.transfer(0x0f);
  SPI.transfer(0xff);
  digitalWrite(pinCS_4,HIGH);
  IO_Update_4();
  //set frequency
  digitalWrite(pinCS_4,LOW);
  SPI.transfer(0x02);
  SPI.transfer(0x40);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  digitalWrite(pinCS_4,HIGH);
  IO_Update_4();
}


void DDS5_Init(void) {
  //reset ad9854
  Master_Reset_5();
  //set parameters
  pinMode(pinIOUpdate_5, INPUT);
  digitalWrite(pinCS_5,LOW);
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
  digitalWrite(pinCS_5,HIGH);
  pinMode(pinIOUpdate_5, OUTPUT);
  IO_Update_5();

  //set amplitude
  digitalWrite(pinCS_5,LOW);
  SPI.transfer(0x08);
  SPI.transfer(0x0f);
  SPI.transfer(0xff);
  digitalWrite(pinCS_5,HIGH);
  IO_Update_5();
  //set frequency
  digitalWrite(pinCS_5,LOW);
  SPI.transfer(0x02);
  SPI.transfer(0x40);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  digitalWrite(pinCS_5,HIGH);
  IO_Update_5();
}

