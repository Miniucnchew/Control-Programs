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
float_t alpha, ma;
long int process_time;

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
  
  
  while (1) {
      
      t = clock();
      
      /* get info about current pointer position */
      XQueryPointer(dsp, RootWindow(dsp, DefaultScreen(dsp)),
      &event.xbutton.root, &event.xbutton.window,
      &event.xbutton.x_root, &event.xbutton.y_root,
      &event.xbutton.x, &event.xbutton.y,
      &event.xbutton.state);
      
      z = event.xbutton.x/8;//((sin(event.xbutton.x) + sin(event.xbutton.y))+2)*125;
      
      // The following two lines of code add a square wave into the signal
      //~ if (i == 0) {z += 5; i=1;}
      //~ else if (i == 1) {z -= 5; i=0;}
      
      // The following two lines of code add a regressive moving average.
      // It is not linear. 
      //~ alpha = 0.3;
      //~ ma = alpha*z + (1-alpha)*ma;      
      
      if (i == 10) { i = 0; }
      z += i;
      i++;
      writeBuf[0] = ((uint16_t)z >> 4) | 0b00110000;
      writeBuf[1] = (uint16_t)z << 4;
      
      wiringPiSPIDataRW(0, writeBuf, 2);

            
      process_time = clock() - t;
      printf("Z: %04ld | Moving Avg: %04d | Process Time: %d\n", (int)z, (int)ma, process_time);
      
      //~ DelayMicrosecondsNoSleep(10);
      //~ delay(0.01);
      
  } // end while loop

  
  XCloseDisplay(dsp);

  return 0;

}
