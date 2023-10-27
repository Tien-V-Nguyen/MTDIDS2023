# Runned on boot
import gc
from network import Bluetooth
from network import WLAN
import pycom
import micropython

# Enable automatic garbage collection
gc.enable()

# Disable Wi-Fi on boot
if pycom.wifi_on_boot() == True:
  pycom.wifi_on_boot(False)

# Lora and sigfox auto disabled already

# Somewhat needed to disable wlan to disable bluetooth (bug?)
wlan = WLAN()
wlan.deinit()

bluetooth = Bluetooth()
bluetooth.deinit()

# Disable the pycom heartbeat
pycom.heartbeat(False)

# Enable wlan again
wlan.init()

print("\nAvailable memory:")
micropython.mem_info()
print("\n")