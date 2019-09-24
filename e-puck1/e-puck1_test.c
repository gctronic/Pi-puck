#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <linux/i2c-dev.h> /* for I2C_SLAVE */
//#include <linux/i2c.h>
#include <sys/ioctl.h>
#include <stdlib.h>
#include <unistd.h>

#define ROBOT_ADDRESS 0x1F

#define RING_LEDS		0x00
#define FRONT_BODY_LEDS	0x01
#define LEFT_SPEED		0x02
#define RIGHT_SPEED		0x03
#define LEFT_STEPS		0x04
#define RIGHT_STEPS		0x05
#define IR_ENABLE		0x06
#define PROX_SENSOR0	0x07
#define PROX_SENSOR1	0x08
#define PROX_SENSOR2	0x09
#define PROX_SENSOR3	0x0a
#define PROX_SENSOR4	0x0b
#define PROX_SENSOR5	0x0c
#define PROX_SENSOR6	0x0d
#define PROX_SENSOR7	0x0e
#define AMBIENT_SENSOR0	0x0f
#define AMBIENT_SENSOR1	0x10
#define AMBIENT_SENSOR2	0x11
#define AMBIENT_SENSOR3	0x12
#define AMBIENT_SENSOR4	0x13
#define AMBIENT_SENSOR5	0x14
#define AMBIENT_SENSOR6	0x15
#define AMBIENT_SENSOR7	0x16

int fh;
uint8_t i = 0;
uint16_t prox[8];
uint16_t prox_amb[8];
int16_t mot_steps[2];
uint8_t temp_write[32];
uint8_t temp_read[64];


int read_reg(int file, uint8_t reg, int count, uint8_t *data) {

	if(write(file, &reg, 1) != 1) {
		perror("robot i2c read error 1");
		return -1;
	}

	if(read(file, data, count) != count) {
		perror("robot i2c read error 2");
		return -1;
	}

	return 0;
}

int write_reg(int file, uint8_t reg, int count, uint8_t *data) {
	temp_write[0] = reg;
	memcpy(&temp_write[1], data, count);
	
	if(write(file, temp_write, count+1) != (count+1)) {
		perror("robot i2c write error");
		return -1;
	}

	return 0;
}

int main() {

	uint8_t data = 0;
	int16_t data2 = 300;
	uint16_t loop = 0;
	
	// Set the I2C timeout to 20 ms (instead of 1 second). This need to be done on the "swticher" bus channel.
	int fh1 = open("/dev/i2c-1", O_RDWR);
	if(ioctl(fh1, I2C_TIMEOUT, 2) < 0) {
		perror("fail to set i2c1 timeout");
	}		
	close(fh1);	
	
	fh = open("/dev/i2c-4", O_RDWR);	// open the I2C dev driver for bus 4

	ioctl(fh, I2C_SLAVE, ROBOT_ADDRESS);

	data = 0x01;
	write_reg(fh, IR_ENABLE, 1, &data);

	while(1) {

		read_reg(fh, LEFT_STEPS, 4, temp_read);
		mot_steps[0] = temp_read[1]*256 + temp_read[0];
		mot_steps[1] = temp_read[3]*256 + temp_read[2];		
		printf("steps: %.4d, %.4d\r\n", mot_steps[0], mot_steps[1]);		
		
		for(i=0; i<8; i++) {
			read_reg(fh, PROX_SENSOR0+i, 2, &prox[i]);
			read_reg(fh, AMBIENT_SENSOR0+i, 2, &prox_amb[i]);
		}
		printf("prox: %.4d, %.4d, %.4d, %.4d, %.4d, %.4d, %.4d, %.4d\r\n", prox[0], prox[1], prox[2], prox[3], prox[4], prox[5], prox[6], prox[7]);
		printf("ambient: %.4d, %.4d, %.4d, %.4d, %.4d, %.4d, %.4d, %.4d\r\n\n", prox_amb[0], prox_amb[1], prox_amb[2], prox_amb[3], prox_amb[4], prox_amb[5], prox_amb[6], prox_amb[7]);		
		
 		data = 0x55;
		write_reg(fh, RING_LEDS, 1, &data);
		usleep(200000);
		data = 0xAA;
		write_reg(fh, RING_LEDS, 1, &data);
		usleep(200000);

	}

	close(fh);

	return 0;

}
