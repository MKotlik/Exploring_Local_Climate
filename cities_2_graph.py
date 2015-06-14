#!/usr/bin/python
# ====LINE ABOVE IS MAGICKS! MUST BE FIRST LINE OF FILE===
print "Content-Type:text/html\n"
# ===THIS LINE IS ALSO MAGIC!====
print ""
# ====THIS LINE IS ALSO REQUIRED====

import cgi
import cgitb

cgitb.enable()

# Toggle debug global to turn on/off debugging print statements
# Set to False by default
debug = False
DEBUG2 = False
DEBUG3 = False

# Global string containing HTML page body section. Only used if city query given. Used in main()
HTML_BODY_1CITY = """\
<div>
%s
</div>
<div>
    %s
</div>
<div>
    %s
</div>
"""
# %s is replaced by table for each type of Data
# div1 - city stats, div2- precip_graph, div3- temp_graph


HTML_BODY_2CITY = """\
<div>
<h3>%s</h3>
%s
</div>
<div>
<h3>%s</h3>
%s
</div>
<div>
<h3>Comparison</h3>
%s
</div>
<div>
    %s
</div>
<div>
    %s
</div>
"""
# div1 - city1 stats, div2 - city2 stats, div3 - comparison stats, div4 - precip_graph, div5 - temp_graph


def fs_to_dict():  # Converts mutant FieldStorage dictionary into regular dictionary
    cgi_dict = cgi.FieldStorage()
    clean_dict = {}
    fs_keys = cgi_dict.keys()
    for key in fs_keys:
        clean_dict[key] = cgi_dict[key].value
    return clean_dict


def reformat_list(csv_list):  # Converts .readlines output into list with sublist per row, and element per cell.
    pos = 0
    while pos < len(csv_list):
        csv_list[pos] = csv_list[pos].strip('\r\n')  # Strips tabs and enters
        row_list = csv_list[pos].split(',')
        csv_list[pos] = row_list
        pos += 1
    return csv_list


def file_readlines(address):  # Returns .readlines of file at address
    in_stream = open(address, 'r')
    csv_list = in_stream.readlines()
    in_stream.close()
    if debug:
        print "CSV READ SUCCESS"
    formatted = reformat_list(csv_list)
    if debug:
        print "CSV FORMAT SUCCESS"
    return formatted


def get_condition_db(city, cond_type):  # Returns file name of condition database of Type for city
    csv_list = file_readlines('data/city_dbs.csv')  # Gets database directory database
    if debug:
        print "CSV EXTRACTION SUCCESS"
    for group in csv_list:
        if group[0] == city:
            if cond_type == 'precip':
                return group[1]
            else:
                return group[2]


def create_condition_list(db_path):  # Returns condition data from database at DBpath as formatted list
    csv_list = file_readlines(db_path)  # Gets condition database at address DBpath
    cond_list = []
    for line in csv_list[4:]:
        year = line[0][:4]
        value = line[1]
        row = [year,
               value]  # List will contain sublist per year:value pair, with an element for each within the sublist
        cond_list.append(row)
    return cond_list


def shorten_years_in_list(cond_list):
    pos = 0
    while pos < len(cond_list):
        cond_list[pos][0] = "'" + cond_list[pos][0][-2:]
        pos += 1
    return cond_list


def build_table_body(cond_list):  # Builds HTML body section of table representing data in input list
    contents = ''
    for el in cond_list:
        row = '\t\t\t<tr>'
        for cell in el:
            row += '<td>' + cell + '</td>'
        row += '</tr> \n'
        contents += row
    table_body = '\t<tbody>\n' + contents + '\t\t</tbody>\n'
    return table_body


def build_cond_table(cond_list,
                     cond_type):  # Builds HTML table, header included, for specific database and condition type
    if cond_type == 'precip':  # Header changes depending on type
        measure = 'Annual Mean Precipitation (In)'
        table_id = 'precip_table'
        graph_id = '#precip_graph'
    else:
        measure = 'Annual Total Precipitation (In)'
        table_id = 'temp_table'
        graph_id = '#temp_graph'
    table_header = """\
    <table id="%s" class="highchart_table" data-graph-container="%s" data-graph-type="line" style="display:none">
        <thead>
            <tr>
                <th>Year</th>
                <th>%s</th>
            </tr>
        </thead>
    """ % (table_id, graph_id, measure)  # Replaces %s in string with value of var measure
    table_body = build_table_body(cond_list)
    table = table_header + table_body + '\t</table>'
    return table


def list_cities():
    cities_list = file_readlines('data/cities.csv')
    return cities_list


def retrieve_validate_city():
    cgi_args = fs_to_dict()
    if DEBUG2:
        cgi_args = {'city': 'Chicago'}
    if 'city' not in cgi_args:
        city = 'No city chosen!'
        page_body = 'Please select a city!'
        return city, page_body
    city = cgi_args['city'].lower()
    if [city] not in list_cities():
        page_body = """\
        The city you have requested does not currently have information available.
        <br>Please enter a valid city or <a href="index.html/#contact">request</a> that the city be added to the website.      
        """
        return city, page_body
    page_body = ''
    return city, page_body


