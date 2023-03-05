import hashlib
import datetime

class Permission:
    
    pub_key = '' #insert here public key 
    priv_key = '' #insert here private key

    def __init__ (self):
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d%H:%M:%S')

    def hash_params(self):
        """ Marvel API requires server side API calls to include
        md5 hash of timestamp + public key + private key """
        hash_md5 = hashlib.md5()
        hash_md5.update(f'{self.timestamp}{self.priv_key}{self.pub_key}'.encode('utf-8'))
        hashed_params = hash_md5.hexdigest()
        return hashed_params
    
    def parameters(self):
        """Return necessary parameters to get Permission to access Marvel API"""
        params = {'ts': self.timestamp, 'apikey': self.pub_key, 'hash': self.hash_params()}
        return params