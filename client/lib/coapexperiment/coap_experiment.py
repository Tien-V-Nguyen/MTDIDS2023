import asyncio
import logging
import sys
import time
from aiocoap import *
from lib.coapexperiment import coap_experiment_methods
import os
import statistics
import random

async def perform_experiment(ip_address, get_request_interval, entries, period_length_seconds_arr):
    """
    Performs CoAP requests to the server side of PyCom
    :return: True
    """

    # Update the clock with the same NTP server as PyCom
    internal_clock = coap_experiment_methods.update_internal_clock()

    # Setup the CoAP client context
    coap_context = await Context.create_client_context()
    request_times = []
    entry = 0
    expected_sequence = 0
    packet_loss = 0
    next_port_trial = False
    next_changing_seconds = 0
    period_length_seconds = period_length_seconds_arr[0]
    univ = 0
    rate = 1
    temp_entry = 0
    while True:
        packet_ok = False
        univ = 0
        time.sleep(0.5)
        while True:
            for u in range(5):
                packet_ok = False
                port = coap_experiment_methods.find_server_port(period_length_seconds, u)
                try:
                    print("\n\nReconnaissance 1... ", port)
                    packet_ok = await asyncio.wait_for(coap_experiment_methods.get_coap_well_known_core_experiment(coap_context, ip_address, port, 0), timeout=2)
                except asyncio.TimeoutError as e:
                    packet_ok = False
                    print(e)
                print("Reconnaissance 1... ",packet_ok)
                if packet_ok:
                    univ = u
                    break

            next_changing_seconds = coap_experiment_methods.get_floored_iv_time(period_length_seconds) + period_length_seconds
            if packet_ok:
                break

        # Do the GET request for the ./well-known/core
        pre_check = False

        # temp_entry = 0
        for interval in get_request_interval:
            packet_ok = False
            while entry < entries:
                if univ > 0:
                    if int(time.time()) > next_changing_seconds:
                        univ = 0
                port = coap_experiment_methods.find_server_port(period_length_seconds, univ)
                # port = 5683

                print('sequence = ', expected_sequence)
                expected_sequence += 1
                packet_ok = False
                start_time = time.monotonic_ns()
                try:
                    entry += 1
                    temp_entry += 1
                    packet_ok = await asyncio.wait_for(coap_experiment_methods.get_coap_well_known_core_experiment(coap_context, ip_address, port, expected_sequence), timeout=0.5)
                except asyncio.TimeoutError as e:
                    packet_ok = False
                    print(e)
                end_time = time.monotonic_ns()
                
                print(packet_ok, (end_time - start_time)/1000000, "\n\n\n")

                if packet_ok and pre_check:
                    request_times.append(end_time - start_time)
                if not packet_ok:
                    packet_loss += 1
                    if not pre_check and len(request_times) > 0:
                        request_times.pop()
                        pre_check = packet_ok
                    break
                pre_check = packet_ok
                
                # print("temp entry = ", temp_entry)
                # if temp_entry * interval * rate == 30:
                #     # rate = rate/2
                #     # temp_entry = 0
                #     # if rate < 1/4:
                #     #     rate = 1
                #     rate = random.choice([1, 1/2, 1/4, 1/8, 1/16])
                #     temp_entry = 0
                #     print("rate = ", interval*rate)
                await asyncio.sleep(interval*rate)
            if not packet_ok and entry < entries:
                break
            print(request_times)
            # Average RTT and Standard Deviation
            print("GET interval: ", interval, ", Avg. RTT: ", "{:.2f}ms".format(statistics.mean(request_times) / 1000000), \
                ", Standard Deviation: ", "{:.2f}ms".format(statistics.stdev(request_times) / 1000000), \
                ", Packet Loss: ", "{:0f}%".format((packet_loss / expected_sequence) * 100))
            return True