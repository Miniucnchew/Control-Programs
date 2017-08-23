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

int fd_mcp;
unsigned char writeBuf[2];
int x, y;
int i=0;
volatile int z, z_prev;
int lookup[1800];

int fd_ads;
int ads_address = 0x48;
uint8_t writeBuf_ads[3];
uint8_t readBuf_ads[2];
float myfloat_ads;

const float mmPOU = 0.0029; // mm per optical units

int analog_val[4];
int analog_val_prev[4];

int w_freq, w_form, w_off, amp, trial_dur;
int button_interrupt_called=0;

float sum_vel = 0;
uint32_t velocity = 0;
float avg;
clock_t start_t, end_t, total_t;

void createLookup (int waveform, int freq, int amplitude, int offset) {
  
    if (waveform == 1) {
      for (x = 0; x < 1800; x++) {
        lookup[x] = offset + (float)amplitude*((sin(M_PI*2*(freq*x/1800.0))+1));
        //~ lookup[x] = offset + amplitude/4*((sin(M_PI*2*(freq*x/1800.0))+1) + sin(M_PI*2*(freq*2*x/1800.0))+1 );
      }
    } else if (waveform == 2) {
      int period = 1800/freq;
      int p_count = 0;
      for (x = 0; x < 1800; x++) {
        if (x % period == 0 && x > 0) {p_count++;}
        if (abs(period - (x - p_count*period)) > period/2) {lookup[x] = 0;}
        else {lookup[x] = amplitude;}
      }
    } else if (waveform == 3) {
      int period = 1800/freq;
      int p_count = 0;
      for (x = 0; x < 1800; x++) {
        if (x % period == 0 && x > 0) {p_count++;}
        lookup[x] = (x - p_count*period)*amplitude/period;
      }
    }
    
    
    //~ lookup[x] += rand() % 10; 
    //~ lookup[x] = (int)(100*x/1800.0);
}



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

void myInterrupt0 (void) { 
/*
  analog_val[0] = Position (0-1750) (Baseline~=120->130)
  analog_val[1] = Force (0-1400) (tare to change baseline)
  analog_val[2] = Distance Sensor (250-900) (Baseline~=530)
  analog_val[3] = read_ads(3); // Ground
*/   
    
  
  if (button_interrupt_called == 0) {
    analog_val[1] = read_ads(1);
    analog_val[2] = read_ads(2);
    
    if (analog_val[1] > 50) {
      analog_val[0] = read_ads(0); // Position (0-1750) (Baseline~=120->130)
      z = lookup[analog_val[0]];
            
      z_prev = z;
      
    } else {
      z = z_prev;
      analog_val[0] = analog_val_prev[0];
    }
    
    writeBuf[0] = (z >> 8) | 0b00110000;
    writeBuf[1] = z & 0xff;

    spiWrite(fd_mcp, (char *)writeBuf, 2);
    
    //~ end_t = clock();
    
    //~ velocity = (analog_val[0] - analog_val_prev[0])*(10.1/1800)/((double)(end_t-start_t)/CLOCKS_PER_SEC);
    //~ sum_vel += velocity;
    //~ i++; 
    
    //~ printf("Pos: %d\n", analog_val[0]);
    //~ 
    //~ analog_val_prev[0] = analog_val[0];
    //~ start_t = clock();
    
    
    //~ printf("Pos: %04d | Force: %04d | Dist: %04d | Z: %03d\n", analog_val[0], 
    //~ analog_val[1], analog_val[2], z);
  } 

}

int main(int argc, char *argv[]) {
  
  if (argc != 6) {
    printf("usage: sudo ./parameter_test waveform frequency amplitude offset trial_duration"); 
    exit(1);
  }
  
  srand(time(NULL));
  
  connect_ads();    
  
  gpioInitialise();
  
  fd_mcp = spiOpen(0, 16000000, 0b0000000100000000000000);
   
  w_form = atoi(argv[1]);
  w_freq = atoi(argv[2]);
  amp = atoi(argv[3]);
  w_off = atoi(argv[4]);
  trial_dur = atoi(argv[5]);
  
  //~ printf("waveform: %d | frequency: %d | amplitude: %d | offset: %d", w_form, w_freq, amp, w_off);
  
  //~ gpioSleep(0, 3, 0);
  
  createLookup(w_form, w_freq, amp, w_off);
  
  gpioSetISRFunc(17, EITHER_EDGE, 0, myInterrupt0);
  
  gpioSleep(0, trial_dur, 0);
  
  gpioSetISRFunc(17, EITHER_EDGE, 0, NULL);
  
  //~ avg = 1.0*(sum_vel/i);
  
  //~ printf("Average Velocity: %fcm/s \n", avg);
  
  disconnect_ads();
  
  spiClose(fd_mcp);
  gpioTerminate();
  
  
  return 0;
}



