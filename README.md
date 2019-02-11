# RSA NetWitness Lua Whitelist Office365
whitelist office365 traffic parser and script
uploaded 2 sets of files

Pulls from this API
https://docs.microsoft.com/en-us/office365/enterprise/office-365-ip-web-service

## Script
python script to connect to the office365 API endpoint to collect the data to generate the content for the whitelists

## Content
output of the script are 3 things
### Lua Parser
this contains the hostnames that are returned from the API and added to the lua parser automactically
### IP feeds
2 IP feeds that contain the IPv4 and v6 addresses for the O365 endpoints

the data is intended to be written to the filter key in Netwitness that can be used to provide a filter point for data to include or exclude different data from investigations.

the parser includes 3 potential values for the hostnames added:
-whitelist
-office365
-<service or endpoint> which could include common, onenote, skype etc.
