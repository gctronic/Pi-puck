from decawave_1001_rjg import Decawave1001Driver

if __name__ == '__main__':
    driver = Decawave1001Driver(None, 0)
    driver.config_tag(True); # BLE enabled
    driver.set_pan_id(0xBB11)
    driver.set_label("robot-tag")
    driver.reset()