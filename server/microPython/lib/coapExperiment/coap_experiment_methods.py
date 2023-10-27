# Static methods used by the CoAP experiment
import gc
import binascii
import os
import pycom
import ustruct as struct
import utime as time


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
    # if attacked == 1:
    #     epoch += period_length_seconds

    # Floor-Rounding the current epoch time to the nearest epoch
    # that is a multiple of our period length.
    # (e.g. if period is 1 hour, and we launched this at
    #     01:33:11 UTC on 1 January 1970,
    # Epoch will be Floor-Rounded to exact multiples of one hour, in this case
    #     01:00:00 UTC on 1 January 1970)

    epoch_rounded = epoch - (epoch % period_length_seconds) + univ
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


def get_ip_address(wlan):
    """
    Gets the IP address of the wlan object
    :param wlan: Wlan object
    """
    return wlan.ifconfig()[0]
    