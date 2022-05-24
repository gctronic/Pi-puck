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

#define I2C_CHANNEL "/dev/i2c-12"
#define LEGACY_I2C_CHANNEL "/dev/i2c-4"

#define NUM_SAMPLES_CALIBRATION 20
//#define GRAVITY_LSM330 16384    // 1 g for 16 bits accelerometer
#define GRAVITY_MPU9250 16384    // ### to define ...1 g for 16 bits accelerometer
#define AK8963_ADDRESS  0x0C   // Address of magnetometer
#define AK8963_XOUT_L    0x03  // data

#define MPU9250_ADDRESS_AD1_0 0x68  // Device address when AD1 = 0
#define MPU9250_ADDRESS_AD1_1 0x69

#define INT_STATUS         0x3A
#define ACCEL_XOUT_H       0x3B
#define TEMP_OUT_H         0x41
#define GYRO_XOUT_H        0x43

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
uint8_t imu_addr = MPU9250_ADDRESS_AD1_0;

// The chip has two alternative addresses based on the AD1 pin.
void mpu9250_change_addr(void) {
	if(imu_addr == MPU9250_ADDRESS_AD1_0) {
		imu_addr = MPU9250_ADDRESS_AD1_1;
	} else {
		imu_addr = MPU9250_ADDRESS_AD1_0;
	}
	ioctl(fh, I2C_SLAVE, imu_addr);
}

int read_reg(int file, uint8_t reg, int count, uint8_t *data) {

	if(write(file, &reg, 1) != 1) {
		mpu9250_change_addr();
		if(write(file, &reg, 1) != 1) {
			perror("write before read");
			return -1;
		}
	}

	if(read(file, data, count) != count) {
		mpu9250_change_addr();
		if(read(file, data, count) != count) {
			printf("count=%d\n", count);
			perror("read");
			return -1;
		}
	}

	return 0;
}

void calibrateAcc() {
	int samplesCount=0;
	// reset and send configuration first?
	for(i=0; i<NUM_SAMPLES_CALIBRATION; i++) {
		if(read_reg(fh, ACCEL_XOUT_H, 6, accData) == 0) {	// for MPU9250 set just the address also for a multiple read with autoincrement
			accSum[0] += (int16_t)(accData[1] + (accData[0]<<8)); // MPU9250 big-endian
			accSum[1] += (int16_t)(accData[3] + (accData[2]<<8));
			accSum[2] += (int16_t)(accData[5] + (accData[4]<<8)) - GRAVITY_MPU9250; //!#######
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
	// reset and send configuration first?
	for(i=0; i<NUM_SAMPLES_CALIBRATION; i++) {
		if(read_reg(fh, GYRO_XOUT_H, 6, gyroData) == 0) {	// // for MPU9250 set just the address also for a multiple read with autoincrement
			gyroSum[0] += (int16_t)(gyroData[1] + (gyroData[0]<<8)); // MPU9250 big-endian
			gyroSum[1] += (int16_t)(gyroData[3] + (gyroData[2]<<8));
			gyroSum[2] += (int16_t)(gyroData[5] + (gyroData[4]<<8));
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

	printf("0 for accelerometer, 1 for gyroscope:");
	scanf("%d", &choice);

	ioctl(fh, I2C_SLAVE, imu_addr);

	if(choice == 0) {
		calibrateAcc();
	} else if(choice == 1) {
		calibrateGyro();		
	}

	while(1) {

		read_reg(fh, ACCEL_XOUT_H, 6, accData);	
		read_reg(fh, GYRO_XOUT_H, 6, gyroData);		

		accValue[0] = (accData[1] + (accData[0]<<8)) - accOffset[0];// MPU9250 big-endian
		accValue[1] = (accData[3] + (accData[2]<<8)) - accOffset[1];
		accValue[2] = (accData[5] + (accData[4]<<8)) - accOffset[2];

		gyroValue[0] = (gyroData[1] + (gyroData[0]<<8)) - gyroOffset[0];
		gyroValue[1] = (gyroData[3] + (gyroData[2]<<8)) - gyroOffset[1];
		gyroValue[2] = (gyroData[5] + (gyroData[4]<<8)) - gyroOffset[2];

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
