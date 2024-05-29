/*! ------------------------------------------------------------------------------------------------------------------
 * @file    conf_tag.c
 * @brief   Setup the node as a tag and print out the RTLS info.
 *          In this example, the steps to configure the Tag include:
 *          Tag mode, PANID, update rate.
 *
 */

#include <string.h>
#include "dwm_api.h"
#include "hal.h"
#include <sys/time.h>
#include<unistd.h>

int main(int argc, char*argv[])
{ 
	uint16_t panid;
	uint16_t ur_set;
	uint16_t ur_s_set;
	const char label_set[] = "robot-tag";
  
	printf("Initializing...\n");
	//dwm_deinit();
	dwm_init();

	printf("Reset...\n");
	//dwm_factory_reset();
	dwm_reset();
	HAL_Delay(1500); // Wait 1.5 seconds
   
	// Setup tag mode configurations
	dwm_cfg_tag_t cfg_tag;
	cfg_tag.stnry_en = 0;
	cfg_tag.low_power_en = 0; 
	cfg_tag.meas_mode = DWM_MEAS_MODE_TWR;
	cfg_tag.loc_engine_en = 1;
	cfg_tag.common.enc_en = 0;
	cfg_tag.common.led_en = 0;
	cfg_tag.common.ble_en = 1;
	cfg_tag.common.uwb_mode = DWM_UWB_MODE_ACTIVE;
	cfg_tag.common.fw_update_en = 0;
	dwm_cfg_tag_set(&cfg_tag);
	
	// Setup tag update rate
	ur_s_set = ur_set = 1; // every 100 ms
	dwm_upd_rate_set(ur_set, ur_s_set);
	
	// Setup PANID
	panid = 0xBB11;
	dwm_panid_set(panid);
	
	// Give a name
	dwm_label_write((uint8_t *)label_set, strlen(label_set));
   
	// Reset to apply modifications
	dwm_reset();
	HAL_Delay(1500); // Wait 1.5 seconds      
   
	printf("Done.\n");
	
	return 0;
}



