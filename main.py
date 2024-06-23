import requests
import pandas as pd
from bs4 import BeautifulSoup

URL = "https://allianceforcoffeeexcellence.org/nicaragua-2024/"

def aCE_url_to_rank_url_list(url:str) :
    # grab0 the table soup
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")

    table_soup = soup.body.find('table').select('tr')

    # get the urls and fill the rank_url_list
    rank_url_list = []
    for child_soup in table_soup:
        anchor_string = str(child_soup.select('td')[2].div.find('a'))
        href_index = anchor_string.find('href=') + 5
        anchor_string = anchor_string[href_index:]
        
        start_index = anchor_string.find('\"')
        end_index = anchor_string[start_index+1:].find('\"')
        rank_url_list.append(anchor_string[start_index+1:end_index+1])

    return rank_url_list[2:] # [2:] is for get rid of the repetation.

def rank_listing_url_to_inform_dict(url:str):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")

    # select the lot inform table
    lot_inform_candidate_list = soup.body.find_all('ul', attrs={'class': 'extra-details'})

    inform_dict = {}
    for lot_inform in lot_inform_candidate_list:
        lot_inform = lot_inform.select('li')

        # make the inform dict
        for lot in lot_inform:
            inform_dict[lot.select('div')[0].text] = lot.select('div')[1].text

    return inform_dict

def add_dataframe_rank_url_inform(old_dataframe:pd.DataFrame, farm_dict:dict, is_new=False):
    farm_dict_keys = list(farm_dict.keys())
    farm_dict_values = list(farm_dict.values())
    new_dataframe = pd.DataFrame(farm_dict_values,index=farm_dict_keys)

    if is_new == True:
        return new_dataframe

    return pd.concat([old_dataframe, new_dataframe], axis=1)



is_dataframe_empty = True
dataframe = None
ace_url_list = aCE_url_to_rank_url_list(URL)
print(ace_url_list)
for url in ace_url_list:
    # rank_listing_url_to_inform_dict(url)
    if is_dataframe_empty == True:
        dataframe = add_dataframe_rank_url_inform(None,rank_listing_url_to_inform_dict(url), is_new=True)
        is_dataframe_empty = False
    else:
        dataframe = add_dataframe_rank_url_inform(dataframe,rank_listing_url_to_inform_dict(url))

print(dataframe.T)

dataframe.T.to_csv('main.csv',sep=',',na_rep='NaN')