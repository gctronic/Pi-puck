from decawave_1001_rjg import Decawave1001Driver

if __name__ == '__main__':
    driver = Decawave1001Driver(None, 0)
    driver.config_anchor(True, True); # Anchor, BLE enabled
    driver.set_pos(2000, 2000, 0) # given in mm
    driver.set_pan_id(0xBB11)
    driver.set_label("anchorX")
    driver.reset()