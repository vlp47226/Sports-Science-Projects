import re
from time import sleep
from urllib import response
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
tqdm.pandas()
# Load your CSV
stem = "https://www.pro-football-reference.com/players/"
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
checkedNames = {}

def get_player_career_length(player_name):
    try:
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
        print(result)
        years = [int(link.text) for link in soup.find_all('a') if link.text.isdigit()]
        if years:
            return len(set(years))  # Count unique years
    except Exception as e:
        return None

# Add career length to your dataset

player_name = "Brian Westbrook"

lengthOfCareer = get_player_career_length(player_name)
print(player_name+": ", lengthOfCareer)