
# Linux Setup IANVS Part II
## Pre-requirements
- Python
- cmake
- gcc
- pyserial (python-serial)
- pip (python-pip)

And run this as well
```terminal
sudo apt-get install git wget make libncurses-dev flex bison gperf python python-serial
```

## I. Installation
```
cd ~
mkdir esp
git clone https://github.com/pycom/pycom-micropython-sigfox.git
cd pycom-micropython-sigfox
git submodule update --init
cd ..

wget https://dl.espressif.com/dl/xtensa-esp32-elf-linux64-1.22.0-80-g6c4433a-5.2.0.tar.gz
tar -xzf xtensa-esp32-elf-linux64-1.22.0-80-g6c4433a-5.2.0.tar.gz
export PATH="$PATH:$HOME/esp/xtensa-esp32-elf/bin"
cd ..

git clone --recursive -b idf_v3.3.1 https://github.com/pycom/pycom-esp-idf.git
cd pycom-esp-idf
git submodule update --init
export IDF_PATH=~/esp/pycom-esp-idf/
```

Now we have the necessary programs
```terminal
cd pycom-micropython-sigfox
cd mpy-cross && make clean && make && cd ..
```

Lets try to build
```terminal
cd esp32/
make clean
```

Try to make bootloader
```terminal
make TARGET=boot
```

Then, make the app
```terminal
make TARGET=app
```

If its working, we are good!

## II. Finish installing the pycom-esp-idf
```terminal
cd ~/esp/pycom-esp-idf/
./install.sh
. ./export.sh
```

## III. Modifing library

We need to edit the compiled liblwip.a file in the esp32/lib directory. 
However, after reading through the internet, the coping part is a bit
funky. What we are essentially doing is building an example, then coping the .a files
over. This example is specifically the examples/wifi/scan folder.

I think this was the best solution:

```terminal
cd ~/esp/pycom-esp-idf/examples/wifi/scan
make menuconfig
make clean
make all
make bootloader
```

## IV. Try to rebuild the ESP32 folder!
Build for LoPy

COPY_IDF_LIB Flag: Copy the LIB from the wifi/scan example folder

```terminal
cd ~/esp/pycom-micropython-sigfox/esp32
make clean
make BOARD=LOPY COPY_IDF_LIB=1
```

Make sure that your board is placed into programming mode, otherwise flashing will fail.
All boards except Expansion Board 2.0 will automatically switch into programming mode.
Remember “G23” and “GND”.

Flash at full speed!

```terminal
make flash BOARD=LOPY ESPSPEED=921600
```

#### Error, red flash on Pycom
Make sure you have good connection on your "G23" to "GND".

#### Error, permission denied USB
If using Vagrant
```terminal
sudo su
//type your password
cd /
cd dev
chown username ttyUSB0
```

#### Error, will not build
Try delete the LoPy build folder

## Okay, lets try to build with the ICMP disabled
Disable it in the doxyfile on line 2077,36
```terminal
cd ~/esp/pycom-esp-idf/components/lwip/lwip/doc/doxygen
vim lwip.Doxyfile
```


Disable it in the opt.h file on Line 774.42
```terminal
cd ~/esp/pycom-esp-idf/components/lwip/lwip/src/include/lwip
vim opt.h
```

```code
/**
 * LWIP_ICMP==1: Enable ICMP module inside the IP stack.
 * Be careful, disable that make your product non-compliant to RFC1122
 */
#if !defined LWIP_ICMP || defined __DOXYGEN__
#define LWIP_ICMP                       0
#endif
```

Follow step III again
and then step IV

## Modify the libCoAP library
Now it is time to modify the libcoap library. Follow the steps [here](ModifyCoap.md)!

## Rebuilding later
Remember to run this for your environment:
```terminal
export PATH="$PATH:$HOME/esp/xtensa-esp32-elf/bin"
export IDF_PATH=~/esp/pycom-esp-idf/
/usr/bin/python -m pip install --user -r /home/vagrant/esp/pycom-esp-idf/requirements.txt
```