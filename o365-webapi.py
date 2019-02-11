#!/usr/bin/env python

import json
import os
import urllib.request
import uuid
from datetime import datetime

#variables for output control
#master whitelist name
feed_col_whitelist = "whitelist"
#product whitelist value
feed_col_whitelist_name = "office365"

#generate parser date version
now = datetime.now()
parser_gen_date = now.strftime("%Y.%m.%d")
parser_date_string='local parserVersion = "' + parser_gen_date + '"\n'

#name of parser
parser_name='lua_wl_o365'
parser_name_string='local parserName = "' + parser_name + '"\n'

lua_script_pre='''
local O365 = nw.createParser(parserName, parserName .. ": " .. parserVersion)
-- this shows in the mouseover

nw.logDebug(parserName .. " " .. parserVersion)

local summary = {["parserName"] = parserName, ["parserVersion"] = parserVersion}

summary.parserDetails = [=[
marks Office365 traffic as whitelisted as well as the product name detected
looks for hostname and domains in the following keys 
    alias.host
    host.src
    host.dst
    fqdn

then marks them in the following keys
filter
with whitelist meta
    whitelist               - for global whitelisting
    o365                    - for office365 specifics
    'application name'      - for the application in office365 that leverages the hostname

the parser attempts to match both exact AND subdomain matches so for an entry that has both
a specific domain and overlapping *. wildcard subdomain you will potentially get 6 values written (3 for each match)
this can be changed by ordering the list from specific to substring and putting a break in teh loop to prevent after first match (specific first)

]=]

--[[
    VERSION
        2018.08.11.1  eric.partington@rsa.com  11.1.0.0-8987.3  UDM
        2018.10.10.2  eric.partington@rsa.com  updated to work with different lua import list
        
    OPTIONS
        none

    IMPLEMENTATION
        Relies on meta registered by other parsers.

    TODO
        none?
--]]
--local debugParser = require('debugParser')

local lookup_list = ({
'''

lua_script_post='''
})

O365:setKeys({
	nwlanguagekey.create("filter", nwtypes.Text),
	nwlanguagekey.create("feed.name", nwtypes.Text),
})

function O365:onHost(idx, host)
    --lowercase the incoming value
    host = string.lower(host)
	
    for domain in pairs(lookup_list) do
   
        -- replace the * wildcard in the list with .*
        domain_esc = string.gsub(domain, "%*", "%.%*")
        --print("domain after gsub for * " .. domain)
        
        -- for hostnames that have a - in them we need to escape that with %% so the end string ends %- (first % escapes on replace)
        domain_esc = string.gsub(domain_esc, "%-", "%%-")
        
        if string.match(host, "^"..domain_esc.."$") then
            -- QUESTIONS::
            -- should the list match both specific and wildcard matches?
            -- should the list only match specific first and then do wildcard only if no match
            -- if above is correct, list should be ordered specific first then wildcard so that first match exits the loop
            
            --print(domain_esc)
            for index,list_value in ipairs(lookup_list[domain]) do
                -- this is the counter in the table
                --print(index)
                -- this is the value from the table
                --print(list_value)
                nw.createMeta(self.keys["filter"], list_value)
            end
            
            -- finally aftger writing all the values from the matched value update the  feed.name meta
            -- this throws an error oddly
            nw.createMeta(self.keys["feed.name"], parserName)
        
        end
    end
    --end
end

O365:setCallbacks({
    [nwlanguagekey.create("alias.host")] = O365.onHost,
    [nwlanguagekey.create("fqdn")] = O365.onHost,
    [nwlanguagekey.create("host.src")] = O365.onHost,
    [nwlanguagekey.create("host.dst")] = O365.onHost
})
'''

