#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from bs4 import BeautifulSoup
import requests
from itertools import chain
from tqdm import tqdm_notebook as tqdm
import re


# In[51]:


def parse_bat_table(tbl):
    columns = tbl.find_all('th')
    columns = [col.text for col in columns]
    rows = tbl.find('tbody').find_all('tr')
    data = []
    for row in rows:
        cols = row.find_all('td')
        classes = cols[0].get("class")
        if classes is not None and "batsman-cell" in classes:
            data.append([col.text for col in cols])
    # Append tfoot and check for did not bat.
    did_not_bat = tbl.find('tfoot').find_all('tr')[1].text.split('Did not bat:')[1].strip('').split(',')
    [data.append([bat, 'not out', None, None, None, None, None, None])for bat in did_not_bat]
    
    # After parsing into a dataframe, clean and return it.
    df =  pd.DataFrame(data=data, columns=columns)
    df = df.apply(lambda x: clean_column(x), axis=0)
    df['is_not_out'] = df['\xa0'].apply(lambda x:  True if pd.isna(x)!=True and 'not out' in x else False)
    del df['\xa0']
    return df


# In[57]:


def parse_bowl_table(tbl, player_list):
    columns = tbl.find_all('th')
    columns = [col.text for col in columns]
    rows = tbl.find('tbody').find_all('tr')
    data = []
    for row in rows:
        cols = row.find_all('td')
        data.append([col.text for col in cols])
    bowl_df =  pd.DataFrame(data=data, columns=columns)
    diff_players = list(set(player_list).difference(set(bowl_df['BOWLING'])))
    no_bowl = []
    [no_bowl.append([player, None, None, None, None, None, None, None, None, None, None]) for player in diff_players]
    no_bowl = pd.DataFrame(data = no_bowl, columns = columns)
    df =  pd.concat([bowl_df, no_bowl])
    df = df.apply(lambda x: clean_column(x), axis=0)
    return df


# In[79]:


def clean_column(col):
    col = col.apply(lambda x: x.split('(')[0].strip() if pd.isna(x)!=True else x)
    col = col.apply(lambda x: re.sub('[^A-Za-z0-9. ]+', '', x) if pd.isna(x)!=True else x)
    col = col.fillna('0')
    return col


# In[92]:


def scrape_score_table(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    batsman_tables = soup.find_all('table', class_='batsman')
    bowling_tables = soup.find_all('table', class_='bowler')
    team1_bat = parse_bat_table(batsman_tables[0])
    team2_bat = parse_bat_table(batsman_tables[1])
    
    team1_bowl = parse_bowl_table(bowling_tables[1], team1_bat['BATTING'])
    team2_bowl = parse_bowl_table(bowling_tables[0], team2_bat['BATTING'])
    team1_merged = team1_bat.merge(team1_bowl, left_on='BATTING', right_on='BOWLING', how='inner', suffixes=('_bat', '_bowl') )
    del team1_merged['BOWLING']
    team1_merged.rename(columns={'BATTING': 'player_name'}, inplace=True)
    team2_merged = team2_bat.merge(team2_bowl, left_on='BATTING', right_on='BOWLING', how='inner', suffixes=('_bat', '_bowl') )
    del team2_merged['BOWLING']
    team2_merged.rename(columns = {'BATTING': 'player_name'}, inplace=True)
    concated_df =  pd.concat([team1_merged, team2_merged])
    concated_df.set_index('player_name', inplace=True)
    return concated_df.T.to_dict()


# In[6]:


URL1 = 'https://www.espncricinfo.com/series/ipl-2021-1249214/punjab-kings-vs-delhi-capitals-29th-match-1254086/full-scorecard'
URL2 = 'https://www.espncricinfo.com/series/ipl-2021-1249214/rajasthan-royals-vs-sunrisers-hyderabad-28th-match-1254085/full-scorecard'
URL3 = 'https://www.espncricinfo.com/series/ipl-2021-1249214/punjab-kings-vs-royal-challengers-bangalore-26th-match-1254083/full-scorecard'


# In[98]:


scrape_score_table(URL1)


# In[95]:


scrape_score_table(URL2)


# In[96]:


scrape_score_table(URL3)


# In[ ]:




