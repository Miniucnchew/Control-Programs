
// MCP4725.c
// Program the MCP4725 DAC
// Source: http://www.bristolwatch.com/rpi/mcp4725.html

// Note to self: Figure out how this works!!!

// ads1115b.c read pot on ANC1
// output value in volts exit program.
// uses one-shot mode
// pull up resistors in module caused problems
// used level translator - operated ADS1115 at 5V
// by Lewis Loflin lewis@bvu.net
// www.bristolwatch.com
// Source: http://www.bristolwatch.com/rpi/geany/ads1115a.c


#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>    // read/write usleep
#include <stdlib.h>    // exit function
#include <inttypes.h>  // uint8_t, etc
#include <linux/i2c-dev.h> // I2C bus definitions



int fd_mcp;
int mcp4725_address = 0x62;
int16_t val_mcp;
uint8_t writeBuf_mcp[3];
float myfloat_mcp;

int fd_ads;
int ads_address = 0x48;
int16_t val_ads;
uint8_t writeBuf_ads[3];
uint8_t readBuf_ads[2];
float myfloat_ads;

const float VPS = 4.096 / 2048.0; // volts per step for ads



int main()   {

  /* CONNECTING TO DEVICES */

  // open DAC device on /dev/i2c-1 the default on Raspberry Pi B
  if ((fd_mcp = open("/dev/i2c-1", O_RDWR)) < 0) {
    printf("Error: Couldn't open device! %d\n", fd_mcp);
    exit (1);
  }

  // connect to mcp4725 as i2c slave
  if (ioctl(fd_mcp, I2C_SLAVE, mcp4725_address) < 0) {
    printf("Error: Couldn't find device on address!\n");
    exit (1);
  }
  
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

  /* DONE CONNECTING TO DEVICES */
  
  //*****************************************
  
  //*****************************************

  /* SETTING UP ADS1015 ADC */

  // set config register and start conversion
  // AIN0 and GND, 4.096v, 128s/s
  // Refer to page 19 area of spec sheet
  writeBuf_ads[0] = 1; // config register is 1
  writeBuf_ads[1] = 0b11000010; // 0xC2 single shot off
  // bit 15 flag bit for single shot not used here
  // Bits 14-12 input selection:
  // 100 ANC0; 101 ANC1; 110 ANC2; 111 ANC3
  // Bits 11-9 Amp gain. Default to 010 here 001 P19
  // Bit 8 Operational mode of the ADS1115.
  // 0 : Continuous conversion mode
  // 1 : Power-down single-shot mode (default)

  writeBuf_ads[2] = 0b11100101; // bits 7-0  0x85
  // Bits 7-5 data rate default to 100 for 128SPS
  // Bits 4-0  comparator functions see spec sheet.

  /* DONE SETTING UP ADS1015 ADC */
  
  //*****************************************
  
  //*****************************************

  /* SETTING UP MCP4725 DAC */

  // 12-bit device values from 0-4095
  // page 18-19 spec sheet
  writeBuf_mcp[0] = 0b01000000; // control byte
  // bits 7-5; 010 write DAC; 011 write DAC and EEPROM
  // bits 4-3 unused
  // bits 2-1 PD1, PD0 PWR down P19 00 normal.
  // bit 0 unused

  writeBuf_mcp[1] = 0b00000000; // HIGH data
  // bits 7-0 D11-D4


  writeBuf_mcp[2] = 0b00000000; // LOW data
  // bits 7-4 D3-D0
  // bits 3-0 unused

  /* DONE SETTING UP MCP4725 DAC */
  
  
  
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
  
  
  
  int count = 1;
  
  while (1) {
    
    // read conversion register
    if (read(fd_ads, readBuf_ads, 2) != 2) {
      perror("Read conversion");
      exit(-1);
    }

    // could also multiply by 256 then add readBuf[1]
    val_ads = readBuf_ads[0] << 8 | readBuf_ads[1];
    val_ads = val_ads >> 4;
	
    // with +- LSB sometimes generates very low neg number.
    if (val_ads < 0)   val_ads = 0;

    myfloat_ads = val_ads * VPS; // convert to voltage
    
    val_mcp = val_ads*2;
    
    // write number to MCP4725 DAC
    writeBuf_mcp[1] = val_mcp >> 4; // MSB 11-4 shift right 4 places
    printf("WriteBuf[1] = %04d  ", writeBuf_mcp[1]);

    writeBuf_mcp[2] = val_mcp << 4; // LSB 3-0 shift left 4 places
    printf("WriteBuf[2] = %04d  ", writeBuf_mcp[2]);

    if (write(fd_mcp, writeBuf_mcp, 3) != 3) {
      perror("Write to register 1");
      exit (1);
    }


    count++; // inc count
    
    printf("Count: %08d DEC %04d Volts: %4.3f\n",
    count, val_ads, myfloat_ads);
    // Output: Conversion number 1 HEX 0x1113 DEC 4371 0.546 volts.

    if (val_ads == 0)   break;
    
  } // end while loop


  // power down ADS1115
  writeBuf_ads[0] = 1;    // config register is 1
  writeBuf_ads[1] = 0b11000011; // bit 15-8 0xC3 single shot on
  writeBuf_ads[2] = 0b10000101; // bits 7-0  0x85
  
  if (write(fd_ads, writeBuf_ads, 3) != 3) {
    perror("Write to register 1");
    exit (1);
  }

  close(fd_ads);
  close(fd_mcp);
  return 0;

}



//~ // wiringPi reference

//~ #include <wiringPi.h>
//~ #include <wiringPiI2C.h>

//~ int main(void)
//~ {
   //~ int fd;
	//~ 
	//~ wiringPiSetupGpio();
	//~ piHiPri(99);
	//~ 
	//~ pinMode(4, GPIO_CLOCK);
	//~ pinMode(21, OUTPUT);
	//~ for (;;)
	//~ {
		//~ digitalWrite(21, 1);
		//~ delayMicroseconds(200);
		//~ digitalWrite(21, 0);
		//~ delayMicroseconds(200);
	//~ }
	//~ return 0;
//~ }
