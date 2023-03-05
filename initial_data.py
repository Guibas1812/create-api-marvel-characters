import requests
import hashlib
import datetime
import pandas as pd

"""Script that accesses Marvel API and gets 30 characters."""

#Access Marvel API (needed: Timestamp, privkey, publickey, hash)
timestamp = datetime.datetime.now().strftime('%Y-%m-%d%H:%M:%S')
pub_key = '' #insert public key
priv_key = '' #insert private key
urlMarvel = 'http://gateway.marvel.com/v1/public/characters'

def hash_params():
    """ Marvel API requires server side API calls to include
    md5 hash of timestamp + public key + private key """
    hash_md5 = hashlib.md5()
    hash_md5.update(f'{timestamp}{priv_key}{pub_key}'.encode('utf-8'))
    hashed_params = hash_md5.hexdigest()
    return hashed_params

#We just want 30 Marvel characters 
params = {'ts': timestamp, 'apikey': pub_key, 'hash': hash_params(), 
          'limit':30}

#Get and put in DataFrames
info = requests.get(urlMarvel,
                   params=params)
info = info.json()
info_df = pd.DataFrame(info)
results_list = info_df['data']['results']
results_df = pd.DataFrame(results_list)

id_list = []
events_list = []
series_list = []
comics_list = []

for dicts in results_list:
    #Add to empty lists the events/series/comics available
    id_list += [dicts['id']]
    events_list += [dicts['events']['available']]
    series_list += [dicts['series']['available']]
    comics_list += [dicts['comics']['available']]

#Add columns to results_df with required information (only price missing)
results_df['Character ID'] = id_list
results_df['Total Available Events'] = events_list
results_df['Total Available Series'] = series_list
results_df['Total Available Comics'] = comics_list

#Get Url links to access comic 'folder'
links_list = []

for dicts in results_list:  
    #Store Url for each comic in links_list to make it possible to access it  
    links_list.append(dicts['comics']['collectionURI'])

#Create comic_results_list and highest_price_per_comic_list to store info after
comic_results_list = []
highest_price_per_comic_list = []

for link in links_list:
    #Get data each comic and store its info in comic_results_list
    comic_info = requests.get(link,
                       params=params)
    comic_info = comic_info.json() 
    comic_results_list.append(comic_info)
#Create all_prices_per_comic_list to use it in the next loop
all_prices_per_comic_list = []

for dicts in comic_results_list:
    #Store all prices in all_prices_per_comic_list
    path = dicts['data']['results']
    for dicts_2 in path:
        path_2 = dicts_2['prices']
        for dicts_3 in path_2:
                all_prices_per_comic_list.append(dicts_3['price'])  
                
    #Append highest value in highest_price_per_comic_list
    highest_price_per_comic_list.append(max(all_prices_per_comic_list,
                                            default=0))
    all_prices_per_comic_list = []

#Add a column to results_df with the information about the Price
results_df['Price of the Most Expensive Comic'] = highest_price_per_comic_list
 
results_df = results_df.rename(columns={'name':'Character Name'})

#Select only needed columns 
df = results_df[['Character ID',
                          'Character Name',
                          'Total Available Events',
                          'Total Available Series',
                          'Total Available Comics',
                          'Price of the Most Expensive Comic']]

df = df.replace(0,None)
df.to_csv('data.csv')
