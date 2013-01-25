SensorTrafficGenerator
======================

The code generates random traffic for an IoT simulator.

We currently simulate the following __sensor_types__:
- [x] temp (in deg centigrade) every 1s
- [x] device (ON, OFF) every few seconds
- [x] motion camera (100, 1000 kbps) depending on detection 
- [x] GPS (lat, lon) every few seconds depending on vehicular speed

Example:
```
 python sensor.py <sensor_type> <ip> <port>
 python sensor.py camera localhost 5000
```
