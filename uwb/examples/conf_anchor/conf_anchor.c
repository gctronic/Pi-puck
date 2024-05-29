/*! ------------------------------------------------------------------------------------------------------------------
 * @file    conf_anchor.c
 * @brief   Setup the node as anchor.
 *          In this example, the steps to configure the Anchor include:
 *          Anchor mode, position, PANID.
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
	const char label_set[] = "anchor1";
	
	printf("Initializing...\n");
	//dwm_deinit();
	dwm_init();
	
	printf("Reset...\n");
	//dwm_factory_reset();
	dwm_reset();
	HAL_Delay(1500); // Wait 1.5 seconds
	
	// Setup anchor mode configurations
	dwm_cfg_anchor_t cfg_an;    
	cfg_an.initiator = 0;
	cfg_an.bridge = 1;
	cfg_an.uwb_bh_routing = DWM_UWB_BH_ROUTING_AUTO; 
	cfg_an.common.enc_en = 0;
	cfg_an.common.led_en = 0;
	cfg_an.common.ble_en = 1;
	cfg_an.common.uwb_mode = DWM_UWB_MODE_ACTIVE;; //DWM_UWB_MODE_PASSIVE; //DWM_UWB_MODE_ACTIVE;
	cfg_an.common.fw_update_en = 0;
	dwm_cfg_anchor_set(&cfg_an);
	
	// Setup anchor position (fixed)
	dwm_pos_t pos_set;
	pos_set.qf = 100;
	pos_set.x = 0; // Given in mm
	pos_set.y = 0; // Given in mm
	pos_set.z = 0; // Given in mm
	dwm_pos_set(&pos_set);
	
	// Setup PANID
	panid = 0xBB11;
	dwm_panid_set(panid);
	
	// Give a name
	dwm_label_write((uint8_t *)label_set, strlen(label_set));
   
	// Reset to apply modifications
	dwm_reset();
	HAL_Delay(1500); // Wait 1.5 seconds   
   
	printf("Done\r\n");
	
	return 0;
}



