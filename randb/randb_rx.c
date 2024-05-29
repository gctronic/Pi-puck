#include <stdio.h>
#include <stdint.h> 
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <linux/i2c-dev.h> /* for I2C_SLAVE */
#include <linux/i2c.h>
#include <sys/ioctl.h>
#include <stdlib.h>
#include <unistd.h>
#include <math.h>

#define RANDB_ADDR 0x20
#define I2C_CHANNEL "/dev/i2c-12"
#define LEGACY_I2C_CHANNEL "/dev/i2c-4"

int fh;
uint8_t i = 0;
uint8_t result[6];
uint8_t dataTx = 0;
uint8_t temp_write[32];
uint8_t rab_state = 0;
uint8_t regValue[2] = {0};
uint16_t rab_data = 0;
double rab_bearing = 0.0;
uint16_t rab_range = 0;
uint16_t rab_sensor = 0;


// The following implementation uses a "restart" between a "write" and "read".
int read_reg(uint8_t reg, int count, uint8_t *data) {
	
    struct i2c_rdwr_ioctl_data packets;
    struct i2c_msg messages[2];
	int trials = 0;
	
	// S Addr Wr [A] Data(actuators) NA Sr Addr Rd [A] Data(sensors) [A] P
    messages[0].addr  = RANDB_ADDR;
    messages[0].flags = 0;
    messages[0].len   = 1;
    messages[0].buf   = &reg;
	
    messages[1].addr  = RANDB_ADDR;
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
			perror("error reading");
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

int write_reg(uint8_t reg, int count, uint8_t *data) {
	temp_write[0] = reg;
	memcpy(&temp_write[1], data, count);
	
	if(write(fh, temp_write, count+1) != (count+1)) {
		perror("robot i2c write error");
		return -1;
	}
	return 0;
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

	ioctl(fh, I2C_SLAVE, RANDB_ADDR);	// Tell the driver we want the device with address 0x20 on the I2C bus

	while(1) {

		switch(rab_state) {
			case 0:
				dataTx = 150;
				write_reg(12, 1, &dataTx); // Set range.
				dataTx = 0;
				write_reg(17, 1, &dataTx); // Onboard calculation.
				rab_state = 1;
				break;

			case 1:
				read_reg(0, 1, &regValue[0]);
				
				if(regValue[0] != 0) {
					read_reg(1, 1, &regValue[0]);
					read_reg(2, 1, &regValue[1]);
					rab_data = (((uint16_t)regValue[0])<<8) + regValue[1];
					
					read_reg(3, 1, &regValue[0]);
					read_reg(4, 1, &regValue[1]);
					rab_bearing = ((double)((((uint16_t)regValue[0])<<8) + regValue[1])) * 0.0001;
					
					read_reg(5, 1, &regValue[0]);
					read_reg(6, 1, &regValue[1]);
					rab_range = (((uint16_t)regValue[0])<<8) + regValue[1];
					
					read_reg(9, 1, &regValue[0]);
					rab_sensor = regValue[0];
					
					printf("%d %3.2f %d %d\r\n", rab_data, (rab_bearing*180.0/M_PI), rab_range, rab_sensor);
		    	}
				break;
		}
		
		usleep(20000);	// Let the bus be free for a while (refresh @ 50 Hz).

	}

	close(fh);
	
	return 0;

}
