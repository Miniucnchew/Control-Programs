// MCP4725.c
// Program the MCP4725 DAC
// Source: http://www.bristolwatch.com/rpi/mcp4725.html

// Note to self: Figure out how this works!!!

#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>    // read/write usleep
#include <stdlib.h>    // exit function
#include <inttypes.h>  // uint8_t, etc
#include <linux/i2c-dev.h> // I2C bus definitions

int fd;
int mcp4725_address = 0x62;
int16_t val;
uint8_t writeBuf[3];
float myfloat;

int main()   {

  // open device on /dev/i2c-1 the default on Raspberry Pi B
  if ((fd = open("/dev/i2c-1", O_RDWR)) < 0) {
    printf("Error: Couldn't open device! %d\n", fd);
    exit (1);
  }

  // connect to mcp4725 as i2c slave
  if (ioctl(fd, I2C_SLAVE, mcp4725_address) < 0) {
    printf("Error: Couldn't find device on address!\n");
    exit (1);
  }

  // 12-bit device values from 0-4095

  // page 18-19 spec sheet
  writeBuf[0] = 0b01000000; // control byte
  // bits 7-5; 010 write DAC; 011 write DAC and EEPROM
  // bits 4-3 unused
  // bits 2-1 PD1, PD0 PWR down P19 00 normal.
  // bit 0 unused

  writeBuf[1] = 0b00000000; // HIGH data
  // bits 7-0 D11-D4


  writeBuf[2] = 0b00000000; // LOW data
  // bits 7-4 D3-D0
  // bits 3-0 unused

  // input number from 0-4095
  // 2048 50% Vcc
  char buffer [15];
  printf ("Enter a number 0-4095: ");
  scanf("%s", buffer);
  // string to int
  val = atoi(buffer);
  printf("You entered %d  ", val);

  // write number to MCP4725 DAC
  writeBuf[1] = val >> 4; // MSB 11-4 shift right 4 places
  printf("WriteBuf[1] = %d  ", writeBuf[1]);

  writeBuf[2] = val << 4; // LSB 3-0 shift left 4 places
  printf("WriteBuf[2] = %d  \n", writeBuf[2]);

  if (write(fd, writeBuf, 3) != 3) {
    perror("Write to register 1");
    exit (1);
  }

  close(fd);
  return 0;

}
