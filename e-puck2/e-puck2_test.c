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
#include <sys/time.h>

#define ACTUATORS_SIZE (19+1) // Data + checksum.
#define SENSORS_SIZE (46+1) // Data + checksum.
#define ROBOT_ADDR 0x1F
#define I2C_CHANNEL "/dev/i2c-12"
#define LEGACY_I2C_CHANNEL "/dev/i2c-4"

int fh;
uint8_t actuators_data[ACTUATORS_SIZE];
uint8_t sensors_data[SENSORS_SIZE];
uint16_t prox[8];
uint16_t prox_amb[8];
uint16_t mic[4];
uint8_t sel;
uint8_t button;
int16_t mot_steps[2];
uint8_t tv_remote;
uint8_t actuators_state = 0;

/*
int update_robot_sensors_and_actuators() {

	int ret = 0;
	int i = 0;

	ret = write(fh, actuators_data, ACTUATORS_SIZE);
	if (ret != ACTUATORS_SIZE) {
		perror("robot i2c write error");
		return -1;
	}

	ret = read(fh, sensors_data, SENSORS_SIZE);
	if (ret != SENSORS_SIZE) {
		perror("robot i2c read error");
		return -1;
	}

	return 0;
}
*/

int update_robot_sensors_and_actuators() {
	
    struct i2c_rdwr_ioctl_data packets;
    struct i2c_msg messages[2];
	int trials = 0;
	
	// S Addr Wr [A] Data(actuators) NA Sr Addr Rd [A] Data(sensors) [A] P
    messages[0].addr  = ROBOT_ADDR;
    messages[0].flags = 0;
    messages[0].len   = ACTUATORS_SIZE;
    messages[0].buf   = actuators_data;
	
    messages[1].addr  = ROBOT_ADDR;
    messages[1].flags = I2C_M_RD;
    messages[1].len   = SENSORS_SIZE;
    messages[1].buf   = sensors_data;

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
		perror("update_robot_sensors_and_actuators: ");
		return -1;
	} else {
		return 0;
	}
}

int main() {
	uint16_t i = 0;
	uint8_t checksum = 0;
	struct timeval start_time, curr_time;	
	int32_t time_diff_us = 0;
	uint8_t counter = 0;

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

	ioctl(fh, I2C_SLAVE, ROBOT_ADDR);			// tell the driver we want the device with address 0x1F (7-bits) on the I2C bus

	while(1) {

		gettimeofday(&start_time, NULL);

		counter++;
		if(counter == 20) {
			counter = 0;
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
					actuators_data[18] = 0; 	// Settings.
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
					actuators_data[18] = 0;		// Settings.
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
					actuators_data[18] = 0; 	// Settings.
					actuators_state = 3;
					break;
				case 3:
					actuators_data[0] = 0;		// Left speed: 0
					actuators_data[1] = 0;
					actuators_data[2] = 0;		// Right speed: 0
					actuators_data[3] = 0;
					actuators_data[4] = 0; 		// Speaker sound
					actuators_data[5] = 0x0;	// LED1, LED3, LED5, LED7 on/off flag
					actuators_data[6] = 100;	// LED2 red
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
					actuators_data[18] = 0; 	// Settings.
					actuators_state = 0;
					break;
			}
		}

		checksum = 0;
		for(i=0; i<(ACTUATORS_SIZE-1); i++) {
			checksum ^= actuators_data[i];
		}
		actuators_data[ACTUATORS_SIZE-1] = checksum;

		update_robot_sensors_and_actuators();
		
    	// Verify the checksum (Longitudinal Redundancy Check) before interpreting the received sensors data.
    	checksum = 0;
    	for(i=0; i<(SENSORS_SIZE-1); i++) {
    		checksum ^= sensors_data[i];
    	}
		if(checksum == sensors_data[SENSORS_SIZE-1]) {
			for(i=0; i<8; i++) {
				prox[i] = sensors_data[i*2+1]*256+sensors_data[i*2];
			}
			printf("prox: %.4d, %.4d, %.4d, %.4d, %.4d, %.4d, %.4d, %.4d\r\n", prox[0], prox[1], prox[2], prox[3], prox[4], prox[5], prox[6], prox[7]);
			for(i=0; i<8; i++) {
				prox_amb[i] = sensors_data[16+i*2+1]*256+sensors_data[16+i*2];
			}
			printf("ambient: %.4d, %.4d, %.4d, %.4d, %.4d, %.4d, %.4d, %.4d\r\n", prox_amb[0], prox_amb[1], prox_amb[2], prox_amb[3], prox_amb[4], prox_amb[5], prox_amb[6], prox_amb[7]);			
			for(i=0; i<4; i++) {
				mic[i] = sensors_data[32+i*2+1]*256+sensors_data[32+i*2];
			}
			printf("mic: %.4d, %.4d, %.4d, %.4d\r\n", mic[0], mic[1], mic[2], mic[3]);
			printf("sel: %.2d\r\n", sensors_data[40]&0x0F);
			printf("button: %.1d\r\n", sensors_data[40]>>4);
			for(i=0; i<4; i++) {
				mot_steps[i] = sensors_data[41+i*2+1]*256+sensors_data[41+i*2];
			}
			printf("steps: %.4d, %.4d\r\n", mot_steps[0], mot_steps[1]);
			printf("tv: %.2d\r\n", sensors_data[45]);

			printf("\r\n");
		} else {
			printf("wrong checksum (%02x != %02x)\r\n", sensors_data[ACTUATORS_SIZE-1], checksum);
		}
		
		// Communication frequency @ 20 Hz.
		gettimeofday(&curr_time, NULL);
		time_diff_us = (curr_time.tv_sec * 1000000 + curr_time.tv_usec) - (start_time.tv_sec * 1000000 + start_time.tv_usec);		
		if(time_diff_us < 50000) {
			usleep(50000 - time_diff_us);
		}

	}

	close(fh);
	
	return 0;

}
