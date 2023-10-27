import asyncio
import logging
import sys
from aiocoap import *
from lib.coapexperiment import coap_experiment_methods
from lib.coapexperiment import coap_experiment
import os

logging.basicConfig(level=logging.INFO)

TEST_1_GET_REQUEST_INTERVAL = [3] # seconds
TEST_2_ENTRIES = 400 # Tries 125 times 
period_length_seconds_arr = [120] # seconds, MTD period

async def main():
    test_case = sys.argv[1]
    ip_address = sys.argv[2]

    if test_case == "1":
        print("TEST 1 - Baseline attack, no attack")
        await coap_experiment.perform_experiment(ip_address, TEST_1_GET_REQUEST_INTERVAL, TEST_2_ENTRIES, period_length_seconds_arr)
    elif test_case == "2":
        print("TEST 2 - Attacker, no MTD system")
        await coap_experiment.perform_experiment(ip_address, TEST_1_GET_REQUEST_INTERVAL, TEST_2_ENTRIES, period_length_seconds_arr)
    elif test_case == "3a":
        print("TEST 3a - Attacker - MTD system only port Hopping")
        await coap_experiment.perform_experiment(ip_address, TEST_1_GET_REQUEST_INTERVAL, TEST_2_ENTRIES, period_length_seconds_arr)
    elif test_case == "3b":
        print("TEST 3ba - Attacker - MTD system with CoAP .well-known/core hopping")
        await coap_experiment.perform_experiment(ip_address, TEST_1_GET_REQUEST_INTERVAL, TEST_2_ENTRIES, period_length_seconds_arr)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python client_tests.py test-case ip-address-of-pycom\n python client_tests.py 1 198.168.2.40")
    else:
        # The aiocoap library seems to require asyncio
        asyncio.get_event_loop().run_until_complete(main())