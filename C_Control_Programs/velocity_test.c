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
int x, y, x_pred, y_pred;
double alpha = 0.05;
int y_prev = 0;
int x_prev = 0;
int vx = 0;
int vy = 0;
int i=0;
volatile int z;
int lookup[1600][1200];

void createLookup (void) {
  //~ FILE *fp;
  
  //~ fp = fopen("lookup_table.txt", "w+");
  //~ fprintf(fp, "static const int lookup[1600][1200] = {");
  
  
  for (x = 0; x < 1600; x++) {
    for (y = 0; y < 1200; y++) {
      
       if (x % 100 > 10) {lookup[x][y] = 100;}
      else {lookup[x][y] = 200;}
      
      //~ lookup[x][y] = 100 + 20.0*sin(M_PI*2*(50*x/1600.0+y/1200.0));
      //~ if (lookup[x][y] < 100) {lookup[x][y] = 100;}
      //~ else if (lookup[x][y] > 175) {lookup[x][y] = 175;}
      
      
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
  
  vx = x - x_prev;
  vy = y - y_prev;
  
  x_pred = x + vx;
  if (x_pred > 1599) {x_pred = 1599;}
  y_pred = y + vy;
  if (y_pred > 1199) {y_pred = 1199;}
  
  z = (int)lookup[x][y] + (int)(alpha * lookup[x_pred][y_pred]);

  printf("vx: %04d | vy: %04d | x_pred: %04d | y_pred: %04d | z: %04d\n",
    vx, vy, x_pred, y_pred, z);

  x_prev = x;
  y_prev = y;


  writeBuf[0] = ((uint16_t)z >> 4) | 0b00110000;
  writeBuf[1] = (uint16_t)z << 4;

  wiringPiSPIDataRW(0, writeBuf, 2);

  //~ printf("X: %04d | Y: %04d | Z: %04d\n", x, y, (int)z);

   }



int main (void)
{
  
  XInitThreads();
  dsp=XOpenDisplay(NULL);
  if (!dsp) {return 1;}
  
  wiringPiSetup ();
  wiringPiSPISetup(0, 16000000);
  piHiPri(99);
  
  createLookup();

  wiringPiISR (0, INT_EDGE_FALLING, &myInterrupt0);
  
  while (1) {  }
  return 0 ;
}

