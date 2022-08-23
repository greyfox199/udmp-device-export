import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import sys, getopt
from os.path import exists
import socket
from datetime import datetime
import logging
import csv

argumentList = sys.argv[1:]

# Options
options = "hc:"
ConfigFilePath = ""
long_options = ["Help", "ConfigFilePath"]

#get command line arguments
try:
    # Parsing argument
    arguments, values = getopt.getopt(argumentList, options, long_options)

    if arguments:
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-h", "--Help"):
                print ("Usage: python3 udmp-device-export.py -c /path/to/config.json")

            elif currentArgument in ("-c", "--ConfigFilePath"):
                ConfigFilePath = currentValue
    else:
        print("Usage: python3 udmp-device-export.py -c /path/to/config.json")
        exit()

except getopt.error as err:
    # output error, and return with an error code
    print(str(err))

#we require a json config file, so if it doesn't exist, abort
if not exists(ConfigFilePath):
    print("json config file specified at " + ConfigFilePath + " does not exist, aborting process")
    exit()

#open config file and check that it's a valid json file, if its not, abort
objConfigFile = open (ConfigFilePath, "r")
try:
    jsonData = json.loads(objConfigFile.read())
except Exception as e:
    print("Config file of " + ConfigFilePath + " is not a valid json file, aborting process")
    exit()

#create config dictionary object to hold configuration items
config = {}

#function to do general validation on json configuration items
def validateJSONConfig(section, key):
    if key in jsonData[section]:
        try:
            config.update({key:str(jsonData[section][key])})
        except:
            print("required field of " + key + " in config not valid, aborting proces")
            exit()
    else:
        print("required field of " + key + " in config does not exist, aborting proces")
        exit()

#validate all required keys in config file
validateJSONConfig("required", "apiuser")
validateJSONConfig("required", "apipass")
validateJSONConfig("required", "udmphost")
validateJSONConfig("required", "pathToExportFilesDir")

#since pathToExportFilesDir is a local path, validate that it exists before proceeding
if not exists(config["pathToExportFilesDir"]):
    print("local path of " + config["pathToExportFilesDir"] + "does not exist, aborting process")
    exit()

#ignore ssl check, build auth header and get authenticated session
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
headers = {"Accept": "application/json","Content-Type": "application/json"}
data = {'username': config["apiuser"], 'password': config["apipass"]}
s = requests.Session()
r = s.post('https://' + config["udmphost"] + ':443/api/auth/login', headers = headers,  json = data , verify = False, timeout = 1)

#save local variables for use later in reporting
deviceData = []
device = {}

#first get sites (should only be one on a udmp, but building this out to use on a self-hosted controller)
response = s.get('https://' + config["udmphost"] + '/proxy/network/api/self/sites', headers = headers, verify = False, timeout = 1).json()

#loop through each site and get devices per site
for site in response['data']:
    devices = s.get('https://' + config["udmphost"] + '/proxy/network/api/s/default/stat/device', headers = headers, verify = False, timeout = 1).json()
    #loop through each device and save key items 
    #future expansion would be to build list from config file or command line argument
    for device in devices['data']:
    
        record = {}
        record["site"] = site["name"]
        record["name"] = ""
        record["id"] = ""
        record["model"] = ""
        record["mac"] = ""
        record["version"] = ""
        record["model_in_lts"] = ""
        record["model_in_eol"] = ""
        record["adopted"] = ""
        record["uplink_mac"] = ""
        record["uplink_device_name"] = ""
        record["uplink_remote_port"] = ""
        record["port_idx"] = ""
        record["type"] = ""
        record["full_duplex"] = ""
        record["media"] = ""
        record["max_speed"] = ""
        record["upgradable"] = ""
        record["upgrade_to_firmware"] = ""

        if "name" in device:
            record["name"] = device["name"]
        if "_id" in device:
            record["id"] = device["_id"]
        if "model" in device:
            record["model"] = device["model"]
        if "mac" in device:
            record["mac"] = device["mac"]
        if "version" in device:
            record["version"] = device["version"]
        if "model_in_lts" in device:
            record["model_in_lts"] = device["model_in_lts"]
        if "model_in_eol" in device:
            record["model_in_eol"] = device["model_in_eol"]
        if "adopted" in device:
            record["adopted"] = device["adopted"]
        if "upgradable" in device:
            record["upgradable"] = device["upgradable"]
        if "upgrade_to_firmware" in device:
            record["upgrade_to_firmware"] = device["upgrade_to_firmware"]
        #need to refactor this part later for accessing a level deeper into the json output
        if "uplink" in device:
            for key, value in device["uplink"].items():
                if key == "uplink_mac":
                    record["uplink_mac"] = value
                if key == "uplink_device_name":
                    record["uplink_device_name"] = value
                if key == "uplink_remote_port":
                    record["uplink_remote_port"] = value
                if key == "port_idx":
                    record["port_idx"] = value
                if key == "type":
                    record["type"] = value
                if key == "full_duplex":
                    record["full_duplex"] = value
                if key == "media":
                    record["media"] = value
                if key == "max_speed":
                    record["max_speed"] = value
        deviceData.append(record) 

#now that we have all our device data in an array, export it to both json and csv file
#export device data to json file using path from config file
with open(str(config["pathToExportFilesDir"]) + "/udmp-device-export.json", "w") as json_file:
    json.dump(deviceData, json_file, indent=4)

#export device data to csv file using path from config file
with open(str(config["pathToExportFilesDir"]) + "/udmp-device-export.csv", 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["site", "name", "id", "model", "mac", "firmware", "LTS", "EOL", "adopted", "upgradable", "upgrade_to_firmware", "uplink_mac", "uplink_device_name", "uplink_remote_port", "port_idx", "type", "full_duplex", "media", "max_speed"])
    for item in deviceData:
        writer.writerow([item["site"], item["name"], item["id"], item["model"], item["mac"], item["version"], item["model_in_lts"], item["model_in_eol"], item["adopted"], item["upgradable"], item["upgrade_to_firmware"], item["uplink_mac"], item["uplink_device_name"], item["uplink_remote_port"], item["port_idx"], item["type"], item["full_duplex"], item["media"], item["max_speed"]])

print("JSON file available at " + str(config["pathToExportFilesDir"]) + "/udmp-device-export.json")
print("CSV file available at " + str(config["pathToExportFilesDir"]) + "/udmp-device-export.csv")
