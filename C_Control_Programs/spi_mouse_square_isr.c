#include <X11/X.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/Xos.h>
#include <math.h>
#include <time.h>
#include <unistd.h>    // read/write usleep
#include <stdlib.h>    // exit function
#include <inttypes.h>  // uint8_t, etc
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
#include <wiringPi.h>
#include <wiringPiSPI.h>


Display *dsp;
unsigned char writeBuf[2];
float_t alpha, ma;
long int process_time;

static volatile double z;  
clock_t t;
XEvent event;

int i=0;

/*
 * myInterrupt:
 *********************************************************************************
 */

void myInterrupt0 (void) { 


  /* get info about current pointer position */
  XQueryPointer(dsp, RootWindow(dsp, DefaultScreen(dsp)),
  &event.xbutton.root, &event.xbutton.window,
  &event.xbutton.x_root, &event.xbutton.y_root,
  &event.xbutton.x, &event.xbutton.y,
  &event.xbutton.state);

  //~ z = ((sin(event.xbutton.x) + sin(event.xbutton.y))+2)*50;


  //~ z = event.xbutton.x/8;


  // The following two lines of code add a square wave into the signal
  //~ if (i == 0) {z += 50; i=1;}
  //~ else if (i == 1) {z -= 50; i=0;}



  // The following two lines of code add a regressive moving average.
  // It is not linear. 
  //~ alpha = 0.3;
  //~ ma = alpha*z + (1-alpha)*ma;      


  //~ if (i == 10) { i = 0; }
  //~ z += i;
  //~ i++;

  writeBuf[0] = ((uint16_t)z >> 4) | 0b00110000;
  writeBuf[1] = (uint16_t)z << 4;

  wiringPiSPIDataRW(0, writeBuf, 2);

  //~ printf("Z: %04ld | Moving Avg: %04d | Process Time: %d\n", (int)z, (int)ma, process_time);

   }


/*
 *********************************************************************************
 * main
 *********************************************************************************
 */

int main (void)
{
  
  XInitThreads();
  dsp=XOpenDisplay(NULL);
  if (!dsp) {return 1;}
  
  wiringPiSetup ();
  wiringPiSPISetup(0, 16000000);
  wiringPiISR (0, INT_EDGE_FALLING, &myInterrupt0);
  
  piHiPri(99);
  
  while (1) {
    //~ t = clock();
  
    //~ process_time = clock() - t;
    
    //~ printf("Z: %04d | Process Time: %d | Wait Time: %03ld\n", (int)z, process_time, process_time-cycle_time);

  }
  return 0 ;
}
