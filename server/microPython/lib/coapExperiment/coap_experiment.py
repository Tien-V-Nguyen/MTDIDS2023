import binascii
import chacha.chacha2 as chacha2
import coapExperiment.coap_experiment_methods as static
import gc
import machine
from machine import I2C
import BME280
from network import Coap
import os
import pycom
import reading.reading as reading
import utime as time
import uselect
import usocket as socket
import _thread


_SERVER_PORT = 5683  # CoAP Server Default UDP Port
_BASE_PORT = 10001   # Avoid collisions on the lower
# well-known ports that may be in use

############ define pins ############
#i2c ("Inter-Integrated Circuit") is the multi master bus used to connect the sensors to the lopy4
i2c = I2C(0)
i2c = I2C(0, I2C.MASTER)
i2c = I2C(0, pins=('P9', 'P10'))
i2c.init(I2C.MASTER, baudrate=10000)

bme = BME280.BME280(i2c=i2c) # BME280 is the pressure, humidity and outdoor temp sensor. Uses addr=119

class CoapExperiment:

    def __init__(self, wlan, N, periods, period_length_ms_arr, is_using_mtd, key_file="key.txt"):
        """
        Initialize the class used for a experiment

        :param N: Number of ports to apply pour hopping
        :param periods: Number of periods
        :param period_length_ms: Period length in milliseconds
        :param key_file: Custom key if wanted. 
        """

        self.wlan = wlan
        self.N = N
        self.periods = periods
        self.period_length_ms_arr = period_length_ms_arr
        #self.well_known_core_uri = ".secret-core/hey"
        self.well_known_core_uri = ".well-known/core"
        self.sequence = 0

        self.stats = []
        self.stats.append(reading.Reading(0))

        self.waiting = {}
        self.max_waiting_size = 0
        self.window = [0, 0]
        self.alert = 0
        self.attk_pow = 0
        self.threshold = 4
        self.temp_threshold = 0
        self.window_size = 1
        self.univ = 0
        self.multiverse = False
        self.max_rate = 0
        self.moving_point = 0
        self.exposure_time = 3 #seconds

        # ChaCha20 Setup
        # We read the PSK from a file.
        # WARNING: This was for testing purposes only, this is a very weak Key material.
        key_file = open(key_file, 'r')
        self.key = bytearray(key_file.read())

        print("KEY:", binascii.hexlify(self.key))
        print("MTD Port-Range:", _BASE_PORT, "-", _BASE_PORT + (N - 1))

        # Initialize the CoAP server
        self.initialize_coap_server(is_using_mtd)

        open("mem_data.txt", "w").close()
        open("waiting_size.txt", "w").close()
        # Iterate the MTD periods!
        if is_using_mtd:
            self.iterate_mtd_periods(True)
        else:
            self.run_one_period(5683, 0, 0, False)

    def create_resource(self):
        # Add a resource with a default value and a plain text content format
        coap_server_resource = Coap.add_resource("getTemperature", media_type=Coap.MEDIATYPE_APP_JSON, value=str(time.time()))

        # Add the sequence number
        coap_server_resource.add_attribute("Seq#", str(self.sequence))

        # Add an attribute to the resource
        coap_server_resource.add_attribute("temperature", str(bme.temperature))

        # Configure the available operations for the resource
        coap_server_resource.callback(Coap.REQUEST_GET | Coap.REQUEST_POST | Coap.REQUEST_PUT | Coap.REQUEST_DELETE, True)

    def remove_resource(self):
        Coap.remove_resource("getTemperature")

    def initialize_coap_server(self, is_using_mtd):
        """
        Initilizing the CoAP server for our experiments

        :param ip_address: The IP-address of our Pycom device
        :param port: The port we want to use
        :param period_length_ms: The length of the period in milliseconds
        :param period_nr: Integer of current period in the experiment
        """

        # Initialize the CoAP module
        # Weird, but setting port is not working, like port=5683
        # changed to localhost
        #Coap.init(static.get_ip_address(self.wlan), service_discovery=False)
        try:
            if is_using_mtd:
                Coap.init("127.0.0.1", service_discovery=False)
            else:
                Coap.init("192.168.2.40", service_discovery=False)
        except Exception as e:
            print(e)
            pass

        # Try to use our .well-known core function (16 chars)
        # Coap.our_function(self.well_known_core_uri)

        # Create the resource
        self.create_resource()

    # Handling the sockets
    # Forwarding the packets sent to the correct port we are exposing
    def socket_handling(self, coap_server_poll, period_nr):
        # Wait for any socket to become available in 100 milliseconds
        sockets = coap_server_poll.poll(100)

        for s in sockets:
            sock = s[0]
            event = s[1]
            if(event & uselect.POLLIN):
                # Forward to the CoAP socket
                (tempBuffer, tempRemoteAddress) = sock.recvfrom(1024)
                # print("Sender", "Buffer", str(tempBuffer), "temp address", str(tempRemoteAddress))

                if self.multiverse:
                    t = int(time.time())
                    if self.alert == self.exposure_time:
                        if t - self.moving_point == self.window_size + 2:
                            self.window[1] += 1
                        elif t - self.moving_point == self.window_size + 3:
                            print("w1 = ", self.window[1]," temp_threshold = ", self.temp_threshold)
                            if self.window[1] < self.temp_threshold - 2: #minus 2 is the error in measurement
                                print("Attackedddddddd1!!!\n")
                            else:
                                print("No Attacks!\n")
                                self.threshold = self.max_rate = self.window[1]
                            self.window[1] = 1
                            self.alert = 0
                        elif t - self.moving_point > self.window_size + 3:
                            print("Attackedddddddd2!!!\n")
                            self.alert = 0
                            self.window[1] = 1
                            
                    else:
                        # print("test0\n\n")
                        if t - self.window[0] < self.window_size:
                            self.window[1] += 1
                        elif t - self.window[0] == self.window_size:
                            print("total requests of previous window:", self.window[1], ", threshold = ", self.threshold,"\n")
                            if self.window[1] <= self.threshold and self.max_rate <= self.window[1]:
                                self.max_rate = self.window[1]
                            if self.window[1] > self.threshold:
                                # print("test1\n\n")
                                self.alert += 1
                                if self.alert == self.exposure_time:
                                    self.temp_threshold = self.window[1]
                            else:
                                # print("test2\n\n")
                                self.alert = 0
                            self.window[1] = 1
                            if self.alert == self.exposure_time:
                                # print("test3\n\n")
                                self.window[0] = t
                                self.moving_point = t
                                
                                self.window[1] = 0
                                return 1
                        else:
                            self.window[1] = 1
                            self.alert = 0
                    self.window[0] = t

                if tempBuffer == b'':
                    # In this case the attacker is also successfull
                    # print("CoAp Attack")
                    self.stats[period_nr].attack += 1
                else:
                    if tempRemoteAddress[0] != '127.0.0.1':
                        self.waiting[str(tempBuffer[2:6])] = tempRemoteAddress
                        # if len(self.waiting) > self.max_waiting_size:
                        #     self.max_waiting_size = len(self.waiting)
                        #     f = open("waiting_size.txt", "a")
                        #     f.write(str(self.max_waiting_size) + "\n")
                        #     f.close()

                        #sock.sendto(b'@\x01\xfc\\\xbb.well-known\x04core', ("192.168.1.8", 5683))
                        #sock.sendto(tempBuffer, (static.get_ip_address(self.wlan), 5683))
                        sock.sendto(tempBuffer, ("127.0.0.1", 5683)) # changed to localhost

                        # Update the internal resource
                        self.remove_resource()
                        self.create_resource()

                        # Call Coap.read() which parses the incoming CoAp message
                        Coap.read()

                        # Update the internal sequence
                        self.sequence = self.sequence + 1
                    else:
                        # print("Receiver", "Buffer from", str(tempBuffer2), "temp address", str(tempRemoteAddress2))
                        sock.sendto(tempBuffer, self.waiting[str(tempBuffer[2:6])])
                        self.waiting.pop(str(tempBuffer[2:6]))
        return 0

                

    def iterate_mtd_periods(self, isMTD):
        # Iterate through the MTD periods, one at a time
        # attacked = 0
        i = 0
        while True:
            print("Change Moving period!")
            # if attacked == 2:
            #     i = (i+1) % len(self.period_length_ms_arr)
            period_length_ms = self.period_length_ms_arr[0]

            for period in range(0, self.periods):

                if isMTD:
                    # The IV is a multiple of our period length
                    iv = static.create_iv_epoch_rounded(int(period_length_ms / 1000), self.univ)
                    # print("IV:", binascii.hexlify(iv))

                    # WARNING: This IV may be out of synch for a fraction
                    # of the period if you synchronize with an MTD CoAP client.
                    # The FIRST syncrhonized MTD period should be shorter.
                    # We do not fix the first period length, in the interest of
                    # simplicity for our paper experiments. This way, we operate with
                    # full period lengths, independently of when the experiment started.
                    # (Otherwise we should discard the first period of every experiment)

                    # By default the ChaCha2 library has lesser rounds, which will make
                    # it incompatible with Desktop versions of ChaCha20. Thus, we force
                    # it to use 20 rounds.
                    crypt = chacha2.ChaCha(self.key, iv, rounds=20)

                    # Using the static server port as data input
                    # Zero padding the rest
                    message_encrypt = bytearray(_SERVER_PORT.to_bytes(2, "little"))
                    message_encrypt += bytes(64 - len(message_encrypt))

                    data = crypt.next(message_encrypt)
                    port = _BASE_PORT + (static.create_udp_port(data) % self.N)
                else:
                    port = 10002

                print("[" + str(period) + "] port:", port)
                print("\nTry: " + "coap-client -m get coap://" + static.get_ip_address(self.wlan) + ":" + str(port) + "/" + self.well_known_core_uri + "\n")

                res = self.run_one_period(port, period, period_length_ms, True)
                if res != 0:
                    self.univ += 1
                else:
                    self.univ = 0

                print("[" + str(period) + "] attack:", self.stats[period].attack)
                print("****************\n\n")
                if self.univ != 0:
                    break

        # Experiment Finished.

    def store_results(self):
        # Creating/Opening the file to append the results
        # We create a file named "YYYY-mm-dd-results.txt" for the day
        time_tuple = time.localtime()
        results_filename = str(time_tuple[0]) + "-" + str(time_tuple[1]) + "-" + str(time_tuple[2]) + "-results.txt"

        with open(results_filename, 'a') as datafile:
            # Sums up the successful attacks for the periods (we log max one attack per period)
            sum_success = 0
            for period in range(0, self.periods):
                # Make sure we are only counting one, even though we
                # have multiple attacks during a single MTD period
                if self.stats[period].attack > 0:
                    sum_success += 1

            # The line contains the relevant parameters of the experiment
            datafile.write(str(self.N) + "," + str(self.periods) + "," + str(self.period_length_ms) + "," + str(sum_success) + "\n")

        datafile.close()
    
    def sock_thread(self, p, coap_socket):
        # Wait for any socket to become available
        sockets = p.poll()
        for s in sockets:
            sock = s[0]
            event = s[1]
            if(event & uselect.POLLIN):
                # Check if the socket belongs to the CoAp module
                if(sock == coap_socket):
                    # Update the internal resource
                    self.remove_resource()
                    self.create_resource()
                    # Call Coap.read() which parses the incoming CoAp message
                    Coap.read()

    def run_one_period(self, port, period_nr, period_length_ms, is_using_mtd):
        """
        Method for running a period.
        Setup the CoAP server for a period

        :param server: CoAP server
        :param port: The port we want to use
        :param period_length_ms: The length of the period in milliseconds
        :param period_nr: Integer of current period in the experiment
        """

        # Collect from garbage
        gc.collect()
        f = open("mem_data.txt", "a")
        mem_free = gc.mem_free()
        f.write(str(mem_free) + "\n")
        f.close()
        print("Available memory:", mem_free, "bytes")
        print("Wi-Fi connected", self.wlan.isconnected())

        # Increase the stats array
        self.stats.append(reading.Reading(0))

        if is_using_mtd:
            # The socket that is redirecting to our local CoAP server
            special_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            special_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            special_sock.bind(('', port))
        else:
            special_sock = Coap.socket()

        # Create a new poll object
        coap_server_poll = uselect.poll()

        # Set up the polling for the resource, which is our special socket
        coap_server_poll.register(special_sock, uselect.POLLIN | uselect.POLLHUP | uselect.POLLERR)
        attacked = 0
        if not is_using_mtd:
            while True:
                self.sock_thread(coap_server_poll, special_sock)
        else: 
            # Finding the expected end time of the server polling, and we
            # are adjusting it based on the current time we are into the
            # IV period. By having this offset we are making sure the period
            # finishes when the time based IV is changed.

            period_length_seconds = int(period_length_ms / 1000)

            previous_iv_change_seconds = static.get_floored_iv_time(period_length_seconds)
            next_iv_change_seconds = previous_iv_change_seconds + period_length_seconds

            next_iv_change_seconds_time = time.gmtime(next_iv_change_seconds)
            print("Expected end time", static.get_time(next_iv_change_seconds_time))
            while (int(time.time()) < next_iv_change_seconds and attacked == 0):
                # Find the remaining time of the period
                #remaining_time_ms = int(( next_iv_change_seconds - int(time.time()) ) * 1000)
                #print("Remaing timeout:", remaining_time_ms, "ms")

                # Polling for the incom requests
                attacked = self.socket_handling(coap_server_poll, period_nr)

            # Close the CoAP socket
            if self.max_rate > 0:
                self.threshold = self.max_rate
            else:
                self.threshold = 1
            self.max_rate = 0
            print("One CoAP period done!", attacked)
        special_sock.close()
        return attacked
        # return 0
