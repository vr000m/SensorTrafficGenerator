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
 python sensor.py <sensor_type> <ip> <port> <id>
 python sensor.py camera localhost 5000 1
```

It also creates a log file (CSV) with filename `dev_id.log`.
`dev_id` is a combination of `<sensor_type>_<id>`
```
 timestamp  seq_no   data_value
```
Camera is a special case in which the log file just stores
the length of the data field because the simulated
data from the camera can be very large. Instead the data
is stored in a `camera.data` file