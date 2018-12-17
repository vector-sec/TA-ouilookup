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

## Database updates
The ouilookup command will automatically download the oui manuf database from WireShark every 24 hours, so you shouldn't have too many issues with stale results. If you wanted it to be more often or less often, you can modify the number of seconds here https://github.com/vector-sec/TA-ouilookup/blob/master/bin/ouilookup.py#L45
