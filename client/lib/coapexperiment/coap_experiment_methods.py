import asyncio
import binascii
import logging
import sys
import random
import time
from aiocoap import *
from lib.chacha import chacha2
import ntplib
import os
import statistics

_NTP_SERVER = "128.199.44.119"  # NTP Server IP
_SERVER_PORT = 5683  # CoAP Server Default UDP Port
_BASE_PORT = 10001  # Base ports to avoid collisions on lower well-known ports

def update_internal_clock():
    """
    Sync the internal clock on the Computer with an NTP Server's time
    :return: time object of the clock
    """
    internal_clock = None

    try:
        client = ntplib.NTPClient()
        response = client.request(_NTP_SERVER)
        internal_clock = time.ctime(response.tx_time)
        print("Updated internal clock", internal_clock)
    except:
        print('Could not sync with time server.')

    return internal_clock

def get_time(time_object):
    """
    Method that convert a time object to a string
    :param time_object: time object 
    :return: String of the time
    """
    return str(time_object[0]) + "-" + str(time_object[1]) + "-" + str(time_object[2]) \
     + " " +  str(time_object[3]) + ":" + str(time_object[4]) + ":" + str(time_object[5]) 


def get_floored_iv_time(period_length_seconds):
    """
    Method for getting the floored IV time,
    it is rounding backwards
    :param period_length_seconds: The period length in seconds
    :return: Epoch that is floored to the nearest period length
    """
    epoch_now = int(time.time())
    epoch_floored = epoch_now - (epoch_now % period_length_seconds)
    print("Floored IV", get_time(time.gmtime(epoch_floored)))
    return epoch_floored


def create_iv_epoch_rounded(period_length_seconds, univ):
    """
    Creates an 8-byte array of the time for the IV
    :param input period_length_seconds: MTD period length in  seconds
    :return: 8-bytte array of the time
    """

    epoch = time.time()
    # if is_next_trial == 1:
    #     epoch += period_length_seconds

    # Floor-Rounding the current epoch time to the nearest epoch
    # that is a multiple of our period length.
    # (e.g. if period is 1 hour, and we launched this at
    #     01:33:11 UTC on 1 January 1970,
    # Epoch will be Floor-Rounded to exact multiples of one hour, in this case
    #     01:00:00 UTC on 1 January 1970)

    epoch_rounded = int(epoch - (epoch % period_length_seconds)) + univ
    return epoch_rounded.to_bytes(8, "little")


def create_udp_port(byte_array):
    """
    Creates the UDP port out of the byte array
    :param byte_array: The byte array we want to get the port number
    :return: Integer of the port number
    """
    first_two_bytes = [int(no) for no in byte_array]
    first_two_bytes = first_two_bytes[:2]
    return int.from_bytes(bytes(first_two_bytes), "little")

def find_server_port(period_length_seconds, univ):
    N = 1024

    # ChaCha20 Setup
    # We read the PSK from a file.
    # WARNING: This was for testing purposes only, this is a very weak Key material.
    key_file = open("key.txt", 'r')
    key = bytearray(key_file.read().encode())

    print("KEY:", binascii.hexlify(key))

    # The IV is a multiple of our period length,
    # and we use the ChaCha2 library (runs 20 rounds,
    # since default in os)
    iv = create_iv_epoch_rounded(period_length_seconds, univ)
    crypt = chacha2.ChaCha(key, iv, rounds=20)

    # Using the static server port as data input, and
    # then we use zero padding
    message_encrypt = bytearray(int(_SERVER_PORT).to_bytes(2, "little"))
    message_encrypt += bytes(64 - len(message_encrypt))

    data = crypt.next(message_encrypt)
    port = _BASE_PORT + (create_udp_port(data) % N)

    print("CoAP server is running on port:", port)

    return port


async def get_coap_request(coap_context, payload, uri, sequence):
    """
    :param coap_context: The context we are using to send this call
    :param payload: The payload to be sent
    :param uri: The CoAP URI we are targeting
    :return: True if we recieve the expected payload
    """
    # print('sequence = ', sequence)
    request = Message(
        mtype=1,    # NON-CONFIRMABLE = 1
        code=Code.GET,
        payload=payload.encode('UTF-8'),
        uri=uri
    )

    try:
        response = await coap_context.request(request).response
    except Exception as e:
        # print('Failed to fetch resource:\n ', e)
        return False
    else:
        print('Result: %s\n%r\n' % (response.code, response.payload))
        return True

async def get_coap_well_known_core_experiment(coap_context, ip_address, port, sequence):
    return await get_coap_request(coap_context, "lol", "coap://" + ip_address + ":" + str(port) + "/.well-known/core", sequence)