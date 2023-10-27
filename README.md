# IANVS phase II

## Server
Where the microPython code is.

### Create a build
If your Pycom is low on memory, create a special build directory by using the create_build.py file.
Here we will remove the python comments.

```
cd server
python create_build.py
cd microPythonBuild
```

### IANVS LoPy Build
[Instructions](IANVSLoPyBuild.md) of how to setup the environment for building for the PyCom device.


## Client
Client code used to simulate an attack on the Pycom device.

### Setup the virtual environment
```terminal
cd client
virtualenv env
source env/bin/activate
```

### Store Requirements
```terminal
pip freeze > requirements.txt
```

### Install Requirements
```terminal
pip install -r requirements.txt
```

### Add Requirements
```terminal
pip install xyz
```

### Generic client attack example
```terminal
$ python client_attacker.py 192.168.1.7
Updated internal clock Wed Aug 26 09:53:14 2020
KEY: b'74657374746573747465737474657374'
CoAP server is running on port: 10143
Result: 2.05 Content
b'</getmytime>;This is my time!=getmytime'
```

### Expirments
Use the following python files client_test_1.py, client_test_2.py for experiment 1, 2 etc.