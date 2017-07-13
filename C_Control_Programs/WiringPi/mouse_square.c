#include <X11/X.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/Xos.h>
#include <math.h>
#include <time.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>    // read/write usleep
#include <stdlib.h>    // exit function
#include <inttypes.h>  // uint8_t, etc
#include <linux/i2c-dev.h> // I2C bus definitions

long int process_time;

int fd_mcp;
int mcp4725_address = 0x62;
int16_t val_mcp;
uint8_t writeBuf_mcp[3];
float myfloat_mcp;

void DelayMicrosecondsNoSleep (int delay_us)
{
	long int start_time;
	long int time_difference;
	struct timespec gettime_now;

	clock_gettime(CLOCK_REALTIME, &gettime_now);
	start_time = gettime_now.tv_nsec;		//Get nS value
	while (1)
	{
		clock_gettime(CLOCK_REALTIME, &gettime_now);
		time_difference = gettime_now.tv_nsec - start_time;
		if (time_difference < 0)
			time_difference += 1000000000;				//(Rolls over every 1 second)
		if (time_difference > (delay_us * 1000))		//Delay for # nS
			break;
	}
}
  
int main()   {
  
  //Get system window
  Display *dsp=XOpenDisplay(NULL);
  if (!dsp) {return 1;}
  
  XEvent event;

  double z;

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

  /* DONE CONNECTING TO DEVICES */
  
  //*****************************************
  
  //*****************************************

  /* SETTING UP MCP4725 DAC */

  // 12-bit device values from 0-4095
  // page 18-19 spec sheet
  writeBuf_mcp[0] = 0b00000000; // control byte
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
  
  int i = 0;
  int count = 0;
  clock_t t;
  
  while (1) {
      
      t = clock();
      
      /* get info about current pointer position */
      XQueryPointer(dsp, RootWindow(dsp, DefaultScreen(dsp)),
      &event.xbutton.root, &event.xbutton.window,
      &event.xbutton.x_root, &event.xbutton.y_root,
      &event.xbutton.x, &event.xbutton.y,
      &event.xbutton.state);
      
      z = ((sin(event.xbutton.x) + sin(event.xbutton.y))+2)*1000;
      
      
      
      val_mcp = (int)z;
       
       
       
      // write number to MCP4725 DAC
      writeBuf_mcp[1] = val_mcp >> 4; // MSB 11-4 shift right 4 places
      //~ printf("WriteBuf[1] = %04d  ", writeBuf_mcp[1]);
      
      writeBuf_mcp[2] = val_mcp << 4; // LSB 3-0 shift left 4 places
      //~ printf("WriteBuf[2] = %04d  ", writeBuf_mcp[2]);
      
      if (write(fd_mcp, writeBuf_mcp, 3) != 3) {
        perror("Write to register 1");
        exit (1);
      }


      count++; // inc count
      i++;
      
      process_time = clock() - t;
      printf("Z: %04d | Process Time: %d\n", (int)z, process_time);
      
      //DelayMicrosecondsNoSleep(...);
      delay(0.01);
      
  } // end while loop

  
  XCloseDisplay(dsp);

  close(fd_mcp);
  return 0;

}
