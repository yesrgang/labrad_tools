# LabRAD M-squared server

LabRad server to configure a M-squared laser using the [ICE](http://www.m2lasers.com/why-us/ice.aspxmo)
module (ethernet control).

## Requirements

### pylabrad

Make sure you install `pylabrad` before you run the server, e.g. using `pip`:

```shell
$ pip install labrad
```

You should als set the required environment variables, e.g. in `bash`:

```shell
$ export LABRADHOST=<hostname or ip>
$ export LABRADPASSWORD=<password>
```

### Configuration

Create a configuration file with the ip/hostname and port of the
M-squared ICE module.

```shell
$ cp config.example.json config.json
$ vim config.json
...
```

*Make also sure to enable remote control in the web
interface of the ICE module. Consult the M-squared manual for more information.*

## Example usage

First, start the server:

```shell
$ python msquared_server.py
```

Then start an (i)python console...

```shell
$ ipython
```

... and use the settings:

```python
import labrad

cxn = labrad.connection()
msquared = cxn.msquared

msquared.get_system_status() # => '{ "wavelength": 813.0, ... }'
```
