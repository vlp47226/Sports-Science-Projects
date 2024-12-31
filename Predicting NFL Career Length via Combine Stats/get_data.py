import pandas as pd
import requests
from bs4 import BeautifulSoup

# Load your CSV
players = pd.read_csv('NFL_Combine_and_pro_day_data_(1987-2021).csv')

# Function to scrape career years from Pro Football Reference
def get_player_career_length(player_name):
    try:
        # Format the player name for the URL
        search_name = player_name.lower().replace(' ', '-')
        url = f"https://www.pro-football-reference.com/players/{search_name[0]}/{search_name[:4]}{search_name.split()[-1][:2]}00.htm"
        response = requests.get(url)
        if response.status_code != 200:
            return None
        
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
