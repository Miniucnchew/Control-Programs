#include <stdio.h>
#include <inttypes.h>  // uint8_t, etc
#include <math.h>
#include <time.h>
#include <string.h>
#include <errno.h>
#include <pigpio.h>

unsigned char writeBuf[2];
int x, y;
int z;
int i = 0;
int lookup[1800];
int mcp;
int k=0;

void createLookup (void) {
  for (x = 0; x < 20; x++) {
    //~ lookup[x] = 120+20.0*(sin(M_PI*2*(x/20.0))+1);
    //~ lookup[x] = (int)(100*x/1800.0);
  }
}


void myInterrupt0 (void) {    
  
  //~ if (i >= 20) {i = 0;}
  if (i == 0) {i = 255;}
  else {i = 0;}
  
  z = i;
  //~ z = lookup[i];
  
  writeBuf[0] = ((uint16_t)z >> 4) | 0b00110000;
  writeBuf[1] = (uint16_t)z << 4;

  spiWrite(mcp, (char *)writeBuf, 2);
    
  //~ printf("i: %03d\n", i);
  //~ i++;
}



int main(void) {  
  
  gpioInitialise();
  
  mcp = spiOpen(0, 16000000, 0b0000000100000000000000);
  //~ int mcp = bbSPIOpen(8, 27, 10, 11, 0, 16000000, 0b0000000000000000000000);
  
  //~ wiringPiSetup ();
  //~ wiringPiSPISetup(0, 16000000); 
  //~ piHiPri(99);
  
  //~ createLookup();
  
  gpioSetISRFunc(17, EITHER_EDGE, 0, myInterrupt0);
  
  
  
  while (1) { }
  
  spiClose(mcp);
  gpioTerminate();
  
  return 0;
}
