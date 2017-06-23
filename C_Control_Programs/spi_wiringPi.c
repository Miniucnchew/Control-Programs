#include <wiringPiSPI.h>


unsigned char writeBuf[2];

int main ( void ) {
  
  writeBuf[0] = 0b00111100;
  writeBuf[1] = 0b10000000;
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
  
  
  
  wiringPiSPISetup(0, 1000000);
  
  wiringPiSPIDataRW(0, writeBuf, 2);
  
  
}
