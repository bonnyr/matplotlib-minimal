# SNMP Counter Plotter
This little script processes a number of input files and options to do either or both of:
1. Update a state file with new sample snapshots.
1. Plot metric graphs for selected counters from the current stat.

Each distinct counter (identified by name) is treated as a separate data set which gets plotted across all devices stored in the state file. 
The script knows about the ipv4 and ipv6 stats relationship (each ipv4 stat has a matching ipv6 counterpart) and will plot
two graphs for the stats on the same image.

The state data file has the following specification:

1. The file is a CSV file 
1. Each entry in the file is a data sample with the following fields
    - sample date. Thie is a date formatted as iso8601 string
    - device name. This is the host name of the device
    - counter name. This is the name of the counter
    - counter value

The script loads this state file and creates a set of counter datasets, each with multiple tuples containing device, date and value.

When provided with snapshot files, the files are assumed to be a new data set instance for all the counters, formatted as snmpwalk output. 
This means the output format of each line matches the following regex:
```
^[^:]+::(?P<counter>[^.]+).[0-9] = [^:]+: (?P<sample>[0-9]+)$
```

The second input file name must be formatted as follows:
`<device_name>-<timestamp>.txt`

The device name is the device host name.

The script parses the snmp output, stripping unneeded fields and creating entries in the respective data sets.

Once done, the data sets are iterated over and plotted, one plot per selected counter. The generated plots are saved in a file whose name is 
`<metric-name>-<plot date>.png`

## Invocation
The script is run as follows:

``` 
python3 chartplotter.py [options] <state file> <input dir> <output dir>

usage: chartplotter.py [-h] [-m METRICS] [-t TRIM] state input output

Maintain counter snapshot and plot them

positional arguments:
  state                 path to state file. Required
  input                 path to input directory containing SNMP counter data. Required
  output                path to output directory where generated graphs are stored. Required

optional arguments:
  -h, --help            show this help message and exit
  -m METRICS, --metric METRICS
                        name of counter to plot. Optional. If no counters are specified, all counters are plotted
  -t TRIM, --trim TRIM  trim data set to contain at most TRIM samples per counter and device                      
```

