#!/usr/bin/python
#====LINE ABOVE IS MAGICKS! MUST BE FIRST LINE OF FILE===
print "Content-Type:text/html\n"
#===THIS LINE IS ALSO MAGIC!====
print ""
#====THIS LINE IS ALSO REQUIRED====

import cgi
import cgitb
cgitb.enable()

def FStoDict(): #Converts mutant FieldStorage dictionary into regular dictionary
    cgiDict = cgi.FieldStorage()
    cleanDict = {}
    FSKeys = cgiDict.keys()
    for key in FSKeys:
        cleanDict[key] = cgiDict[key].value
    return cleanDict
    
def main():
    args = FStoDict()
    if 'city' not in args:
        return 'Please select a city.'
    else:
        return args['city']

htmlStr = "<html>\n <head>\n <title>City Page Py</title>\n </head>\n "
htmlStr += "<body>\n "
htmlStr += "<p>This is test page for the city.py script.\n As of now, it just displays the city name.\n """
htmlStr += "This will be modified to print an actual page for the city data in the future.</p>\n "
htmlStr += "<p>" + main() + "</p>\n "
htmlStr += "</body>\n </html>"

print htmlStr