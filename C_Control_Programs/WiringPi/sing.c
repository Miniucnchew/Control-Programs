#include <X11/X.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/Xos.h>
#include <math.h>
#include <time.h>
#include <stdio.h>
#include <unistd.h>    // read/write usleep
#include <stdlib.h>    // exit function
#include <inttypes.h>  // uint8_t, etc
#include <linux/i2c-dev.h> // I2C bus definitions
#include <wiringPiSPI.h>


unsigned char writeBuf[2];
long int process_time;
float ma;
int i=0;
  
int main()   {
  
  wiringPiSPISetup(0, 8000000);
  
  //Get system window
  Display *dsp=XOpenDisplay(NULL);
  if (!dsp) {return 1;}
  
  XEvent event;

  double z;  
  clock_t t;
  ma = 0;
  
const uint16_t DACLookup_FullSine[128] =
{
50,52,55,57,60,62,65,67,
69,71,74,76,78,80,82,84,
85,87,89,90,92,93,94,95,
96,97,98,99,99,99,100,100,
100,100,100,99,99,99,98,97,
96,95,94,93,92,90,89,87,
85,84,82,80,78,76,74,71,
69,67,65,62,60,57,55,52,
50,48,45,43,40,38,35,33,
31,29,26,24,22,20,18,16,
15,13,11,10,8,7,6,5,
4,3,2,1,1,1,0,0,
0,0,0,1,1,1,2,3,
4,5,6,7,8,10,11,13,
15,16,18,20,22,24,26,29,
31,33,35,38,40,43,45,48
};

  while (1) {
      
      if (i == 255) {i = 0;}
      
      t = clock();
      
      /* get info about current pointer position */
      XQueryPointer(dsp, RootWindow(dsp, DefaultScreen(dsp)),
      &event.xbutton.root, &event.xbutton.window,
      &event.xbutton.x_root, &event.xbutton.y_root,
      &event.xbutton.x, &event.xbutton.y,
      &event.xbutton.state);
      
      //~ z = event.xbutton.x/12 + 80;//((sin(event.xbutton.x) + sin(event.xbutton.y))+2)*125;
      
      z = DACLookup_FullSine[i];
      
      //~ z += DACLookup_FullSine[i];
      writeBuf[0] = ((uint16_t)z >> 4) | 0b00110000;
      writeBuf[1] = (uint16_t)z << 4;
      
      wiringPiSPIDataRW(0, writeBuf, 2);

            
      process_time = clock() - t;
      printf("Z: %04ld | Moving Avg: %04d | Process Time: %d\n", (int)z, (int)ma, process_time);
      
      
      i++;
      
  } // end while loop

  
  XCloseDisplay(dsp);

  return 0;

}