def retrieve_validate_2_cities():
    cgi_args = fs_to_dict()
    if DEBUG2:
        cgi_args = {'city1': 'Chicago', 'city2': 'wichita'}
    if 'city1' not in cgi_args and 'city2' not in cgi_args:
        city1 = None
        city2 = None
        page_body = 'Please select a city!'
        return city1, city2, page_body
    if 'city1' in cgi_args:
        city1 = cgi_args['city1'].lower()
    else:
        city1 = None
    if 'city2' in cgi_args:
        city2 = cgi_args['city2'].lower()
    else:
        city2 = None
    cities_list = list_cities()
    if (city1 is not None and [city1] not in cities_list) or (city2 is not None and [city2] not in cities_list):
        page_body = """\
        One or more of the cities you have requested do not currently have information available.
        <br>Please enter valid cities or <a href="index.html/#contact">request</a> that a city be added to the website.
        """
        return city1, city2, page_body
    page_body = ''
    return city1, city2, page_body


def build_precip_table(city):
    precip_list = shorten_years_in_list(create_condition_list(get_condition_db(city, 'precip')))
    precip_table = build_cond_table(precip_list, 'precip')
    return precip_table


def build_temp_table(city):
    temp_list = shorten_years_in_list(create_condition_list(get_condition_db(city, 'temp')))
    temp_table = build_cond_table(temp_list, 'temp')
    return temp_table


def timeperiod_average(cond_list, bounds_list):
    start_year = bounds_list[0]
    end_year = bounds_list[1]
    total = 0
    years = 0
    for el in cond_list:
        if start_year <= int(el[0]) <= end_year:
            total += float(el[1])
            years += 1
    average = float(total) / years
    return average


def compare_timeperiod_averages(cond_list, time_period_1, time_period_2):
    time_period_1_average = timeperiod_average(cond_list, time_period_1)
    time_period_2_average = timeperiod_average(cond_list, time_period_2)
    difference = abs(time_period_1_average - time_period_2_average)
    return difference


def rate_increase_data(list_2d):
    sum_x = 0
    sum_y = 0
    sum_x2 = 0
    sum_xy = 0
    for el in list_2d:
        sum_x += float(el[0])
    for el in list_2d:
        sum_y += float(el[1])
    for el in list_2d:
        sum_x2 += float(el[0]) ** 2
    for el in list_2d:
        sum_xy += float(el[0]) * float(el[1])
    if sum_x == 0:
        return 0
    mean_x = sum_x / len(list_2d)
    mean_y = sum_y / len(list_2d)
    rate_change = (sum_xy - sum_x * mean_y) / (sum_x2 - sum_x * mean_x)
    return rate_change


def change_over_time(cond_list, bounds_list):
    start_year = bounds_list[0] - 1959
    end_year = bounds_list[1] - 1959
    chosen_list = cond_list[start_year:(end_year + 1)]
    rate_change = rate_increase_data(chosen_list)
    approx_change = rate_change * len(chosen_list)
    return approx_change


def rate_change_over_time(cond_list, bounds_list):
    start_year = bounds_list[0] - 1959
    end_year = bounds_list[1] - 1959
    chosen_list = cond_list[start_year:(end_year + 1)]
    rate_change = rate_increase_data(chosen_list)
    approx_change = rate_change * len(chosen_list)
    return rate_change, approx_change


def read_html(address):
    in_stream = open(address, 'r')
    html_page = in_stream.read()
    in_stream.close()
    if debug:
        print 'HTML READ SUCCESS'
    return html_page


STAT_DIV = """\
<h3>Precipitation</h3>
<p>
    Average Annual Total Precipitation Over Time Period: %s
    <br>Approximate Rate of Change per Year: %s
    <br>Approximate Change over Time: %s
</p>
<h3>Temperature</h3>
<p>
    Average Annual Temperature Over Time Period: %s
    <br>Approximate Rate of Change per Year: %s
    <br>Approximate Change over Time: %s
</p>
"""


COMPARE_STAT_DIV = """\
<h3>Precipitation</h3>
<p>
    %s
    %s
    %s
</p>
<h3>Temperature</h3>
<p>
    %s
    %s
    %s
</p>
"""

COMPARE_STAT_DIV_LINES = ['The average annual precipitation has been %sin greater in %s than in %s',
                          '<br>The approximate rate of change per year has been %sin %s in %s than in %s'
                          '<br>The approximate total change in annual precipitation has been %sin %s in %s than in %s'
                          'The average annual mean temperature has been %sF greater %s than in %s'
                          '<br>The approximate rate of change per year has been %sF %s in %s than in %s'
                          '<br>The approximate total change in annual mean temperature has been %sF %s in %s than in %s'
                          ]


def display_stats(city):
    all_years = [1959, 2014]
    precip_list = create_condition_list(get_condition_db(city, 'precip'))
    temp_list = create_condition_list(get_condition_db(city, 'temp'))
    precip_average = timeperiod_average(precip_list, all_years)
    temp_average = timeperiod_average(temp_list, all_years)
    precip_rate, precip_change = rate_change_over_time(precip_list, all_years)
    temp_rate, temp_change = rate_change_over_time(temp_list, all_years)
    mod_stat_div = STAT_DIV % (precip_average, precip_rate, precip_change, temp_average, temp_rate, temp_change)
    return mod_stat_div


