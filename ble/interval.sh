sudo chmod 777 /sys/kernel/debug/bluetooth/hci0/adv_min_interval
sudo chmod 777 /sys/kernel/debug/bluetooth/hci0/adv_max_interval
echo 100 > /sys/kernel/debug/bluetooth/hci0/adv_min_interval
echo 100 > /sys/kernel/debug/bluetooth/hci0/adv_max_interval