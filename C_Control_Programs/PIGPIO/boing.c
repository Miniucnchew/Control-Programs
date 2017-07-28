#include <stdio.h>
#include <sys/types.h> // open
#include <sys/stat.h>  // open
#include <fcntl.h>     // open
#include <unistd.h>    // read/write usleep
#include <stdlib.h>    // exit
#include <inttypes.h>  // uint8_t, etc
#include <linux/i2c-dev.h> // I2C bus definitions
#include <math.h>
#include <time.h>
#include <string.h>
#include <errno.h>
#include <pigpio.h>

unsigned char writeBuf_mcp[2];

int analog_val[4], analog_val_prev[4];

int z, z_prev;
int i;
int fd_mcp;
double t_pause;

int fd_ads;
int ads_address = 0x48; 
uint8_t writeBuf_ads[3];
uint8_t readBuf_ads[2];
int cone_dist;

const float mmPOU = 0.0029; // mm per optical units


void connect_ads(void) {

  // open ADC device on /dev/i2c-1 the default on Raspberry Pi B
  if ((fd_ads = open("/dev/i2c-1", O_RDWR)) < 0) {
    printf("Error: Couldn't open device! %d\n", fd_ads);
    exit (1);
  }

  // connect to ADS1015 as i2c slave
  if (ioctl(fd_ads, I2C_SLAVE, ads_address) < 0) {
    printf("Error: Couldn't find device on address!\n");
    exit (1);
  }

}

void disconnect_ads(void) {
  // power down ADS1115
  writeBuf_ads[0] = 1;    // config register is 1
  writeBuf_ads[1] = 0b11000011; // bit 15-8 0xC3 single shot on
  writeBuf_ads[2] = 0b10000101; // bits 7-0  0x85
  
  if (write(fd_ads, writeBuf_ads, 3) != 3) {
    perror("Write to register 1");
    exit (1);
  }

  close(fd_ads);
}

int read_ads(int channel)   {

  int16_t val_ads;

  
  //*****************************************

  /* SETTING UP ADS1015 ADC */

  // set config register and start conversion
  // AIN0 and GND, 4.096v, 128s/s
  // Refer to page 19 area of spec sheet
  writeBuf_ads[0] = 1; // config register is 1
  
  writeBuf_ads[1] = 0b10000011;
  if (channel == 0) { writeBuf_ads[1] |= 0b01000000; }
  else if (channel == 1) {writeBuf_ads[1] |= 0b01010000; }
  else if (channel == 2) {writeBuf_ads[1] |= 0b01100000; }
  else if (channel == 3) {writeBuf_ads[1] |= 0b01110000; }
  else {printf("Channel doesn't exist."); exit(-1); }
  
  // bit 15 flag bit for single shot
  // Bits 14-12 input selection:
  // 100 ANC0; 101 ANC1; 110 ANC2; 111 ANC3
  // Bits 11-9 Amp gain.
  // Bit 8 Operational mode of the ADS1115.
  // 0 : Continuous conversion mode
  // 1 : Power-down single-shot mode (default)

  writeBuf_ads[2] = 0b11100101; // bits 7-0  0x85
  // Bits 7-5 data rate default to 100 for 128SPS
  // Bits 4-0  comparator functions see spec sheet.

  /* DONE SETTING UP ADS1015 ADC */
  
  //*****************************************
  
  //*****************************************
  
  
  if (write(fd_ads, writeBuf_ads, 3) != 3) {
    perror("Write to register 1");
    exit (1);
  }
 
 
  // set pointer to 0
  readBuf_ads[0] = 0;
  if (write(fd_ads, readBuf_ads, 1) != 1) {
    perror("Write register select");
    exit(-1);
  }

    
  // read conversion register
  if (read(fd_ads, readBuf_ads, 2) != 2) {
    perror("Read conversion");
    exit(-1);
  }

  // could also multiply by 256 then add readBuf[1]
  val_ads = readBuf_ads[0] << 8 | readBuf_ads[1];
  val_ads = val_ads >> 4;
  
  return val_ads;
} 

void myInterrupt0(void) {
  //~ printf("Z Value: ");
  //~ scanf("%d", &z);

  //~ printf("Z = %03d\n", z);
  
  analog_val[1] = read_ads(1);
  analog_val[2] = read_ads(2);
  
  if (analog_val[1] > 100) {
    analog_val[0] = read_ads(0); // Position (0-1750) (Baseline~=120->130)
    analog_val_prev[0] = analog_val[0];
    z_prev = z;
    
  } else {
    z = z_prev;
    analog_val[0] = analog_val_prev[0];
  }  
  
  
  
  
  //~ analog_val[1] = read_ads(1);
  //~ 
  //~ if (analog_val[1] > 100) {
    //~ 
    //~ z_prev = z;    
    //~ analog_val_prev[0] = analog_val[0];    
    //~ 
    //~ analog_val[0] = read_ads(0); // Position (0-1750) (Baseline~=120->130)
    //~ 
  //~ } else {
    z = z_prev;
    //~ analog_val[0] = analog_val_prev[0];
  //~ }  
  
  z = analog_val[0]/8;
  
  for (i = 0; i < abs(z - 127); i++) {

    writeBuf_mcp[0] = ((uint16_t)z >> 4) | 0b00110000;
    writeBuf_mcp[1] = (uint16_t)z << 4;

    spiWrite(fd_mcp, (char *)writeBuf_mcp, 2);

    time_sleep(0.001);

    if (z >= 127) {z = 127 - abs(127 - z) + i; }
    else {z = 127 + abs(127 - z) - i; }

    z_prev = z;
    printf("Z: %03d\n", z);
  }
  
}
int main(void) {  
  
  gpioInitialise();
  connect_ads();
  
  fd_mcp = spiOpen(0, 16000000, 0b0000000100000000000000);
  
  
  gpioSetISRFunc(17, EITHER_EDGE, 0, &myInterrupt0);

  
  while (1) {  }
  
  
  disconnect_ads();
  spiClose(fd_mcp);
  gpioTerminate();
  
  return 0;
}
