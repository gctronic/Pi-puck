import sys
import dbus, dbus.mainloop.glib
from gi.repository import GObject
from gi.repository import GLib
from example_advertisement import Advertisement
from example_advertisement import register_ad_cb, register_ad_error_cb
from example_gatt_server import Service, Characteristic
from example_gatt_server import register_app_cb, register_app_error_cb
import array
import time
import threading
 
BLUEZ_SERVICE_NAME =		   'org.bluez'
DBUS_OM_IFACE =				   'org.freedesktop.DBus.ObjectManager'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
GATT_MANAGER_IFACE =		   'org.bluez.GattManager1'
GATT_CHRC_IFACE =			   'org.bluez.GattCharacteristic1'
UART_SERVICE_UUID =			   '0000abf0-0000-1000-8000-00805f9b34fb' #'6e400001-b5a3-f393-e0a9-e50e24dcca9e'
UART_RX_CHARACTERISTIC_UUID =  '0000abf1-0000-1000-8000-00805f9b34fb' #'6e400002-b5a3-f393-e0a9-e50e24dcca9e'
UART_TX_CHARACTERISTIC_UUID =  '0000abf2-0000-1000-8000-00805f9b34fb' #'6e400003-b5a3-f393-e0a9-e50e24dcca9e'
LOCAL_NAME =				   'e-puck2_pi-puck'
mainloop = None
adv = None

tx_characteristic = None
bt_received = False
bt_rx_data = None
stop_bt_tx_rx_thread = False
 
class TxCharacteristic(Characteristic):
	def __init__(self, bus, index, service):
		Characteristic.__init__(self, bus, index, UART_TX_CHARACTERISTIC_UUID,
								['notify'], service)
		self.notifying = False
		#GObject.io_add_watch(sys.stdin, GObject.IO_IN, self.on_console_input)
 
#	def on_console_input(self, fd, condition):
#		#self.send_tx(array.array('H', [1,2,3,4,5,6,7,8]))
#		s = fd.readline()
#		#if s.isspace():
#		#	pass
#		#else:
#		#	self.send_tx(s)
#		return True
 
	def send_tx(self, s):
		if not self.notifying:
			return
		#value = []
		#for c in s:
		#	value.append(dbus.Byte(c.encode()))
		
		#for loop in range(0,100):
		#	value = []
		#	#for i in range(0, 16):
		#	#	value.append(dbus.Byte(i+loop))
		#	for i in s:
		#		value.append(dbus.Byte(i))
		#	self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])
		#	time.sleep(0.030)
			
		value = []
		for i in s:
			value.append(dbus.Byte(i))
		self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])
 
	def StartNotify(self):
		if self.notifying:
			return
		self.notifying = True
 
	def StopNotify(self):
		if not self.notifying:
			return
		self.notifying = False
 
class RxCharacteristic(Characteristic):
	def __init__(self, bus, index, service):
		Characteristic.__init__(self, bus, index, UART_RX_CHARACTERISTIC_UUID,
								['write-without-response'], service)
 
	def WriteValue(self, value, options):
		global bt_rx_data
		global bt_received
		bt_received = True
		bt_rx_data = value
		#print(value)
		#print('value')
		#for v in value:
		#	print v
		#print('remote: {}'.format(bytearray(value).decode()))
 
class UartService(Service):
	def __init__(self, bus, index):
		global tx_characteristic		
		Service.__init__(self, bus, index, UART_SERVICE_UUID, True)
		tx_characteristic = TxCharacteristic(bus, 0, self)
		self.add_characteristic(tx_characteristic)
		#self.add_characteristic(TxCharacteristic(bus, 0, self))
		self.add_characteristic(RxCharacteristic(bus, 1, self))
 
class Application(dbus.service.Object):
	def __init__(self, bus):
		self.path = '/'
		self.services = []
		dbus.service.Object.__init__(self, bus, self.path)
 
	def get_path(self):
		return dbus.ObjectPath(self.path)
 
	def add_service(self, service):
		self.services.append(service)
 
	@dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
	def GetManagedObjects(self):
		response = {}
		for service in self.services:
			response[service.get_path()] = service.get_properties()
			chrcs = service.get_characteristics()
			for chrc in chrcs:
				response[chrc.get_path()] = chrc.get_properties()
		return response
 
class UartApplication(Application):
	def __init__(self, bus):
		Application.__init__(self, bus)
		self.add_service(UartService(bus, 0))
 
class UartAdvertisement(Advertisement):
	def __init__(self, bus, index):
		Advertisement.__init__(self, bus, index, 'peripheral')
		self.add_service_uuid(UART_SERVICE_UUID)
		self.add_local_name(LOCAL_NAME)
		self.include_tx_power = True
 
def find_adapter(bus):
	remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'), DBUS_OM_IFACE)
	objects = remote_om.GetManagedObjects()
	for o, props in objects.items():
		for iface in (LE_ADVERTISING_MANAGER_IFACE, GATT_MANAGER_IFACE):
			if iface not in props:
				continue
		return o
	return None


class BtMainTask(threading.Thread):
	def __init__(self,):		
		threading.Thread.__init__(self)
	
	def run(self):
		global mainloop
		global adv
		global stop_bt_tx_rx_thread
		
		try:
			mainloop.run()
		except KeyboardInterrupt:		
			#print("BT ctrl+c");
			stop_bt_tx_rx_thread = True
			adv.Release()
			mainloop.quit()
			#raise
