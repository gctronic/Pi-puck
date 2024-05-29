/*! ------------------------------------------------------------------------------------------------------------------
 * @file    tag_get_pos.c
 * @brief   Print out the RTLS info.
 *
 */

#include <string.h>
#include "dwm_api.h"
#include "hal.h"
#include <sys/time.h>
#include<unistd.h>

struct timeval tv;
uint64_t ts_curr = 0;
uint64_t ts_last = 0;
volatile uint8_t data_ready;
   
int get_loc(void)
{
   int rv, i; 
   
   dwm_loc_data_t loc;
   dwm_pos_t pos;
   loc.p_pos = &pos;
   rv = dwm_loc_get(&loc);
   
   gettimeofday(&tv,NULL);      
      
   if(rv == RV_OK)
   {
      printf("TAG: ts:%ld.%06ld [%5d,%5d,%5d,%3u]\r\n", tv.tv_sec, tv.tv_usec, loc.p_pos->x, loc.p_pos->y, loc.p_pos->z, loc.p_pos->qf);
		printf("ANCHORS:\r\n");
      for (i = 0; i < loc.anchors.dist.cnt; ++i) 
      {
         printf("#%u) ", i);
         printf("addr:0x%08x, ", loc.anchors.dist.addr[i]);
         if (i < loc.anchors.an_pos.cnt) 
         {
            printf("pos: [%5d,%5d,%5d,%3u], ", loc.anchors.an_pos.pos[i].x,
                  loc.anchors.an_pos.pos[i].y,
                  loc.anchors.an_pos.pos[i].z,
                  loc.anchors.an_pos.pos[i].qf);
         }
         printf("dist=%5u, qf=%3u", loc.anchors.dist.dist[i], loc.anchors.dist.qf[i]);
		 printf("\r\n");
      }
      printf("\r\n");
   }   
   
   return rv;
}

void get_anchor_list(void) {
   dwm_anchor_list_t list;
   int rv, i;
   rv = dwm_anchor_list_get(&list);
   if(rv == RV_OK) {
      for (i = 0; i < list.cnt; ++i) {
         printf("%d. id=0x%04X pos=[%ld,%ld,%ld] rssi=%d seat=%u neighbor=%d\n", i,
         list.v[i].node_id,
         list.v[i].x,
         list.v[i].y,
         list.v[i].z,
         list.v[i].rssi,
         list.v[i].seat,
         list.v[i].neighbor_network);
      }
   } else {
      printf("get_anchor_list err = %d\r\n", rv);
   }
}

void get_position(void) {
   dwm_pos_t pos;
   dwm_pos_get(&pos);
   printf("pos: [%5d,%5d,%5d,%3u]\r\n", pos.x, pos.y, pos.z, pos.qf);
}

void get_bh_status(void) {
   bh_status_t p_bh_status;
   int rv;
   rv = dwm_bh_status_get(&p_bh_status);
   if(rv == RV_OK) {
      printf("origin_cnt = %d\r\n", p_bh_status.origin_cnt);
   } else {
      printf("get_bh_status err = %d\r\n", rv);
   }

}

int main(int argc, char*argv[])
{   
   int rv = 0;
   dwm_status_t status;
   
   dwm_init();
   
	while(1)
	{
		rv = dwm_status_get(&status);
		if (rv == DWM_OK) {
			//if(status.loc_data == 1)
			//{
				get_loc();
				get_anchor_list();
            get_position();
            get_bh_status();
			//}
		}
		HAL_Delay(500);		
	}
      
	return 0;
}



