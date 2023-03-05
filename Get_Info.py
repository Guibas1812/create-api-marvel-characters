from Permission import Permission
import pandas as pd
import requests

class Get_info:
    
    urlMarvel = 'http://gateway.marvel.com/v1/public/characters/' #Marvel API's url

    def __init__ (self, id):
        """Accessing Marvel API to get information about desired character using its id.
        Information retrieved: 1. name, 2. total number of events, 3. total number of series 
        available, 4. total number of comics and 5. price of the most expensive comic that 
        the charatcer was featured in"""
        
        self.id = id #id needs to be given
        
        link = self.urlMarvel + str(self.id) #url for specific Marvel Character
        response = requests.get(link, params = Permission().parameters()).json()  
        response_price = requests.get(link + '/comics', params = Permission().parameters()).json() #Request for price feature 

        #Get relevant features related to the character (name, events,series,comics & highest price)
        self.name = response['data']['results'][0]['name'] 
        self.events = response['data']['results'][0]['events']['available'] 
        self.series = response['data']['results'][0]['series']['available'] 
        self.comics = response['data']['results'][0]['comics']['available'] 

        #To get the highest price per comic
        all_prices_per_comic_list = []    
        for dicts in response_price['data']['results']:
            for prices in dicts['prices']:
                all_prices_per_comic_list.append(prices['price'])
        #Highest price info
        self.price = max(all_prices_per_comic_list, default=0)

    def filtered_info(self):
        """Return dataframe with all the information related to desired character"""
        entry = pd.DataFrame({
                        'Character Name' : [self.name], 
                        'Character ID' : [self.id],
                        'Total Available Events' : [self.events],  
                        'Total Available Series' : [self.series],  
                        'Total Available Comics' :  [self.comics],  
                        'Price of the Most Expensive Comic' : [self.price]}) 
        return entry