def return_stats(city):
    all_years = [1959, 2014]
    precip_list = create_condition_list(get_condition_db(city, 'precip'))
    temp_list = create_condition_list(get_condition_db(city, 'temp'))
    precip_average = timeperiod_average(precip_list, all_years)
    temp_average = timeperiod_average(temp_list, all_years)
    precip_rate, precip_change = rate_change_over_time(precip_list, all_years)
    temp_rate, temp_change = rate_change_over_time(temp_list, all_years)
    return precip_average, precip_rate, precip_change, temp_average, temp_rate, temp_change


def average_comparison(stat_line, city1_stat, city2_stat, city1_name, city2_name):
    difference = abs(city1_stat - city2_stat)
    greater_average = max(city1_stat, city2_stat)
    if city1_stat == greater_average:
        greater_city = city1_name
        lesser_city = city2_name
    else:
        greater_city = city2_name
        lesser_city = city1_name
    stat_sent = COMPARE_STAT_DIV_LINES[stat_line] % (difference, greater_city, lesser_city)
    return stat_sent


def rate_change_comparison(stat_line, city1_stat, city2_stat, city1_name, city2_name):
    farther_stat = max(abs(city1_stat), abs(city2_stat))
    if city1_stat == farther_stat:
        difference = city1_stat - city2_stat
        if difference >= 0:
            direction = 'greater'
        else:
            direction = 'less'
        greater_city = city1_stat
        lesser_city = city2_stat
    else:
        difference = city2_stat - city1_stat
        if difference >= 0:
            direction = 'greater'
        else:
            direction = 'less'
        greater_city = city2_stat
        lesser_city = city1_stat
    stat_sent = COMPARE_STAT_DIV_LINES[stat_line] % (difference, direction, greater_city, lesser_city)
    return stat_sent


def fill_compare_stat_div(city1, city2):
    city1_precip_average, city1_precip_rate, city1_precip_change, city1_temp_average, city1_temp_rate, city1_temp_change = return_stats(city1)
    city2_precip_average, city2_precip_rate, city2_precip_change, city2_temp_average, city2_temp_rate, city2_temp_change = return_stats(city2)
    average_precip_compare = average_comparison(0, city1_precip_average, city2_precip_average, city1.capitalize(), city2.capitalize())
    rate_precip_compare = rate_change_comparison(1, city1_precip_rate, city2_precip_rate, city1.capitalize(), city2.capitalize)
    change_precip_compare = rate_change_comparison(2, city1_precip_change, city2_precip_change, city1.capitalize(), city2.capitalize())
    average_temp_compare = average_comparison(3, city1_temp_average, city2_temp_average, city1.capitalize(), city2.capitalize())
    rate_temp_compare = rate_change_comparison(4, city1_temp_rate, city2_temp_rate, city1.capitalize(), city2.capitalize)
    change_temp_compare = rate_change_comparison(5, city1_temp_change, city2_temp_change, city1.capitalize(), city2.capitalize())
    compare_div = COMPARE_STAT_DIV % (average_precip_compare, rate_precip_compare, change_precip_compare, average_temp_compare, rate_temp_compare, change_temp_compare)
    return compare_div



def compare_cities(city1, city2):
    city1_stats = display_stats(city1)
    city2_stats = display_stats(city2)
    compare_stats = fill_compare_stat_div(city1, city2)
    return city1_stats


def display_one_city(city):
    page_body = HTML_BODY_1CITY % (display_stats(city), build_precip_table(city), build_temp_table(city))
    return page_body


def display_page_body(city1, city2):
    if city1 is not None and city2 is not None:
        page_body = compare_cities(city1, city2)
    elif city1 is not None:
        page_body = display_one_city(city1)
    else:
        page_body = display_one_city(city2)
    return page_body


def display_city_title(city1, city2):
    if city1 is not None and city2 is None:
        title = '<h2>%s</h2>' % city1.capitalize()
    elif city1 is None and city2 is not None:
        title = '<h2>%s</h2>' % city2.capitalize()
    elif city1 is not None and city2 is not None:
        title = '<h2>Comparing %s and %s</h2>' % (city1.capitalize(), city2.capitalize())
    else:
        title = 'No cities chosen!'
    return title


def main():  # Takes in query containing city name, and returns HTML page with tables for precipitation and temperature data for that city.
    city1, city2, page_body = retrieve_validate_2_cities()
    if debug:
        city1 = 'Chicago'
        city2 = 'Wichita'
        page_body = ''
    if DEBUG3:
        city1 = None
        city2 = None
        page_body = 'Please select a city'
    html_main = read_html('cities_2.txt')
    if page_body == '':
        page_body = display_page_body(city1, city2)
    website = html_main % (display_city_title(city1, city2), page_body)
    return website


print main()


# print retrieve_validate_2_cities()

# print display_city_title(None, None)
