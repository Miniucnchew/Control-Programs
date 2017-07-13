#include <X11/X.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/Xos.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>



int main(int argc, char *argv[]) {
  //Get system window
  Display *dsp=XOpenDisplay(NULL);
  if (!dsp) {return 1;}
  
  XEvent event;

  double z;
  
  while (1) {
    /* get info about current pointer position */
    XQueryPointer(dsp, RootWindow(dsp, DefaultScreen(dsp)),
    &event.xbutton.root, &event.xbutton.window,
    &event.xbutton.x_root, &event.xbutton.y_root,
    &event.xbutton.x, &event.xbutton.y,
    &event.xbutton.state);
    
    z = ((sin(event.xbutton.x) + sin(event.xbutton.y))+2)*1000;
    
    printf("Mouse Coordinates: %d %d | Z: %04d \n", event.xbutton.x, event.xbutton.y, (int)z);
    sleep(0.01);
  } //End while
  
}