bt_main_task = BtMainTask()

class BtRxTxTask(threading.Thread):
	def __init__(self,):		
		threading.Thread.__init__(self)
	
	def run(self):
		global bt_received
		global bt_rx_data
		global tx_characteristic
		global stop_bt_tx_rx_thread
		temp = 0	
		
		while not stop_bt_tx_rx_thread:
			if(bt_received):
				bt_received = False
				#print(bt_rx_data)
				if(int(bt_rx_data[0])==0 and int(bt_rx_data[1])==255 and int(bt_rx_data[2])==0 and int(bt_rx_data[3])==255):
					print('backward')
				if(int(bt_rx_data[0])==255 and int(bt_rx_data[1])==0 and int(bt_rx_data[2])==255 and int(bt_rx_data[3])==0):
					print('forward')
				if(int(bt_rx_data[0])==0 and int(bt_rx_data[1])==255 and int(bt_rx_data[2])==255 and int(bt_rx_data[3])==0):
					print('left')
				if(int(bt_rx_data[0])==255 and int(bt_rx_data[1])==0 and int(bt_rx_data[2])==0 and int(bt_rx_data[3])==255):
					print('right')
				if(int(bt_rx_data[0])==0 and int(bt_rx_data[1])==0 and int(bt_rx_data[2])==0 and int(bt_rx_data[3])==0):
					print('stop')
			
			tx_characteristic.send_tx([temp, temp+1, temp+2, temp+3, temp+4, temp+5, temp+6, temp+7, temp+8, temp+9, temp+10, temp+11, temp+12, temp+13, temp+14, temp+15])
			
			if temp < 100:
				temp = temp + 1
			else:
				temp = 0
			time.sleep(0.1)
			#print('blabla')		
bt_rx_tx_task = BtRxTxTask()

def _print_tree(bus):
	"""Print tree of all bluez objects, useful for debugging."""
	remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
							   DBUS_OM_IFACE)
	objects = remote_om.GetManagedObjects()
	
	for path in objects.keys():
		print("[ %s ]" % (path))
		interfaces = objects[path]
		for interface in interfaces.keys():
			if interface in ["org.freedesktop.DBus.Introspectable","org.freedesktop.DBus.Properties"]:
				continue
			print("    %s" % (interface))
			properties = interfaces[interface]
			for key in properties.keys():
				print("      %s = %s" % (key, properties[key]))		
		

def clear_cached_data(bus):
	remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'), DBUS_OM_IFACE)
	dbus_objects = remote_om.GetManagedObjects()
	
	"""Return a list of all bluez DBus objects that implement the requested
	interface name and are under the specified path.  The default is to
	search devices under the root of all bluez objects.
	"""
	# Iterate through all the objects in bluez's DBus hierarchy and return
	# any that implement the requested interface under the specified path.
	parent_path = '/org/bluez'
	interface = 'org.bluez.Device1'
	objects = []
	for opath, interfaces in dbus_objects.items():
		if interface in interfaces.keys() and opath.lower().startswith(parent_path):
			objects.append(bus.get_object('org.bluez', opath))

	"""Clear any internally cached BLE device data.  Necessary in some cases
	to prevent issues with stale device data getting cached by the OS.
	"""
	# Go through and remove any device that isn't currently connected.
	for device in objects:
		## Skip any connected device.
		#props.Get('org.bluez.Device1', 'Connected')
		#	continue
		# Remove this device.  First get the adapter associated with the device.
		adapter = dbus.Interface(bus.get_object('org.bluez', '/org/bluez/hci0'), 'org.bluez.Adapter1')
		# Now call RemoveDevice on the adapter to remove the device from
		# bluez's DBus hierarchy.
		dev = dbus.Interface(device, 'org.bluez.Device1')
		adapter.RemoveDevice(dev.object_path)
		
def main():
	global tx_characteristic
	global bt_received
	global bt_rx_data
	global mainloop
	global adv
	
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	bus = dbus.SystemBus()
	
 	#_print_tree(bus)
	clear_cached_data(bus)
	#_props = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter), 'org.freedesktop.DBus.Properties')
	#_props.Set('org.bluez.Adapter1', 'Pairable', False)
	#print("\n\n\n\n\n\n\n")
	#_print_tree(bus)
	#time.sleep(3)	
	
	adapter = find_adapter(bus)
	if not adapter:
		print('BLE adapter not found')
		return
 
	service_manager = dbus.Interface(
								bus.get_object(BLUEZ_SERVICE_NAME, adapter),
								GATT_MANAGER_IFACE)
	ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
								LE_ADVERTISING_MANAGER_IFACE)		
		
	app = UartApplication(bus)
	adv = UartAdvertisement(bus, 0)
 
	mainloop = GLib.MainLoop() #GObject.MainLoop()
 
	service_manager.RegisterApplication(app.get_path(), {},
										reply_handler=register_app_cb,
										error_handler=register_app_error_cb)
	ad_manager.RegisterAdvertisement(adv.get_path(), {},
									 reply_handler=register_ad_cb,
									 error_handler=register_ad_error_cb)
									 
	bt_rx_tx_task.start()
	bt_main_task.start()
 
if __name__ == '__main__':
	main()