import re
from time import sleep
from urllib import response
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Load your CSV
players = pd.read_csv('NFL_Combine_and_pro_day_data_(1987-2021).csv')
stem = "https://www.pro-football-reference.com/players/"
'''
TODO:
    If "St.", combine "St." with the next word
        Unless first name is "Amon-Ra", then last name should be "Stxx"
    Add successful URL to dictionary to avoid multiple players with the same name problem

Done:
    if last name length < 4, pad with "x" done
    Problem: (A-Z).(A-Z). is sometimes "(A-Z)." or "(A-Z)(A-Z)
    hyphen(-) should be removed
    apostrophe(') should be removed
    
'''
checkedNames = {}
# Function to scrape career years from Pro Football Reference
def get_player_career_length(player_name):
    try:
        sleep(4) # Wait 4 seconds between requests
        player_name = player_name.replace("-", "").replace("'", "") # Replace hyphen with space
        search_name = player_name.split() # Split the player name for the URL
        if len(search_name[-1]) < 4:
            search_name[-1] = search_name[-1] + "x"*(4-len(search_name[-1]))

        url = f"{stem}{search_name[-1][0]}/{search_name[-1][:4]}{search_name[0][:2]}00.htm"
        if search_name[0] == "Amon-Ra":
            url = f"{stem}{search_name[-1][0]}/{search_name[-1][:4]}Stxx00.htm"
        if "." in search_name[0]:
            url = f"{stem}{search_name[-1][0]}/{search_name[-1][:4]}{search_name[0][0]}{search_name[0][2]}00.htm" #all the (A-Z). did not have a number different than 00
            #response = requests.get(None)
            if checkedNames.get(url) == False:
                #response = requests.get(url)
                response = requests.get(None)
                checkedNames[url] = True
                sleep(4) # Wait 4 seconds between requests
            elif response.status_code == 404 or checkedNames.get(url) == False: 
               url = f"{stem}{search_name[-1][0]}/{search_name[-1][:4]}{search_name[0][:2]}00.htm"
               checkedNames[url] = True

        print(url)
        #check if url is visited already
        if url not in checkedNames:
            #response = requests.get(url)
            response = requests.get(None)
            print("Novel URL")
        else:
            #response = requests.get(None)
            response = requests.get(None)
            print("Used URL")
        checkOtherNumbers = 0
        """If the player's URL doesn't exist, try other numbers"""
        while response.status_code == 404:
            newNum = str(checkOtherNumbers)
            newNum = "0"+newNum if newNum < 10 else newNum
            sleep(4) # Wait 4 seconds between requests
            newurl = url.replace("00", newNum)
            if checkedNames.get(newurl) == False:
                #response = requests.get(newurl)
                response = requests.get(None)
                checkedNames[newurl] = True
            if newNum > 99:
                return None
            checkOtherNumbers += 1
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find years active (use the player's stats table)
        years = [int(link.text) for link in soup.find_all('a') if link.text.isdigit()]
        if years:
            return len(set(years))  # Count unique years
    except Exception as e:
        return None

# Add career length to your dataset
players['Career Length'] = players['Name'].apply(get_player_career_length)

# Save updated dataset
players.to_csv('nfl_combine_with_career_length.csv', index=False)
