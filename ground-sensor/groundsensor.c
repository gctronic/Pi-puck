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

int fh;
uint8_t i = 0;
uint8_t result[6];

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
/*
int read_reg(int file, uint8_t reg, int count) {
	int8_t data[2];

	if (count < 1 || count > 2)
		return -1;

	data[0] = reg;

	if (write(file, &data, 1) != 1) {
		perror("write before read");
		return -1;
	}

	data[1] = 0;

	if (read(file, &data, count) != count) {
		perror("read");
		return -1;
	}

	return (data[1] << 8) + data[0];
}
*/
int main() {

	fh = open("/dev/i2c-4", O_RDWR);	// open the I2C dev driver for bus 3

	ioctl(fh, I2C_SLAVE, 0x60);			// tell the driver we want the device with address 0x60 on the I2C bus

	while(1) {

		for(i=0; i<6; i++) {				// read the first 6 registers => 3 sensors value
			read_reg(fh, i, 1, &result[i]);	// read 1 byte register
		}

		printf("%d,%d,%d\n", result[0]*256+result[1], result[2]*256+result[3], result[4]*256+result[5]);

		usleep(20000);	// let the bus be free for a while

	}

	close(fh);
	
	return 0;

}
