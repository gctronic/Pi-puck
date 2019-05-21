#include <stdio.h>
#include <stdint.h> 
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <linux/i2c-dev.h> /* for I2C_SLAVE */
//#include <linux/i2c.h>
#include <sys/ioctl.h>
#include <stdlib.h>
#include <unistd.h>

#define ACTUATORS_SIZE 19
#define SENSORS_SIZE 30

int fh;
uint8_t actuators_data[ACTUATORS_SIZE];
uint8_t sensors_data[SENSORS_SIZE];
uint16_t prox[8];
uint16_t mic[4];
uint8_t sel;
int16_t mot_steps[2];
uint8_t tv_remote;
uint8_t actuators_state = 0;
uint16_t i = 0;

int read_reg(int file, uint8_t reg, int count, uint8_t *data) {

	int ret = 0;
	int i = 0;

	ret=write(file, actuators_data, ACTUATORS_SIZE);
	if (ret != ACTUATORS_SIZE) {
		perror("write before read");
		return -1;
	}

	ret=read(file, data, count);
	if (ret != count) {
		for(i=0; i<ret; i++) {
			printf("%d, \r\n", data[i]);
		}
		printf("ret/count=%d/%d\n", ret, count);
		perror("read");
		return -1;
	}

	return 0;
}

int main() {

	fh = open("/dev/i2c-4", O_RDWR);	// open the I2C dev driver for bus 3

	ioctl(fh, I2C_SLAVE, 0x1F);			// tell the driver we want the device with address 0x1F (7-bits) on the I2C bus

	while(1) {

		switch(actuators_state) {
			case 0:
				actuators_data[0] = 0;		// Left speed: 512
				actuators_data[1] = 2;
				actuators_data[2] = 0;		// Right speed: -512
				actuators_data[3] = 0xFE;
				actuators_data[4] = 0; 		// Speaker sound
				actuators_data[5] = 0x0F;	// LED1, LED3, LED5, LED7 on/off flag
				actuators_data[6] = 100;	// LED2 red
				actuators_data[7] = 0;		// LED2 green
				actuators_data[8] = 0;		// LED2 blue
				actuators_data[9] = 100;	// LED4 red
				actuators_data[10] = 0;		// LED4 green
				actuators_data[11] = 0;		// LED4 blue
				actuators_data[12] = 100;	// LED6 red
				actuators_data[13] = 0;		// LED6 green
				actuators_data[14] = 0;		// LED6 blue
				actuators_data[15] = 100;	// LED8 red
				actuators_data[16] = 0;		// LED8 green
				actuators_data[17] = 0;		// LED8 blue
				actuators_data[18] = 0; 	// Additional future usage.
				actuators_state = 1;
				break;
			case 1:
				actuators_data[0] = 0;		// Left speed: 0
				actuators_data[1] = 0;
				actuators_data[2] = 0;		// Right speed: 0
				actuators_data[3] = 0;
				actuators_data[4] = 0; 		// Speaker sound
				actuators_data[5] = 0x0;	// LED1, LED3, LED5, LED7 on/off flag
				actuators_data[6] = 0;		// LED2 red
				actuators_data[7] = 100;	// LED2 green
				actuators_data[8] = 0;		// LED2 blue
				actuators_data[9] = 0;		// LED4 red
				actuators_data[10] = 100;	// LED4 green
				actuators_data[11] = 0;		// LED4 blue
				actuators_data[12] = 0;		// LED6 red
				actuators_data[13] = 100;	// LED6 green
				actuators_data[14] = 0;		// LED6 blue
				actuators_data[15] = 0;		// LED8 red
				actuators_data[16] = 100;	// LED8 green
				actuators_data[17] = 0;		// LED8 blue
				actuators_data[18] = 0;		// Additional future usage.
				actuators_state = 2;
				break;
			case 2:
				actuators_data[0] = 0;		// Left speed: 512
				actuators_data[1] = 2;
				actuators_data[2] = 0;		// Right speed: -512
				actuators_data[3] = 0xFE;
				actuators_data[4] = 0; 		// Speaker sound
				actuators_data[5] = 0x0F;	// LED1, LED3, LED5, LED7 on/off flag
				actuators_data[6] = 0;		// LED2 red
				actuators_data[7] = 0;		// LED2 green
				actuators_data[8] = 100;	// LED2 blue
				actuators_data[9] = 0;		// LED4 red
				actuators_data[10] = 0;		// LED4 green
				actuators_data[11] = 100;	// LED4 blue
				actuators_data[12] = 0;		// LED6 red
				actuators_data[13] = 0;		// LED6 green
				actuators_data[14] = 100;	// LED6 blue
				actuators_data[15] = 0;		// LED8 red
				actuators_data[16] = 0;		// LED8 green
				actuators_data[17] = 100;	// LED8 blue
				actuators_data[18] = 0; 	// Additional future usage.
				actuators_state = 3;
				break;
			case 3:
				actuators_data[0] = 0;		// Left speed: 0
				actuators_data[1] = 0;
				actuators_data[2] = 0;		// Right speed: 0
				actuators_data[3] = 0;
				actuators_data[4] = 0; 		// Speaker sound
				actuators_data[5] = 0x0;	// LED1, LED3, LED5, LED7 on/off flag
				actuators_data[6] = 0;		// LED2 red
				actuators_data[7] = 100;	// LED2 green
				actuators_data[8] = 0;		// LED2 blue
				actuators_data[9] = 100;	// LED4 red
				actuators_data[10] = 100;	// LED4 green
				actuators_data[11] = 0;		// LED4 blue
				actuators_data[12] = 100;	// LED6 red
				actuators_data[13] = 100;	// LED6 green
				actuators_data[14] = 0;		// LED6 blue
				actuators_data[15] = 100;	// LED8 red
				actuators_data[16] = 100;	// LED8 green
				actuators_data[17] = 0;		// LED8 blue
				actuators_data[18] = 100; 	// Additional future usage.
				actuators_state = 0;
				break;
		}

		read_reg(fh, 0x00, SENSORS_SIZE, sensors_data);

		for(i=0; i<8; i++) {
			prox[i] = sensors_data[i*2+1]*256+sensors_data[i*2];
		}
		printf("prox: %.4d, %.4d, %.4d, %.4d, %.4d, %.4d, %.4d, %.4d\r\n", prox[0], prox[1], prox[2], prox[3], prox[4], prox[5], prox[6], prox[7]);
		for(i=0; i<4; i++) {
			mic[i] = sensors_data[16+i*2+1]*256+sensors_data[16+i*2];
		}
		printf("mic: %.4d, %.4d, %.4d, %.4d\r\n", mic[0], mic[1], mic[2], mic[3]);
		printf("sel: %.2d\r\n", sensors_data[24]);
		for(i=0; i<4; i++) {
			mot_steps[i] = sensors_data[25+i*2+1]*256+sensors_data[25+i*2];
		}
		printf("steps: %.4d, %.4d\r\n", mot_steps[0], mot_steps[1]);
		printf("tv: %.2d\r\n", sensors_data[29]);

		printf("\r\n");

		usleep(500000);	// let the bus be free for a while

	}

	close(fh);
	
	return 0;

}
