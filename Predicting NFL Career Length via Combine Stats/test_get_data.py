import calendar
import re
import stat
from time import sleep
from turtle import pen
from urllib import response
import pandas as pd
import requests
from bs4 import BeautifulSoup
import soupsieve
from tqdm import tqdm
tqdm.pandas()
# Load your CSV
stem = "https://www.pro-football-reference.com/players/"
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
checkedNames = {}

def check_playerurl_with_year(url, year_drafted):
    '''
        Check player combine year from csv to:
        1) draft year in their bio
        2) nfl/pro day year
        If year input variable is different then the first of the two to be able to get, then the url is wrong   
    '''
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        return False
    soup = BeautifulSoup(response.content, 'html.parser')
    # check draft year in meta
    meta_data = soup.find(id = "meta")

    result = {}
    current_key=None
    for link in meta_data.find_all('p'):
        #print(link.text.strip())
        current_key = None
        for line in link.text.splitlines():
            line = line.strip()  # Remove leading and trailing whitespace
            if ':' in line:  # If the line contains a colon, it's a new key
                current_key, value = map(str.strip, line.split(':', 1))
                # Add the key with the value if the value is not empty
                if value:
                    result[current_key] = value
                else:
                    result[current_key] = ""  # Placeholder for now
            elif current_key:  # If there's no colon but we have a current key, it's the value
                result[current_key] = result[current_key] + line  # Append the value
    #print(result)
    # Parse born value to get the year, month, and day
    born = result.get("Born")
    space_split = born.split()
    month = space_split[0]
    month_num = list(calendar.month_name).index(month)
    day = space_split[1][:-1]  
    year = space_split[2][:-2]
    print(born.split("in"))
    city_state = born.split("in")[1]
    city, state = city_state.split(",")
    print(f'{player_name} was born on {month_num}/{day}/{year} in {city}, {state}')
    # Get highschool and state location
    highschool = result.get("High School")
    highschool = highschool.split("(")
    highschool_name = highschool[0].strip()
    highschool_state = highschool[1][:-1]
    print(f'{player_name} went to {highschool_name} in {highschool_state}')

    # Get Weighted Career AV
    career_AV = result.get("Weighted Career AV (100-95-...)", "0 0").split(" ")[0]
    print(f'{player_name} has a weighted career AV of {career_AV}')

    # Get Career start year
    draft = result.get("Draft", "0000")
    match = re.search(r'\b\d{4}\b', draft)
    if match:
        draft_year = int(match.group())
        print(f'{player_name} was drafted in {draft_year}')
    print(draft_year)
    print(year_drafted)
    if draft_year != year_drafted and draft_year != "0000":
        return True
    else:
        combine_data = soup.find(id = "all_combine")
        print(combine_data)
        if(combine_data):
            combine_data = combine_data.find(id="div_combine")
            for data in combine_data:
                print(data)
        else:
            print("No combine data")
            return False
    return False


