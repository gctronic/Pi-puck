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

#define ROBOT_ADDR 0x1F
#define I2C_CHANNEL "/dev/i2c-12"
#define LEGACY_I2C_CHANNEL "/dev/i2c-4"

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
uint8_t temp_read[32];

int write_reg(uint8_t reg, int count, uint8_t *data) {
	temp_write[0] = reg;
	memcpy(&temp_write[1], data, count);
	
	if(write(fh, temp_write, count+1) != (count+1)) {
		perror("write_reg");
		return -1;
	}

	return 0;
}

// The following implementation uses a "restart" between a "write" and "read".
int read_reg(uint8_t reg, int count, uint8_t *data) {
	
    struct i2c_rdwr_ioctl_data packets;
    struct i2c_msg messages[2];
	int trials = 0;
	
	// S Addr Wr [A] Data(actuators) NA Sr Addr Rd [A] Data(sensors) [A] P
    messages[0].addr  = ROBOT_ADDR;
    messages[0].flags = 0;
    messages[0].len   = 1;
    messages[0].buf   = &reg;
	
    messages[1].addr  = ROBOT_ADDR;
    messages[1].flags = I2C_M_RD;
    messages[1].len   = count;
    messages[1].buf   = data;

    packets.msgs      = messages;
    packets.nmsgs     = 2;
	
	// Form the tests it was noticed that sometimes (about 1/1000) the communication give a "timeout error" followed by "remote I/O" error.
	// Thus 3 retrials are done in case of errors.
	while(trials < 3) {
		if(ioctl(fh, I2C_RDWR, &packets) < 0) {		
			trials++;
			continue;
		}
		break;
	}

	if(trials > 2) {
		perror("read_reg: ");
		return -1;
	} else {
		return 0;
	}
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
	
	fh = open(I2C_CHANNEL, O_RDWR);
	if(fh < 0) { // Try with bus number used in older kernel
		fh = open(LEGACY_I2C_CHANNEL, O_RDWR);	
		if(fh < 0) {
			perror("Cannot open I2C device");
			return -1;
		}
	}

	ioctl(fh, I2C_SLAVE, ROBOT_ADDR);

	data = 0x01;
	write_reg(IR_ENABLE, 1, &data);

	while(1) {

		read_reg(LEFT_STEPS, 4, temp_read);
		mot_steps[0] = temp_read[1]*256 + temp_read[0];
		mot_steps[1] = temp_read[3]*256 + temp_read[2];		
		printf("steps: %.4d, %.4d\r\n", mot_steps[0], mot_steps[1]);		
		
		for(i=0; i<8; i++) {
			read_reg(PROX_SENSOR0+i, 2, (uint8_t*)&prox[i]);
			read_reg(AMBIENT_SENSOR0+i, 2, (uint8_t*)&prox_amb[i]);
		}
		printf("prox: %.4d, %.4d, %.4d, %.4d, %.4d, %.4d, %.4d, %.4d\r\n", prox[0], prox[1], prox[2], prox[3], prox[4], prox[5], prox[6], prox[7]);
		printf("ambient: %.4d, %.4d, %.4d, %.4d, %.4d, %.4d, %.4d, %.4d\r\n\n", prox_amb[0], prox_amb[1], prox_amb[2], prox_amb[3], prox_amb[4], prox_amb[5], prox_amb[6], prox_amb[7]);		
		
 		data = 0x55;
		write_reg(RING_LEDS, 1, &data);
		usleep(200000);
		data = 0xAA;
		write_reg(RING_LEDS, 1, &data);
		usleep(200000);

	}

	close(fh);

	return 0;

}
