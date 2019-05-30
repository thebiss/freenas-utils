#!/usr/bin/python3



#
# Expect bad python.
#
import json
import requests
import urllib3
import argparse
import sys


# Check arguments, abort if missing.
parser=argparse.ArgumentParser(description='Get the status of a VM, and optionally restart it if stopped. Implemented because middleward VM control is not integrated with bhyvectl or iohyve. Uses UNSTABLE FreeNAS REST API v2.0.\n')
parser.add_argument('--host', nargs=1,metavar='HOSTNAME',dest='hostname',help="Hostname of FreeNas host to check. Uses authentication credentials in .netrc",required=True)
parser.add_argument('--vm', nargs=1,metavar='VMNAME',dest='vmname',help="Name of BHYVE VM to check.",required=True)
parser.add_argument('--startup',dest='startup',help='Start the VM, if not running.',action='store_true')

args=parser.parse_args()

# Query the API
#       Ignore certificate health
#       Don't specify auth, use netrc
urllib3.disable_warnings()


try:
        r = requests.get(
        'https://'+args.hostname[0]+'/api/v2.0/vm',
        headers={'Content-Type': 'application/json'},
        verify=False
        )
except Exception as be:
        print("Failed querying VM list on",args.hostname[0],"\n",format(be),file=sys.stderr)
        exit(-1)


if(r.status_code!=200):
        print('Error querying VM list on',r.status_code,': ',r.text,file=sys.stderr)
        exit(-1)

# Parse reply
replyJson=json.loads(r.text)
# print(replyJson)

# Find the VM we want
vmID=0
vmIsFound=False
vmIsRunning=False

for vmInstance in replyJson:
    if (vmInstance['name']==args.vmname[0]):
        vmIsFound=True
        vmID=vmInstance['id']
        
        statusString = ''.join(["Host ",args.hostname[0]," VM ",vmInstance['name'],"status: ",vmInstance['status']['state']])

        if(vmInstance['status']['state']=="RUNNING"):
                vmIsRunning=True
                print(statusString)
        else:
                vmIsRunning=False
                print(statusString,file=sys.stderr)
        

# Exit if not found
if (vmIsFound==False):
    print("Error: VM not found.",file=sys.stderr)
    exit(-2)

# Restart the VM if not running
if ((args.startup==True) and (vmIsRunning==False)):
        try:
                r = requests.post(
                'https://'+args.hostname[0]+'/api/v2.0/vm/id/'+str(vmID)+'/start',
                headers={'Content-Type': 'application/json'},
                verify=False
                )
                print("Restart command sent. Response: ",r.status_code,file=sys.stderr)
        except Exception as be:
                
                print("Failed sending VM start to",args.hostname[0],"\n",format(be),file=sys.stderr)
                exit(-1)


        if(r.status_code!=200):
                print('Error sending VM start',r.status_code,': ',r.text,file=sys.stderr)
                exit(-1)


#end

 