sudo cp config.txt /boot/config.txt
sudo rm /boot/overlays/pi-puck-*
sudo cp pi-puck-*.dtbo /boot/overlays/
sync
sudo reboot
