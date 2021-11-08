#include "IRLibAll.h"

// Sender hardcoded on pin 3
IRsend mySender;

//Create a receiver object to listen on pin 2
IRrecvPCI myReceiver(2);
//Create a decoder object 
IRdecode myDecoder;   

// Mode jumper
const int jumperPin = 4;
int jumperState = -1;

// Operation modes
const int MODE_RECIEVER     = 1;
const int MODE_TRANSMITTER  = 0;

int readJumper() {
  if (-1 == jumperState) {
    Serial.print(F(" -- Jumper state: "));
    jumperState = digitalRead(jumperPin);
    Serial.println(jumperState);
  }
  return jumperState;
}

bool isTransmitter() {
  return readJumper() == MODE_TRANSMITTER;
}

bool isReciever() {
  return readJumper() == MODE_RECIEVER;
}


void setup() {
  Serial.begin(115200);
  if (!Serial) delay(2000);

  // Setup jumper
  pinMode(jumperPin, INPUT);

  // Read jumper state
  readJumper();

  Serial.println(F("READY"));
}

void recieverLoop() {
    //Serial.println(F("Recieve IR signal"));
    myReceiver.enableIRIn();      //Restart receiver

    //Continue looping until you get a complete signal received
    if (!myReceiver.getResults()) {
      return;
    }
    
    myDecoder.decode();           //Decode it

    Serial.print("r,");
    Serial.print(myDecoder.protocolNum, DEC);
    Serial.print(",");
    Serial.print(myDecoder.bits, DEC);
    Serial.print(",");
    Serial.print(myDecoder.address, DEC);
    Serial.print(",");
    Serial.println(myDecoder.value, DEC);
      
    //myDecoder.dumpResults(true);  //Now print results. Use false for less detail
}


char buffer[32];
char* bptr = buffer;
const char COMMAND_PROTOCOL = 'p';
const char COMMAND_BITS = 'b';
const char COMMAND_ADDRESS = 'a';
const char COMMAND_VALUE = 'v';
const char COMMAND_SEND = '\n';

int protocol = 0;
int bits = 0;
int address = 0;
int value = 0;

void transmitterLoop() {
    //Serial.println(F("Send IR signal"));
    //mySender.send(SONY, 0xa8bca, 20);
    if (Serial.available() == 0) {
      return;
    }

    char ch = Serial.read();
    Serial.print(" -- Char: ");
    Serial.println(ch);
    if (ch == COMMAND_PROTOCOL) {
      protocol = atoi(buffer);
      Serial.print(" -- Protocol: ");
      Serial.println(protocol);
      bptr = buffer;
      memset(buffer, 0, sizeof(buffer));
    } else if (ch == COMMAND_BITS) {
      bits = atoi(buffer);
      Serial.print(" -- Bits: ");
      Serial.println(bits);
      bptr = buffer;
      memset(buffer, 0, sizeof(buffer));      
    } else if (ch == COMMAND_ADDRESS) {
      address = atoi(buffer);
      Serial.print(" -- Address: ");
      Serial.println(address);
      bptr = buffer;
      memset(buffer, 0, sizeof(buffer));
    } else if (ch == COMMAND_VALUE) {
      value = atoi(buffer);
      Serial.print(" -- Value: ");
      Serial.println(value);
      bptr = buffer;
      memset(buffer, 0, sizeof(buffer));
    } else if (ch == COMMAND_SEND) {
      //Serial.print(" -- Send: ");
      mySender.send(protocol, value, bits);
      bptr = buffer;
      memset(buffer, 0, sizeof(buffer));
      Serial.print("t,");
      Serial.print(protocol, DEC);
      Serial.print(",");
      Serial.print(bits, DEC);
      Serial.print(",");
      Serial.print(address, DEC);
      Serial.print(",");
      Serial.println(value, DEC);
    } else {
      *bptr = ch;
      bptr += 1;
      Serial.print(" -- Buffer: ");
      Serial.println(buffer);
    }
}

void loop() {
  if (isReciever()) {
    recieverLoop();  
  } else if (isTransmitter()) {
    transmitterLoop();
  }
}
