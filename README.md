# TA-ouilookup
WireShark OUI Lookup -- Simple Splunk TA for obtaining the manufacturer for a provided MAC address

## Installation
Create a TA-ouilookup directory in your Splunk apps directory or just install via file using the latest tar.gz in releases 

## Usage
```
... your search ...
... assume mac addresses are available in the field macAddr ...
| ouilookup field=macAddr
... you will now have two new fields manuf and manuf_long ...
```
