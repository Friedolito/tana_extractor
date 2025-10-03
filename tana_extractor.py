
from bs4 import BeautifulSoup
import pandas as pd
from datetime import timedelta, date, time
import requests

"""
The function takes a URL that points to a published tana search view table and recreats it as a pandas df. 
It only works for tables that are published as articles, no in the tana view.
"""

def extract_tana_table(url=''):
    """
    creates a df from a tana table
    """
    html_file = requests.get(url)

    if html_file.status_code == 200:
        #if status ok, writes the decoded HTML response body into opened page.html
        with open("page.html", "w", encoding="utf-8") as file: 
            file.write(html_file.text) #writes html_file.text to page.html
        print("HTML file downloaded successfully.")
    else:
        print("Failed to retrieve the webpage. Status code:", html_file.status_code)

    soup = BeautifulSoup(html_file.text, 'html.parser')

    ## find table headers ✓
    table_headers = []
    for n in soup.body.table.thead.find_all('th'):
        table_headers.append(n.div.get_text(strip=True))

    ## find rows in table  
    ### hierarchy of one row: tr (level row) > th (entries in rows) > div oder tr > td > div
    ### every other element is empty 
    rows_tbody = soup.table.tbody.contents
    rows_tbody = rows_tbody # sliced starting with 1 and then every other element

    list_of_rows = []
    for n in rows_tbody: #level th/td
        row = n.contents
        list_of_rows.append(row)


    ## find content in cells and create a list with content for each row 
    storing_strings = []
    for row in list_of_rows:
        string_in_cells = []
        for cell in row:
            string = cell.get_text(strip=True)
            string_in_cells.append(string)
        storing_strings.append(string_in_cells)

    ## create df for activities 
    df = pd.DataFrame(data= storing_strings,columns= table_headers)

    # ensures that rows without a tag are excluded. This happens due to a Tana Bug
    df_excluded = df[df['Tags'] == ""] 
    df = df[df['Tags'] != ""] 

    # convert 'duration'str to time
    if df['duration (min)'].dtype == 'object':
        df['duration (min)'] = pd.to_numeric(df['duration (min)'], errors='coerce')
        df['duration (min)'] = pd.to_timedelta(df['duration (min)'], unit='m')
    else:
        pass

    # convert 'Today' to today's date
    df['Date'] = df['Date'].replace('Today', date.today())

    # add total time at the bottom 
    time_spend_today = df['duration (min)'].sum(skipna=True) # total time spend (sum automatically skips NaT values)
    totals_row = pd.DataFrame({
        'Time Spend Today': ['Total'],
        'duration (min)': [time_spend_today]
    })
    df = pd.concat([df, totals_row], ignore_index=True)

    return df

print(extract_tana_table())

