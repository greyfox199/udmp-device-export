# udmp-device-export
this utility is used to to export devices from a udm pro device via the api

Requirements:  
-Assumes a local user has been created on the udm pro device to act as an api user with read access to the network piece.  
-Assumes host path can run python scripts (has only been tested on linux/ubuntu)     

# install
To install this script, either utilize the git-clone feature or manaually download from this repo.  It should be placed in a suitable location of your choosing for scheduled tasks.  This script requires a json config file to be passed in as a parameter.  The config file should be placed in an appropriate location; it does not have to reside in the same location as the script.  This file WILL have the client secret in it (until I can find a better way around this), so ensure that only the user running it can read it:

chmod 600 udmp-device-export-config.json

Once the python script and json config file have been created and configured, the script can be run manually as follows:  

python3 udmp-device-export.py -c "/path/to/udmp-device-export-config.json"

# config file
The config file is a json-formatted config file.  There are 4 required fields to control functionality:

```json
{
    "required": {
        "apiuser": "[insert api user name]",
        "apipass": "[insert password of api user]",
        "udmphost": "[insert hostname/IP of udmp device]",
        "pathToExportFilesDir": "/path/to/udmp-device-export"
    }
}
```
**apiuser**: This is the username of the api user that was created on the udm pro device.  
**apipass**: This is the password for the api user.   
**udmphost**:  This is the hostname and/or IP address of the udm pro device.   
**pathToExportFilesDir**: This is the path that will be used to write the exported json and csv files for the mfa report

# output
This will create two files, a json-formatted file and a csv file.  

the json-formatted file will have a name of udmp-device-export.json in the specified pathToExportFilesDir config entry.  It will have the following structure:

```json
[
    {
        "site": "[site name]",
        "name": "[device name]",
        "id": "[id of device]",
        "model": "[model]",
        "mac": "[mac address]",
        "version": "[firmware version]",
        "model_in_lts": [true | false],
        "model_in_eol": [true | false],
        "adopted": [true | false],
        "uplink_mac": "[mac address of uplink port]",
        "uplink_device_name": "[uplink device]",
        "uplink_remote_port": "[uplink port on remote device]",
        "port_idx": "[local uplink port]",
        "type": "[uplink media type]",
        "full_duplex": [true | false],
        "media": "[media speed]",
        "max_speed": "[max speed]"
    }
]
```

The csv file will have a name of udmp-device-export.csv in the specified pathToExportFilesDir config entry.  It willl have the following header structure:

site,name,id,model,mac,firmware,LTS,EOL,adopted,uplink_max,uplink_device_name,uplink_remote_port,port_idx,type,full_duplex,media,max_speed

The values will match what is in the json file listed above.