#sample data
#{'id': 1, 'serviceArea': 'Exchange', 'serviceAreaDisplayName': 'Exchange Online', 'urls': ['outlook.office.com', 'outlook.office365.com'], 'ips': ['13.107.6.152/31', '13.107.9.152/31', '13.107.18.10/31', '13.107.19.10/31', '13.107.128.0/22', '23.103.160.0/20', '23.103.224.0/19', '40.96.0.0/13', '40.104.0.0/15', '52.96.0.0/14', '111.221.112.0/21', '131.253.33.215/32', '132.245.0.0/16', '134.170.68.0/23', '150.171.32.0/22', '157.56.232.0/21', '157.56.240.0/20', '191.232.96.0/19', '191.234.6.152/32', '191.234.140.0/22', '204.79.197.215/32', '206.191.224.0/19', '2603:1006::/40', '2603:1016::/40', '2603:1026::/40', '2603:1026:200::/39', '2603:1026:400::/39', '2603:1026:600::/44', '2603:1026:620::/44', '2603:1026:800::/44', '2603:1026:820::/45', '2603:1036::/39', '2603:1036:200::/40', '2603:1036:400::/40', '2603:1036:600::/40', '2603:1036:800::/38', '2603:1036:c00::/40', '2603:1046::/37', '2603:1046:900::/40', '2603:1056::/40', '2603:1056:400::/40', '2603:1056:600::/40', '2603:1096::/38', '2603:1096:400::/40', '2603:1096:600::/40', '2603:1096:a00::/39', '2603:1096:c00::/40', '2603:10a6:200::/40', '2603:10a6:400::/40', '2603:10a6:600::/40', '2603:10a6:800::/40', '2603:10d6:200::/40', '2620:1ec:4::152/128', '2620:1ec:4::153/128', '2620:1ec:c::10/128', '2620:1ec:c::11/128', '2620:1ec:d::10/128', '2620:1ec:d::11/128', '2620:1ec:8f0::/46', '2620:1ec:900::/46', '2620:1ec:a92::152/128', '2620:1ec:a92::153/128', '2a01:111:f400::/48'], 'tcpPorts': '80,443', 'expressRoute': True, 'category': 'Optimize', 'required': True}, 
#{'id': 13, 'serviceArea': 'Skype', 'serviceAreaDisplayName': 'Skype for Business Online and Microsoft Teams', 'urls': ['*.broadcast.skype.com', 'broadcast.skype.com'], 'ips': ['13.70.151.216/32', '13.71.127.197/32', '13.72.245.115/32', '13.73.1.120/32', '13.75.126.169/32', '13.89.240.113/32', '13.107.3.0/24', '13.107.64.0/18', '51.140.143.149/32', '51.140.155.234/32', '51.140.203.190/32', '51.141.51.76/32', '52.112.0.0/14', '52.163.126.215/32', '52.170.21.67/32', '52.172.185.18/32', '52.178.94.2/32', '52.178.161.139/32', '52.228.25.96/32', '52.231.36.175/32', '52.231.207.185/32', '52.238.119.141/32', '52.242.23.189/32', '52.244.160.207/32', '104.215.11.144/32', '104.215.62.195/32', '138.91.237.237/32', '2603:1027::/48', '2603:1029:100::/48', '2603:1037::/48', '2603:1039:100::/48', '2603:1047::/48', '2603:1049:100::/48', '2603:1057::/48', '2620:1ec:6::/48', '2620:1ec:40::/42', '2620:1ec:42::/48', '2a01:111:203e:2::/64', '2a01:111:f404:9401::/64', '2a01:111:f404:a001::/64'], 'tcpPorts': '443', 'expressRoute': True, 'category': 'Allow', 'required': True}, 


#helper function to uniqify a list
#https://www.peterbe.com/plog/fastest-way-to-uniquify-a-list-in-python-3.6
def f12(seq):
    # Raymond Hettinger
    # https://twitter.com/raymondh/status/944125570534621185
    return list(dict.fromkeys(seq))


# helper to call the webservice and parse the response
def webApiGet(methodName, instanceName, clientRequestId):
    ws = "https://endpoints.office.com"
    requestPath = ws + '/' + methodName + '/' + instanceName + '?clientRequestId=' + clientRequestId
    #print(requestPath)
    request = urllib.request.Request(requestPath)
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode())

# path where client ID and latest version number will be stored
datapath = os.environ['TEMP'] + '\endpoints_clientid_latestversion.txt'
# fetch client ID and version if data exists; otherwise create new file
if os.path.exists(datapath):
    with open(datapath, 'r') as fin:
        clientRequestId = fin.readline().strip()
        latestVersion = fin.readline().strip()
        
        print("\n")
        print("Office365 Endpoints Downloader")
        print("clientID: "+clientRequestId)
        print("latest version: "+latestVersion)
        print("\n")
else:
    clientRequestId = str(uuid.uuid4())
    latestVersion = '0000000000'
    with open(datapath, 'w') as fout:
        fout.write(clientRequestId + '\n' + latestVersion)
# call version method to check the latest version, and pull new data if version number is different

version = webApiGet('version', 'Worldwide', clientRequestId)

