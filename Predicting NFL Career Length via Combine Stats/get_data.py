import re
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
    Add successful URL to dictionary to avoid multiple players with the same name problem

Done:
    If "St.", combine "St." with the next word
    Unless first name is "Amon-Ra", then last name should be "Stxx"
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
                #response = requests.get(url,headers=headers)
                response = requests.get(stem+"404")
                checkedNames[url] = True
                sleep(4) # Wait 4 seconds between requests
            elif response.status_code == 404 or checkedNames.get(url) == False: 
               url = f"{stem}{search_name[-1][0]}/{search_name[-1][:4]}{search_name[0][:2]}00.htm"
               checkedNames[url] = True

        print(url)
        #check if url is visited already
        if url not in checkedNames:
            #response = requests.get(url, headers=headers)
            response = requests.get(stem+"404")
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
                #response = requests.get(newurl, headers=headers)
                response = requests.get(stem+"404")
                checkedNames[newurl] = True
            if checkOtherNumbers > 99:
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
players['Career Length'] = players['Name'].progress_apply(get_player_career_length)

# Save updated dataset
players.to_csv('nfl_combine_with_career_length.csv', index=False)
