#!/usr/bin/python
#====LINE ABOVE IS MAGICKS! MUST BE FIRST LINE OF FILE===
print "Content-Type:text/html\n"
#===THIS LINE IS ALSO MAGIC!====
print ""
#====THIS LINE IS ALSO REQUIRED====

import cgi
import cgitb
cgitb.enable()

def FStoDict(): #Converts mutant FieldStorage dictionary into regular d$
    cgiDict = cgi.FieldStorage()
    cleanDict = {}
    FSKeys = cgiDict.keys()
    for key in FSKeys:
        cleanDict[key] = cgiDict[key].value
    return cleanDict

requestedDict = FStoDict()
# requestedDict = {'city':"South Bend","state":"Indiana"}
city = requestedDict['city']
city = city.lower()
state = requestedDict['state']
state = state.lower()
inStream = open('requestedCities.csv','r')
requestedCities = inStream.read()
inStream.close()
cityAndState = city + "," + state
inStream2 = open('data/cities.csv','r')
citiesOnSite = inStream2.read()
inStream2.close()
if not cityAndState in requestedCities and not city in citiesOnSite:
    inStream = open('requestedCities.csv','a')
    requestedCities = inStream.write(city + "," + state + "\n")
    inStream.close()

print """
index.html goes here when the file is good to go
"""

