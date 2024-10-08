## Introduction ##
This repo serves as the backend for my fyp project @https://github.com/w3ihong/FYP

## Docs ##
api end point : https://fyp-ml-ejbkojtuia-ts.a.run.app

- /run-pipeline
    - triggers the pipeline that performs ETL from Meta's API into our database

- /onboard_account/{id}
    - extracts data of a new signup, including posts and metrics. Should be triggered only once, upon connecting a new instagram account.
    - fields 
        - {id} : platform account id 

- /demographics/{id}?type={type}&timeframe={timeframe}
    - retrieves demographics data from Meta's API
    - fields 
        - {id}        : platform account id 
        - {type}      : type of users to extract, can be either "reached" or "engaged"
        - {timeframe} : duration, can be either "this_month" or "this_week"

- /trends_by_country/{country}
    - retrieves topics that trending in a specific country
    - fields
        - {country}   : full country name in lowercase and under scores (e.g united_states, singapore)

- /related_topics/{keyword}?timeframe={timeframe}&geo={geo}
    - retrives trending topics related to a given keyword
    - fields
        - {keyword}   : keyword in string, no specific format
        - {timeframe} : can be now 1-H, now 4-H, now 1-d, now 7-d, today 1-m, today 3-m, today 12-m or todau 5-y. defaults to now 7-d
        - {geo}       : string of the country abbreviation e.g. "US", "IN". defaults to (worldwide)

- /related_queries/{keyword}?timeframe={timeframe}&geo={geo}
    - rtrieves trendgin queries realted to a given keyword
    - same fields as topics


## hosting ##
- containerized with docker and hosted on google cloud run 
- data pipeline is triggered by gloud scheduer every day at 12 midnight SGT

## modules ##

- data pipeline 
    - flow
        1. get all accounts item  in db
        2. for each acc, extract all posts and check agaisnt db
        3. for each post get metrics and add to db
        4. check 


- trends
    - a custom proxy endpoint that utilizes the unofficial pytrends library, to get trending data from google trends, applying custom data manipulation and custom foramatting for our web app
            
- demographics 
    - custom end point to simplify the process of fetching reacehed and engaged demographcis from meta's api 