#!/usr/bin/python
#====LINE ABOVE IS MAGICKS! MUST BE FIRST LINE OF FILE===
print "Content-Type:text/html\n"
#===THIS LINE IS ALSO MAGIC!====
print ""
#====THIS LINE IS ALSO REQUIRED====

import cgi
import cgitb
cgitb.enable()

#Toggle debug global to turn on/off debuggig print statements
#Set to False by default
debug = False

def FStoDict(): #Converts mutant FieldStorage dictionary into regular dictionary
    cgiDict = cgi.FieldStorage()
    cleanDict = {}
    FSKeys = cgiDict.keys()
    for key in FSKeys:
        cleanDict[key] = cgiDict[key].value
    return cleanDict

def reformatList(List): #Converts .readlines output into list with sublist per row, and element per cell.
    pos = 0
    while pos < len(List):
        List[pos] = List[pos].strip('\r\n') #Strips tabs and enters
        rowList = List[pos].split(',')
        List[pos] = rowList
        pos += 1
    return List
    
def file_Readlines(address): #Returns .readlines of file at address
    inStream = open(address,'r')
    csvList = inStream.readlines()
    inStream.close()
    if debug: print "READ SUCCESS"
    formatted = reformatList(csvList)
    if debug: print "FORMAT SUCCESS"
    return formatted
   
def get_Condition_DB(city,Type): #Returns file name of condition database of Type for city
    csvList = file_Readlines('data/city_dbs.csv') #Gets database directory database
    if debug: print "EXTRACTION SUCCESS"
    for group in csvList:
        if group[0] == city:
            if Type == 'precip':
                return group[1]
            else:
                return group[2]
        
           
def create_Condition_List(DBpath): #Returns condition data from database at DBpath as formatted list
    csvList = file_Readlines(DBpath) #Gets condition database at address DBpath
    condList = []
    for line in csvList[4:]:
        year = line[0][:4]
        value = line[1]
        row = [year,value] #List will contain sublist per year:value pair, with an element for each within the sublist
        condList.append(row)
    return condList

def build_Table_Body(condList): #Builds HTML body section of table representing data in input list
    contents = ''
    for el in condList:
        Row = '\t\t\t<tr>'
        for cell in el:
            Row += '<td>' + cell + '</td>'
        Row += '</tr> \n'
        contents += Row
    tableBody = '\t<tbody>\n' + contents + '\t\tS</tbody>\n'
    return tableBody

def build_Cond_Table(condList,Type): #Builds HTML table, header included, for specific database and condition type
    if Type == 'precip': #Header changes depending on type
        measure = 'Annual Total Precipitation (In)'
    else:
        measure = 'Annual Mean Temperature (F)'
    tableHeader = """\
    <table border="1">
    <thead>
        <tr>
            <th>Year</th>
            <th>%s</th>
        </tr>
    </thead>\n
    """ % (measure) #Replaces %s in string with value of var measure
    tableBody = build_Table_Body(condList)
    table = tableHeader + tableBody + '</table>\n'
    return table

def list_Cities():
    citiesList = file_Readlines('data/cities.csv')

#Global string containing HTML page body section. Only used if city query given. Used in main()
htmlBody = """\
<h2>%s</h2>
<div>
    <h3>Precipitation Data</h3>
    %s
</div>
<div>
    <h3>Temperature Data</h3>
    %s
</div>
"""
#%s is replaced by table for each type of Data

#Global string containing code for entire HTML page. Used in main()
htmlMain = """\
<!DOCTYPE html>
<html>
    <head>
        <title>Test City Page</title>
    </head>
    <body>
        <div id="description">
            <p>This is a test page for the city.py script.
            <br>As of now, it can only work properly through a manual query.
            <br>It can display extract and display the condition data on a chosen city
            <br>as a pair of tables. In the future, the script will be modified
            <br>to become beautiful, and to display the data as graphs.
        </div>
        %s
    </body>
</html>
"""
#%s is replaced by the pageBody string, as modified by main().

def main(): #Takes in query containing city name, and returns HTML page with tables for precipitation and temperature data for that city.
    args = FStoDict()
    if 'city' not in args:
        pageBody = 'Please select a city!'
    #else:
    #city = args['city']
        #city = city.lower()
      #  if city not in list_Cities():
       #     pageBody = """\
        #    The city you have requested does not currently have information available.
         #   <br>Please enter a valid city or <a href="index.html/#contact">request</a> that the city be added to the website.      
          #  """
    else:
        city = args['city']
        precipList = create_Condition_List(get_Condition_DB(city,'precip'))
        tempList = create_Condition_List(get_Condition_DB(city,'temp'))
        precipTable = build_Cond_Table(precipList,'precip')
        tempTable = build_Cond_Table(tempList,'temp')
        pageBody = htmlBody % (city.capitalize(),precipTable,tempTable)
    website = htmlMain % (pageBody)
    return website
    
print main()
