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
XEvent event;
int x, y;
int i=0;
volatile int z;
int lookup[1600][1200];

void createLookup (void) {
  //~ FILE *fp;
  
  //~ fp = fopen("lookup_table.txt", "w+");
  //~ fprintf(fp, "static const int lookup[1600][1200] = {");
  
  
  for (x = 0; x < 1600; x++) {
    for (y = 0; y < 1200; y++) {
      
      lookup[x][y] = 255.0*fabs(sin(M_PI*(50*x/1600.0+y/1200.0)));
      
      //~ if (y == 0) { fprintf(fp, "{ %d, ", z[x][y]); }
      //~ else if (y == 1199) {fprintf(fp, "%d}\n", z[x][y]); }
      //~ else { fprintf(fp, "%d, ", z[x][y]); }
      //~ 
      //~ if (x == 1599) { fprintf( fp, "}") }
      
    }
  }
  printf("Finished with lookup table. Moving on to main program...\n\n\n");
  //~ fclose(fp);
}

void myInterrupt0 (void) { 


  /* get info about current pointer position */
  XQueryPointer(dsp,  RootWindow(dsp, DefaultScreen(dsp)),
  &event.xbutton.root, &event.xbutton.window,
  &event.xbutton.x_root, &event.xbutton.y_root,
  &event.xbutton.x, &event.xbutton.y,
  &event.xbutton.state);
  
  x = event.xbutton.x;
  y = event.xbutton.y;
  
  z = (int)lookup[x][y];


  // The following two lines of code add a square wave into the signal
  //~ if (i == 0) {z += 50; i=1;}
  //~ else if (i == 1) {z -= 50; i=0;}    


  //~ if (i == 10) { i = 0; }
  //~ z += i;
  //~ i++;

  writeBuf[0] = ((uint16_t)z >> 4) | 0b00110000;
  writeBuf[1] = (uint16_t)z << 4;

  wiringPiSPIDataRW(0, writeBuf, 2);

  printf("X: %04d | Y: %04d | Z: %04d\n", x, y, (int)z);

   }



int main (void)
{
  
  createLookup();
  
  
  
  XInitThreads();
  dsp=XOpenDisplay(NULL);
  if (!dsp) {return 1;}
  
  wiringPiSetup ();
  wiringPiSPISetup(0, 16000000);
  wiringPiISR (0, INT_EDGE_FALLING, &myInterrupt0);
  
  piHiPri(99);
  
  while (1) {  }
  return 0 ;
}
