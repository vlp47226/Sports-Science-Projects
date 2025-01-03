This project revolves around the impossible yet interesting task of predicting the length of the career of an NFL player based on their combine stats. The dataset comes from https://github.com/josedv82/public_sport_science_datasets/tree/main .

The dataset: NFL_Combine_and_pro_day_data_(1987-2021).csv

The headers: Year,Name,College,POS,Height (in),Weight (lbs),Wonderlic,40 Yard,Bench Press,Vert Leap (in),Broad Jump (in),Shuttle,3Cone


TODO:
    Explore the dataset to see duplicates, data distributions, number of unique schools, etc.
    Remove players who have not yet retired. This can be done via checking if they have a 2024 season or if they have a hall of fame monitor
    Or Checking for When did Firstname Lastname retire?
    Could also predict the number of games they would play in versus number of years.
    Or predict the Weighted Career AV score
    Some players play on practice squads for multiple years after initially playing
    
The first step is to find all the available data regarding the length of as many of the players in the original NFL combine dataset

