import calendar
import re
import stat
from time import sleep
from urllib import response
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
tqdm.pandas()
# Load your CSV
players = pd.read_csv('C:\\Users\\Victor\'s Laptop\\Documents\\Sports Science\\Sports-Science-Projects\\Predicting NFL Career Length via Combine Stats\\NFL_Combine_and_pro_day_data_(1987-2021).csv')
stem = "https://www.pro-football-reference.com/players/"
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
'''
TODO:
    Still need to investigate why the 404 requests are excepting instead of returning 404
    Probably just try catch it
    

Done:
    If "St.", combine "St." with the next word
    Unless first name is "Amon-Ra", then last name should be "Stxx"
    if last name length < 4, pad with "x" done
    Problem: (A-Z).(A-Z). is sometimes "(A-Z)." or "(A-Z)(A-Z)
    hyphen(-) should be removed
    apostrophe(') should be removed
    Add successful URL to dictionary to avoid multiple players with the same name problem
    
'''

def check_playerurl_with_year(url, year):
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        return False
    soup = BeautifulSoup(response.content, 'html.parser')
    meta_data = soup.find(id = "tfooter_combine")
    born = meta_data.find("a").text
    print()
    born = born.split()
    year_born = born[-1]
    if year_born == year:
        return True
    return False

checkedNames = {}
def get_player_career_length(year,player_name):
        sleep(4) # Wait 4 seconds between requests
        player_name = player_name.replace("-", "").replace("'", "") # Replace hyphen with space
        if "St." in player_name:
            player_name = player_name.replace("St. ", "St.")
        search_name = player_name.split() # Split the player name for the URL
        if len(search_name[-1]) < 4:
            search_name[-1] = search_name[-1] + "x"*(4-len(search_name[-1]))

        url = f"{stem}{search_name[-1][0]}/{search_name[-1][:4]}{search_name[0][:2]}00.htm"
        if search_name[0] == "Amon-Ra":
            url = f"{stem}{search_name[-1][0]}/{search_name[-1][:4]}Stxx00.htm"
        #elif "St." in search_name[0]:
        #    url = f"{stem}{search_name[-1][0]}/{search_name[-1][:4]}Stxx00.htm"
        elif "." in search_name[0]:
            url = f"{stem}{search_name[-1][0]}/{search_name[-1][:4]}{search_name[0][0]}{search_name[0][2]}00.htm" #all the (A-Z). did not have a number different than 00
            #response = requests.get(None)                                                                        #so we can check it only once
            if checkedNames.get(url) == False:
                response = requests.get(url,headers=headers)
                #response = requests.get(stem+"404")
                checkedNames[url] = True
                sleep(4) # Wait 4 seconds between requests
            elif response.status_code == 404 or checkedNames.get(url) == False: 
               url = f"{stem}{search_name[-1][0]}/{search_name[-1][:4]}{search_name[0][:2]}00.htm"
               checkedNames[url] = True

        print(url)
        #check if url is visited already
        if url not in checkedNames:
            response = requests.get(url, headers=headers)
            #response = requests.get(stem+"404")
            checkedNames[url] = True
            print("Novel URL")
        else:
            #response = requests.get(None)
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
                response = requests.get(newurl, headers=headers)
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
        i = 0 
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
        city = space_split[3][:-1]
        state = space_split[4]
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
new_columns = players[['Year','Name']].progress_apply(get_player_career_length).apply(pd.Series)

# Concatenate the new columns to the original DataFrame
df = pd.concat([players, new_columns], axis=1)
# Save updated dataset
df.to_csv('nfl_combine_with_career_length.csv', index=False)
