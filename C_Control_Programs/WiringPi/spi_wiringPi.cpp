#include <wiringPiSPI.h>
#include <stdio.h>

int z;
unsigned char writeBuf[2];
int i;

int main ( void ) {
  wiringPiSPISetup(0, 8000000);
  i = 0;
  while (1) {
    
    if (i == 0) {z = 80; i=1;}
    else if (i == 1) {z = 200; i=0;}
    
  
    writeBuf[0] = z >> 4 | 0b00110000;
    writeBuf[1] = z << 4;

    //~ bit 15 
    //~   0 = Write to DAC register
    //~   1 = Ignore this command
    
    //~ bit 14 — Don’t Care
    
    //~ bit 13 GA: Output Gain Selection bit
    //~   1 = 1x (VOUT = VREF * D/4096)
    //~   0 = 2x (VOUT = 2 * VREF * D/4096), where internal VREF = 2.048V.
    
    //~ bit 12 SHDN: Output Shutdown Control bit
    //~   1 = Active mode operation. VOUT is available.
    //~   0 = Shutdown the device. Analog output is not available. 
    
    //~ bit 11-4 D7:D0: DAC Input Data bits.
    
    //~ bit 3-0 : Don't Care
    
    
    

    //~ printf("%d | %d\n", i, z);
    wiringPiSPIDataRW(0, writeBuf, 2);
    
  }
}