def get_player_career_length(year,player_name):
        sleep(4) # Wait 4 seconds between requests
        player_name = player_name.replace("-", "").replace("'", "") # Replace hyphen with space
        if "St." in player_name:
            player_name = player_name.replace("St. ", "St.")
        search_name = player_name.split() # Split the player name for the URL
        if len(search_name[-1]) < 4:
            search_name[-1] = search_name[-1] + "x"*(4-len(search_name[-1]))
        isPlayerCorrect = False
        url = f"{stem}{search_name[-1][0]}/{search_name[-1][:4]}{search_name[0][:2]}00.htm"
        if search_name[0] == "Amon-Ra":
            url = f"{stem}{search_name[-1][0]}/{search_name[-1][:4]}Stxx00.htm"
        #elif "St." in search_name[0]:
        #    url = f"{stem}{search_name[-1][0]}/{search_name[-1][:4]}Stxx00.htm"
        elif "." in search_name[0]:
            url = f"{stem}{search_name[-1][0]}/{search_name[-1][:4]}{search_name[0][0]}{search_name[0][2]}00.htm" #all the (A-Z). did not have a number different than 00
            #response = requests.get(None)                                                                        #so we can check it only once
            if checkedNames.get(url) == False:
                #check if data is correct via combine year
                print("Is the player's combine year the same as in the url? ", check_playerurl_with_year(url, year))                #response = requests.get(stem+"404")
                checkedNames[url] = True
                sleep(4) # Wait 4 seconds between requests
            elif response.status_code == 404 or checkedNames.get(url) == False: 
               url = f"{stem}{search_name[-1][0]}/{search_name[-1][:4]}{search_name[0][:2]}00.htm"
               checkedNames[url] = True

        print(url)

        #check if url is visited already
        if url not in checkedNames:
            #check if data is correct via combine year, if true, return soup
            
            print("Is the player's combine year the same as in the url? ", check_playerurl_with_year(url, year))
            #response = requests.get(stem+"404")
            checkedNames[url] = True
            print("Novel URL")
        else:
            #response = requests.get(None)
            #Url has been visited, so we need to increase the number after the name
            response = requests.get(stem+"404")
            print("Used URL")
        
        checkOtherNumbers = 0
        """If the player's URL doesn't exist, try other numbers"""
        #check if players url matches the year in the csv, if not, then the url is wrong
        while response.status_code == 404:
            newNum = str(checkOtherNumbers)
            newNum = "0"+newNum if newNum < 10 else newNum
            sleep(4) # Wait 4 seconds between requests
            newurl = url.replace("00", newNum)
            if checkedNames.get(newurl) == False:
                #check if data is correct via combine year, if true, return soup
                print("Is the player's combine year the same as in the url? ", check_playerurl_with_year(url, year))
                #response = requests.get(stem+"404")
                checkedNames[newurl] = True
            if checkOtherNumbers > 99:
                return None
            checkOtherNumbers += 1
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find years active (use the player's stats table)
        #with open(f'{player_name}{checkOtherNumbers}.html', "w") as file:
        #    file.write(str(soup))
        #print(soup)
        meta_data = soup.find(id = "meta")
        #print(soup.find(id = ["meta"])) #_class = "stats_pullout"))

        #Get Meta Data that we dont already have ie High school and High school state,
        result = {}
        current_key=None
        for link in meta_data.find_all('p'):
            #print(link.text.strip())
            current_key = None
            for line in link.text.splitlines():
                line = line.strip()  # Remove leading and trailing whitespace
                if ':' in line:  # If the line contains a colon, it's a new key
                    current_key, value = map(str.strip, line.split(':', 1))
                    # Add the key with the value if the value is not empty
                    if value:
                        result[current_key] = value
                    else:
                        result[current_key] = ""  # Placeholder for now
                elif current_key:  # If there's no colon but we have a current key, it's the value
                    result[current_key] = result[current_key] + line  # Append the value
        #print(result)
        # Parse born value to get the year, month, and day

        born = result.get("Born")
        space_split = born.split()
        month = space_split[0]
        month_num = list(calendar.month_name).index(month)
        day = space_split[1][:-1]  
        year = space_split[2][:-2]
        city_state = born.split(" in ")[1]
        city, state = city_state.split(",")

        print(f'{player_name} was born on {month_num}/{day}/{year} in {city}, {state}')
        # Get highschool and state location
        highschool = result.get("High School")
        highschool = highschool.split("(")
        highschool_name = highschool[0].strip()
        highschool_state = highschool[1][:-1]
        print(f'{player_name} went to {highschool_name} in {highschool_state}')

        # Get Weighted Career AV
        career_AV = result.get("Weighted Career AV (100-95-...)", "0 0").split(" ")[0]
        print(f'{player_name} has a weighted career AV of {career_AV}')

        # Get Career start year
        draft = result.get("Draft", "0000")
        match = re.search(r'\b\d{4}\b', draft)
        if match:
            draft_year = match.group()
            print(f'{player_name} was drafted in {draft_year}')

        stat_pullout = soup.find(id="div_faq").find_all("p")
        #print(stat_pullout)
        last_played = None
        for link in stat_pullout:
            #print(link.text)
            if "games" in link.text:
                games = re.findall(r'\d+', link.text)
                print(f'{player_name} played {games[0]} games')
            elif "last played" in link.text:
                last_played = re.findall(r'\d+', link.text)
                print(f'{player_name} last played in {last_played[0]}')
        if games == None:
            games = 0
            last_played = 0
        elif last_played == None:
            return None
        
        
        # Get number of years active
        years = int(last_played[0]) - int(draft_year) + 1
        print(f'{player_name} played for {years} years')
        # Get number of games played

        output_dict = {
            "Born": born,
            "Birth Month": month_num,
            "Birth Day": day,
            "Birth Year": year,
            "City": city,
            "State": state,
            "High School": highschool_name,
            "High School State": highschool_state,
            "Weighted Career AV": career_AV,
            "Years Active": years,
            "Games Played": games[0],
            "Last Played": last_played[0],
        }
        return output_dict

# Add career length to your dataset

player_name = "Shaquill Griffin"
year = 2017
career_dict = get_player_career_length(year, player_name)
print(player_name+": ", career_dict)