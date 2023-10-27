# Firmware : Using the custom firmware with ICMP disabled
# Pycom MicroPython 1.20.2.rc7 [v1.20.1.r2-142-g6d0127037-dirty] on 2020-05-08; LoPy with ESP32
import machine
from network import WLAN
import utime as time
from coapExperiment.coap_experiment import CoapExperiment

# Configurations
_WIFI_SSID = "IMTIIoT"  # Wi-Fi SSID Name
_WIFI_PASS = "pokemon151"  #Wi-Fi Password (... in the clear, beware!)
_NTP_SERVER = "132.163.96.4"  # NTP Server IP


def connect_to_network(wlan):
    """
    Connects to Wi-Fi Network
    Warning: we used firmware MicroPython 1.18.2.r7 [v1.8.6-849-df9f237], newer FW versions have an
    issue with the Wi-FI driver as of 29/02/2020 (Scans OK but can not connect)

    :return: True if we could connect to the Wi-Fi or otherwise False.
    """

    # Scanning for networks
    nets = wlan.scan()
    for net in nets:
        print(net.ssid)
        if net.ssid == _WIFI_SSID:
            print("Found the network")
            wlan.connect(net.ssid, auth=(net.sec, _WIFI_PASS), timeout=5000)
            while not wlan.isconnected():
                machine.idle()
            print("WLAN connection to", _WIFI_SSID, "succeeded!")
            break

    # The assigned IP address for the Pycom
    print("IP-address:", wlan.ifconfig()[0])
    return


def update_internal_clock():
    """
    Sync the internal clock on the PyCom with an NTP Server's time
    :return: 1
    """

    print("Updating internal clock", end='')
    rtc = machine.RTC()
    rtc.ntp_sync(_NTP_SERVER)
    while not rtc.synced():
        print(".", end='')
        time.sleep(1)
    print()
    return 1


def main():
    """
    Main method for running the experiment(s)
    :return: 1 if successful, otherwise -1
    """
    wlan = WLAN(mode=WLAN.STA)
    # Connecting to the Wi-Fi network
    if not wlan.isconnected():
        connect_to_network(wlan)
    if wlan.isconnected() < 1:
        print("Could not connect to Wi-Fi")
        return -1

    # Update the internal clock of the Pycom device
    # Make sure both client and server side have synchronized time
    update_internal_clock()

    # Experiment parameters
    N = 1024  # number of hopping ports (e.g. 2048)
    period_length_s_array = [120]  # Array of MTD period length in seconds (e.g. 10). (Allows multiple experiments that differ on period lenght)
    periods = 10000 # Number of periods (e.g. 5)

    print("N=", N, ", T(seg)=",  period_length_s_array, " , Repeat=", periods)
    print("BEGIN: ",  time.localtime())

    CoapExperiment(wlan, N, periods, [i * 1000 for i in period_length_s_array], True)  # Seconds to Mili, "experiment" uses miliseconds for the  period length
    print("END:", time.localtime())

    return 1


if __name__ == "__main__":
    main()