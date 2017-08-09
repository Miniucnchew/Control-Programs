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

int z;
int i;
int fd_mcp;
int print_out = 1;
double time_stamp, time_now;

int fd_ads;
int ads_address = 0x48; 
uint8_t writeBuf_ads[3];
uint8_t readBuf_ads[2];
int cone_dist;

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


void dist_read(void) {
  cone_dist = read_ads(2);
  if (print_out == 1) {
    printf("Cone Dist = %04d\n", cone_dist);// = %0.3fmm\n", cone_dist, (cone_dist-349)*0.008);
  }
}

void z_set(void) {
    
  time_now = time_time();
  if ((time_now - time_stamp) >= 0.3) {
    print_out = 0;
    
    printf("Z Value: ");
    scanf("%d", &z);
    printf("Z = %04d \n\n", z);
    
    writeBuf_mcp[0] = (z >> 8) | 0b00110000;
      // Bit 15: Output Selection. 1 = DAC_B | 0 = DAC_A
      // Bit 14: Don't care. XXX
      // Bit 13: Output gain select bit. 1 = Vout = 0->2.048V | 0 = Vout = 0->4.096V
      // Bit 12: SHDN. 1 = Power on | 0 = Power off
      // Bit 11->0: Data bits. 
    writeBuf_mcp[1] = z & 0xff;
    
    spiWrite(fd_mcp, (char *)writeBuf_mcp, 2);
    
    time_stamp = time_now;
    
    print_out = 1;
  }
}

int main(void) {  
  
  gpioInitialise();
  connect_ads();
  
  time_stamp = time_time();
  
  fd_mcp = spiOpen(0, 16000000, 0b0000000100000000000000);
  
  gpioSetTimerFunc(0, 1000, dist_read);
  
  gpioSetISRFunc(13, FALLING_EDGE, 0, &z_set); 
  
  while (1) {

    
    //~ time_sleep(0.5);
    
    //~ cone_dist = read_ads(2);
    //~ 
    //~ printf("Cone Dist = %03d = %1.3f \n\n", cone_dist, (cone_dist-803.0)*mmPOU); 
  }
  
  
  disconnect_ads();
  spiClose(fd_mcp);
  gpioTerminate();
  
  return 0;
}
