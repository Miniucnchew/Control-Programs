
#include <stdio.h>
#include <time.h>
#include <math.h>



long int last_heartbeat;
long int heartbeat_difference;
struct timespec gettime_now;
int io_state = 0;
int hb_10ms_timer = 0;
int hb_100ms_timer = 0;
int RPI_GPIO_P1_23 = 23;

int main(void) {
  
	//SETUP HEARTBEAT TIMER
	clock_gettime(CLOCK_REALTIME, &gettime_now);
	last_heartbeat = gettime_now.tv_nsec;


  while(1){
	//---------------------------
	//---------------------------
	//----- HEARTBEAT TIMER -----
	//---------------------------
	//---------------------------
	clock_gettime(CLOCK_REALTIME, &gettime_now);
	heartbeat_difference = gettime_now.tv_nsec - last_heartbeat;		//Get nS value
	if (heartbeat_difference < 0)
		heartbeat_difference += 1000000000;				//(Rolls over every 1 second)
    
	if (heartbeat_difference > 1000000)					//<<< Heartbeat every 1mS
	{
    printf("1ms\n");
		//-------------------------
		//----- 1mS HEARTBEAT -----
		//-------------------------
		last_heartbeat += 1000000;						//<<< Heartbeat every 1mS
		if (last_heartbeat > 1000000000)				//(Rolls over every 1 second)
			last_heartbeat -= 1000000000;
	
	
	
		//Toggle a pin so we can verify the heartbeat is working using an oscilloscope
		//~ io_state ^= 1;									//Toggle the pins state
		//~ bcm2835_gpio_write(RPI_GPIO_P1_23, io_state);
	
	
	
	
		//--------------------------
		//----- 10mS HEARTBEAT -----
		//--------------------------
		hb_10ms_timer++;
		if (hb_10ms_timer == 10)
		{
      printf("    10ms\n");
			hb_10ms_timer = 0;
	
	
	
		} //if (hb_10ms_timer == 10)
	
	
		//---------------------------
		//----- 100mS HEARTBEAT -----
		//---------------------------
		hb_100ms_timer++;
		if (hb_100ms_timer == 100)
		{
      printf("      100ms\n");
			hb_100ms_timer = 0;
	
    
	
		} //if (hb_100ms_timer == 100)
	
	} //if (heartbeat_difference > 1000000)
  }
return 0;

}
