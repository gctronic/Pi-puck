#include <wiringPi.h>
#include <unistd.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

#define PWR_ON_PIN 5
#define PWR_ON_RAS_PIN 6

uint8_t press_count = 0;

void buttonInterrupt(void) {
	press_count = 0;
	printf("button press\r\n");
	while(1) {
		usleep(200000);
		if(digitalRead(PWR_ON_RAS_PIN) == 0) {
			press_count++;
			if(press_count >= 10) {
				printf("shutdown\r\n");
				pullUpDnControl(PWR_ON_PIN, PUD_DOWN);	// This is needed in order to have PWR_ON pin to low state during shutdown, since the pins will be 
														// set (somehow ??) to their defaults state, that is input, but the pull setup will remain valid.
				digitalWrite(PWR_ON_PIN, 0);
				usleep(10000);
				system("poweroff");
				break;
			}
		} else {
			break;
		}		
	}
}

int main (void) {	
	
	//wiringPiSetup();
	wiringPiSetupGpio();
	
	digitalWrite(PWR_ON_PIN, 1);
	pinMode(PWR_ON_PIN, OUTPUT);
	digitalWrite(PWR_ON_PIN, 1);
	pinMode(PWR_ON_RAS_PIN,INPUT);
	pullUpDnControl(PWR_ON_RAS_PIN, PUD_UP);
	wiringPiISR(PWR_ON_RAS_PIN, INT_EDGE_FALLING, buttonInterrupt);
	
	while(1) {
		sleep(1);
	}
	
	return 0 ;

}