if version['latest'] > latestVersion:
    print('New version of Office 365 worldwide commercial service instance endpoints detected')
    # write the new version number to the data file
    with open(datapath, 'w') as fout:
        fout.write(clientRequestId + '\n' + version['latest'])
    # invoke endpoints method to get the new data
    endpointSets = webApiGet('endpoints', 'Worldwide', clientRequestId)
    # filter results for Allow and Optimize endpoints, and transform these into tuples with port and category
    
    #print(endpointSets)
    
    flatUrls = []
    for endpointSet in endpointSets:
        if endpointSet['category'] in ('Optimize', 'Allow', 'Default'):
            category = endpointSet['category']
            urls = endpointSet['urls'] if 'urls' in endpointSet else []
            #tcpPorts = endpointSet['tcpPorts'] if 'tcpPorts' in endpointSet else ''
            #udpPorts = endpointSet['udpPorts'] if 'udpPorts' in endpointSet else ''
            serviceArea = endpointSet['serviceArea'] if 'serviceArea' in endpointSet else ''
            #flatUrls.extend([(category, url, tcpPorts, udpPorts) for url in urls])
            #flatUrls.extend([(category, url, serviceArea) for url in urls])
            flatUrls.extend([(url, serviceArea) for url in urls])
    
    flatIps = []
    flatIps6 = []
    for endpointSet in endpointSets:
        if endpointSet['category'] in ('Optimize', 'Allow', 'Default'):
            ips = endpointSet['ips'] if 'ips' in endpointSet else []
            category = endpointSet['category']
            # IPv4 strings have dots while IPv6 strings have colons
            ip4s = [ip for ip in ips if '.' in ip]
            #tcpPorts = endpointSet['tcpPorts'] if 'tcpPorts' in endpointSet else ''
            #udpPorts = endpointSet['udpPorts'] if 'udpPorts' in endpointSet else ''
            serviceArea = endpointSet['serviceArea'] if 'serviceArea' in endpointSet else ''
            #flatIps.extend([(category, ip, tcpPorts, udpPorts) for ip in ip4s])
            #flatIps.extend([(category, ip, serviceArea) for ip in ip4s])
            flatIps.extend([(ip, serviceArea) for ip in ip4s])
            
            # IPv4 strings have dots while IPv6 strings have colons
            ip6s = [ip for ip in ips if ':' in ip]
            #flatIps6.extend([(category, ip, serviceArea) for ip in ip6s])
            flatIps6.extend([(ip, serviceArea) for ip in ip6s])
    
    print('IPv6 Firewall IP Address Ranges')        
    #print(flatIps6)
    #print(',whitelist\r\n'.join(sorted(set([ip for (category, ip, serviceArea) in flatIps6]))))
    #print(',whitelist\r\n'.join(sorted(set([ip for (ip, serviceArea) in flatIps6]))))
    
    #break this out into steps
    ip6Set=[]
    for (ip, serviceArea) in flatIps6:
        ipList=ip+","+feed_col_whitelist+","+feed_col_whitelist_name+","+serviceArea.lower()
        #print(ipList)
        ip6Set.append(ipList)
    
    #print('\r\n'.join(sorted(f12(ip6Set))))
    lua_match_list_ip6='\n'.join(sorted(f12(ip6Set)))
    
    #print out the parser
    with open(parser_name + '-ip6.csv', 'w') as f:
        f.write(lua_match_list_ip6)
        
    print('IPv4 Firewall IP Address Ranges')
    #print(','.join(sorted(set([ip for (category, ip, tcpPorts, udpPorts) in flatIps]))))
    #print(flatIps)
    #generate csv for ip/cidr for netwitness
    #print(',whitelist\r\n'.join(sorted(set([ip for (category, ip, serviceArea) in flatIps]))))
    #print(',whitelist\r\n'.join(sorted(set([ip for (ip, serviceArea) in flatIps]))))
    
    #break this out into steps
    ip4Set=[]
    for (ip, serviceArea) in flatIps:
        ipList=ip+","+feed_col_whitelist+","+feed_col_whitelist_name+","+serviceArea.lower()
        #print(ipList)
        ip4Set.append(ipList)
    
    #print('\r\n'.join(sorted(f12(ip4Set))))
    lua_match_list_ip='\n'.join(sorted(f12(ip4Set)))
    
    #print out the parser
    with open(parser_name + '-ip4.csv', 'w') as f:
        f.write(lua_match_list_ip)
    
    print('URLs Lua Parser')
    #print(','.join(sorted(set([url for (category, url, tcpPorts, udpPorts) in flatUrls]))))
    #print(flatUrls)
    #generate lua_import structure for parser matching due to wildcard requirements
    #print('",\r\n'.join(sorted(set([url for (category, url, serviceArea) in flatUrls]))))
    #print('",\r\n'.join(sorted(set([url for (url, serviceArea) in flatUrls]))))
    
    #break this out into steps
    urlSet=[]
    for (url, serviceArea) in flatUrls:
        #["aadrm.com"] = "
        urlList="[\""+url+"\"] = {\""+feed_col_whitelist+"\",\""+feed_col_whitelist_name+"\",\""+serviceArea.lower()+"\"},"
        #print(urlList)
        urlSet.append(urlList)
    
    #print('\r\n'.join(sorted(f12(urlSet))))
    
    #end for loop
           
    #at the end sort and unique the list
    #print('\r\n'.join(sorted(f12(urls))))

    #join the list to a string
    lua_match_list='\n'.join(sorted(f12(urlSet)))
    #trim the trailing , from the last line
    lua_match_list = lua_match_list[:-1]

    #print(lua_script_pre)
    #print(lua_match_list)
    #print(lua_script_post)

    #print out the parser
    with open(parser_name + '.lua', 'w') as f:
        #f.write(parser_date_string + parser_name_string + lua_script_pre + lua_match_list + lua_script_post)
        f.write(parser_date_string + parser_name_string + lua_script_pre + lua_match_list + lua_script_post)

else:
    print('Office 365 worldwide commercial service instance endpoints are up-to-date\n')