// *** Hardwarespecific defines ***

#if defined(__32MX320F128H__)
	#define SDA	18					// A4 (Remeber to set the jumper correctly)
	#define SCL	19					// A5 (Remeber to set the jumper correctly)
#elif defined(__32MX340F512H__)
	#define SDA	18					// A4 (Remeber to set the jumper correctly)
	#define SCL	19					// A5 (Remeber to set the jumper correctly)
#elif defined(__32MX795F512L__)
	#define SDA	20					// Digital 20
	#define SCL	21					// Digital 21
#else
	#error "Unsupported PIC32 MCU!"
#endif  

#ifndef TWI_FREQ
	#define TWI_FREQ 400000L
#endif

#define MAX_VOLTAGE	3.3f
#define LSb_STEP	0.0008056640625f