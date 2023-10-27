import asyncio
import logging
import sys
import time
from aiocoap import *
from lib.coapexperiment import coap_experiment_methods
import os
import numpy as np

MTD_period = 120

async def scan_one_period(coap_context, ip_address, port_arr, period):
    i = 0
    while True:
        period_length_seconds = int(period)

        previous_iv_change_seconds = coap_experiment_methods.get_floored_iv_time(period_length_seconds)
        next_iv_change_seconds = previous_iv_change_seconds + period_length_seconds

        next_iv_change_seconds_time = time.gmtime(next_iv_change_seconds)
        print("Expected end time", coap_experiment_methods.get_time(next_iv_change_seconds_time))

        print("Scan a new period")
        np.random.shuffle(port_arr)

        i = 0
        packet_ok = False
        for port in port_arr:
        # while True:
            if int(time.time()) >= next_iv_change_seconds:
                break
            # port = 5685
            # port = coap_experiment_methods.find_server_port(period_length_seconds)
            print(i, "Scanning port ", port)
            i+=1
            try:
                packet_ok = await coap_experiment_methods.get_coap_well_known_core_experiment(coap_context, ip_address, port, 0)
            except Exception as e:
                print(e)
                pass
            if packet_ok:
                print("server port is: ", port)
                i = 0
                while True:
                    i+=1
                    print(i)
                    if int(time.time()) >= next_iv_change_seconds:
                        break
                    try:
                        packet_ok = await asyncio.wait_for(coap_experiment_methods.get_coap_well_known_core_experiment(coap_context, ip_address, port, 0), timeout=0.5)
                    except:
                        packet_ok = False
                        break
                    if packet_ok:
                        time.sleep(1/120) #1/14 ~ 8 req/s in Exploitation phase, 1/120 ~ 16, 1/50 ~ 12
                    else:
                        break
                break
            time.sleep(1/2) # 2 req/s in Reconnaissance phase
 
    print("Current time:", coap_experiment_methods.get_time(time.gmtime(int(time.time()))))
    time_remaining = next_iv_change_seconds - int(time.time())
    print("Remaining time of the period:", time_remaining, "seconds\n\n")
    time.sleep(time_remaining)
    return

async def main():
    """
    Performs CoAP requests to the server side of PyCom
    :return: True
    """
    # Setup the CoAP client context
    coap_context = await Context.create_client_context()

    # Do the GET request for the ./well-known/core
    ip_address = sys.argv[1]

    arr = np.arange(10001, 11024)
    while True:
        await scan_one_period(coap_context, ip_address, arr, MTD_period)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 client_attacker.py ip-address-of-pycom\n python3 client_attacker.py 192.168.2.40")
    else:
        # The aiocoap library seems to require asyncio
        asyncio.get_event_loop().run_until_complete(main())