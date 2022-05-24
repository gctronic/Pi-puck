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

#define NUM_SAMPLES_CALIBRATION 20
#define GRAVITY_LSM330 16384    // 1 g for 16 bits accelerometer

#define I2C_CHANNEL "/dev/i2c-12"
#define LEGACY_I2C_CHANNEL "/dev/i2c-4"

int fh;
uint8_t i = 0;
uint8_t accData[6];
uint8_t gyroData[6];
uint8_t temperatureData;
int16_t accValue[3];
int32_t accSum[3] = {0, 0, 0};
int16_t accOffset[3] = {0, 0, 0};
int16_t gyroValue[3];
int32_t gyroSum[3] = {0, 0, 0};
int16_t gyroOffset[3] = {0, 0, 0};
int choice;
uint8_t temp_write[32];

int read_reg(int file, uint8_t reg, int count, uint8_t *data) {

	if (write(file, &reg, 1) != 1) {
		perror("write before read");
		return -1;
	}

	if (read(file, data, count) != count) {
		printf("count=%d\n", count);
		perror("read");
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

void initIMU(void) {
	uint8_t value = 0;
	
	ioctl(fh, I2C_SLAVE, 0x1E); // accelerometer
	
    // REG5_A (0x20) =  ODR (4) | BDU (1)   | Axes enabling (3)
    //                  0 1 1 0 |   1       | 1 1 1             => 0x6F => 100 Hz | BDU | x, y, z axes enabled
    //                  0 1 1 1 |   1       | 1 1 1             => 0x7F => 400 Hz | BDU | x, y, z axes enabled
    //                  1 0 0 0 |   1       | 1 1 1             => 0x8F => 800 Hz | BDU | x, y, z axes enabled
    //                  1 0 0 1 |   1       | 1 1 1             => 0x9F => 1600 Hz | BDU | x, y, z axes enabled
	value = 0x9F;
    write_reg(fh, 0x20, 1, &value);
    // REG7_A (0x25) = 0 1 (enable fifo, needed?) 0 1 (auto increment address on multi read) 0 0 0 0 => 0x50
	value = 0x50;
    write_reg(fh, 0x25, 1, &value);
    // REG6_A (0x24) => default +- 2g
    // FIFO_CTRL_REG_A (0x2E) => default bypass mode

	ioctl(fh, I2C_SLAVE, 0x6A); // gyroscope
    // CTRL_REG1_G (0x20) = ODR and cut-off (4) | mode (1)  | Axes enabling (3)
    //                      0 0 1 1             |   1       | 1 1 1             => 0x3F => odr=95Hz, cut-off=25Hz | normal | x, y, z axes enabled
    //                      1 1 0 0             |   1       | 1 1 1             => 0xCF => odr=760Hz, cut-off=30Hz | normal | x, y, z axes enabled
	value = 0xCF;
    write_reg(fh, 0x20, 1, &value);
    // CTRL_REG2_G (0x21) => normal mode; HPF=51.4 Hz (not used anyway)
	value = 0x20;
    write_reg(fh, 0x21, 1, &value);
    // CTRL_REG4_G (0x23) => 250 dps (degrees per second) and continuous update
	value = 0x00;
    write_reg(fh, 0x23, 1, &value);

    // CTRL_REG5_G (0x24) => enable fifo (needed?)
    //write_reg(fh, 0x24, 0x40);
    //write_reg(fh, 0x24, 0x50);    // LPF1
    //write_reg(fh, 0x24, 0x51);    // LPF1 + HPF
    //write_reg(fh, 0x24, 0x42);    // LPF1 + LPF2
    //write_reg(fh, 0x24, 0x52);    // LPF1 + HPF + LPF2

}

void calibrateAcc() {
	int samplesCount=0;
	ioctl(fh, I2C_SLAVE, 0x1E);				// gyroscope
	for(i=0; i<NUM_SAMPLES_CALIBRATION; i++) {
		if(read_reg(fh, 0x28|0x80, 6, accData) == 0) {	// add "|0x80" on the regsiter to tell the device is a consecutive
			accSum[0] += (int16_t)(accData[0] + (accData[1]<<8));
			accSum[1] += (int16_t)(accData[2] + (accData[3]<<8));
			accSum[2] += (int16_t)(accData[4] + (accData[5]<<8)) - GRAVITY_LSM330;
			samplesCount++;
			//printf("acc sums: x=%d, y=%d, z=%d (samples=%d)\n", accSum[0], accSum[1], accSum[2], samplesCount);
		}
	}
	accOffset[0] = (int16_t)((float)accSum[0]/(float)samplesCount);
	accOffset[1] = (int16_t)((float)accSum[1]/(float)samplesCount);
	accOffset[2] = (int16_t)((float)accSum[2]/(float)samplesCount);
	printf("acc offsets: x=%d, y=%d, z=%d (samples=%d)\n", accOffset[0], accOffset[1], accOffset[2], samplesCount);

}

void calibrateGyro() {
	int samplesCount=0;
	ioctl(fh, I2C_SLAVE, 0x6A);				// gyroscope
	for(i=0; i<NUM_SAMPLES_CALIBRATION; i++) {
		if(read_reg(fh, 0x28|0x80, 6, gyroData) == 0) {	// add "|0x80" on the regsiter to tell the device is a consecutive
			gyroSum[0] += (int16_t)(gyroData[0] + (gyroData[1]<<8));
			gyroSum[1] += (int16_t)(gyroData[2] + (gyroData[3]<<8));
			gyroSum[2] += (int16_t)(gyroData[4] + (gyroData[5]<<8));
			samplesCount++;
			//printf("gyro sums: x=%d, y=%d, z=%d (samples=%d)\n", gyroSum[0], gyroSum[1], gyroSum[2], samplesCount);
		}
	}
	gyroOffset[0] = (int16_t)((float)gyroSum[0]/(float)samplesCount);
	gyroOffset[1] = (int16_t)((float)gyroSum[1]/(float)samplesCount);
	gyroOffset[2] = (int16_t)((float)gyroSum[2]/(float)samplesCount);
	printf("gyro offsets: x=%d, y=%d, z=%d (samples=%d)\n", gyroOffset[0], gyroOffset[1], gyroOffset[2], samplesCount);
}

int main() {

	fh = open(I2C_CHANNEL, O_RDWR);
	if(fh < 0) { // Try with bus number used in older kernel
		fh = open(LEGACY_I2C_CHANNEL, O_RDWR);	
		if(fh < 0) {
			perror("Cannot open I2C device");
			return -1;
		}
	}

	initIMU();
	
	printf("0 for accelerometer, 1 for gyroscope:");
	scanf("%d", &choice);

	if(choice == 0) {
		calibrateAcc();
	} else if(choice == 1) {
		calibrateGyro();		
	}

	while(1) {

		ioctl(fh, I2C_SLAVE, 0x1E);				// accelerometer
		read_reg(fh, 0x28|0x80, 6, accData);	// add "|0x80" on the regsiter to tell the device is a consecutive read 	

		ioctl(fh, I2C_SLAVE, 0x6A);				// gyroscope
		read_reg(fh, 0x28|0x80, 6, gyroData);	// add "|0x80" on the regsiter to tell the device is a consecutive read				

		accValue[0] = (accData[0] + (accData[1]<<8)) - accOffset[0];
		accValue[1] = (accData[2] + (accData[3]<<8)) - accOffset[1];
		accValue[2] = (accData[4] + (accData[5]<<8)) - accOffset[2];

		gyroValue[0] = (gyroData[0] + (gyroData[1]<<8)) - gyroOffset[0];
		gyroValue[1] = (gyroData[2] + (gyroData[3]<<8)) - gyroOffset[1];
		gyroValue[2] = (gyroData[4] + (gyroData[5]<<8)) - gyroOffset[2];

		if(choice == 0) {
			printf("x=%+.5d (%+5.3f g), y=%+.5d (%+5.3f g), z=%+.5d (%+5.3f g)\r\n", accValue[0], (float)accValue[0]/32768.0*2.0,
 accValue[1], (float)accValue[1]/32768.0*2.0, accValue[2], (float)accValue[2]/32768.0*2.0);
		} else if(choice == 1) {
	        printf("x=%+.5d (%+8.3f dps), y=%+.5d (%+8.3f dps), z=%+.5d (%+8.3f dps)\r\n", gyroValue[0], (float)gyroValue[0]/32768.0*250.0, gyroValue[1], (float)gyroValue[1]/32768.0*250.0, gyroValue[2], (float)gyroValue[2]/32768.0*250.0);
		} else {
			break;
		}
 
		usleep(50000);	// let the bus be free for a while

	}

	close(fh);

	return 0;

}
