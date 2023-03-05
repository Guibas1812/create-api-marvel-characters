import pandas as pd
import datetime
from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from Get_Info import Get_info

#Create API 
app = Flask(__name__)
api = Api(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app) #setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret-key"  

class SignUp(Resource):

    def hash_password(self,password):
        """Returns user password encoded"""
        return generate_password_hash(password).decode('utf8')

    def post(self):
        """Allows account creation and saves it in users.csv"""
        parser = reqparse.RequestParser()
        #required arguments
        parser.add_argument('email', type=str, location = 'args',help='Missing argument email', required=True)
        parser.add_argument('password', type=str, location = 'args', help='Missing argument password', required=True)
        args = parser.parse_args() #parse arguments to dictionary

        data = pd.read_csv('users.csv') #csv with accounts
        
        if args['email'] in list(data['email']): #if account already exists
            return {'status': 409, 'response': f"{args['email']} already exists."}, 409
        else:
            #create new dataframe containing new account
            entry = pd.DataFrame({
                'email': [args['email']],
                'password': [self.hash_password(args['password'])]
            })
            
            #add entry to csv
            data = data.append(entry, ignore_index=True)
            data.to_csv('users.csv', index=False) 
            return {'status': 200, 'response': 'Successfully signed up'}, 200 

class LogIn(Resource):

    def get(self):
        """Allows user to log in by verifying if user info is contained in users.csv"""
        parser = reqparse.RequestParser()
        #required arguments
        parser.add_argument('email', type=str, help='Missing argument email',location = 'args', required=True)
        parser.add_argument('password', type=str, help='Missing argument password',location = 'args', required=True)
        args = parser.parse_args()  #parse arguments to dictionary
        data = pd.read_csv('users.csv')
        
        if args['email'] not in list(data['email']): #email not registred in users.csv
            return {'status': 401, 'response': f"Invalid email"}, 401
        else: 
            #look for password hash in database
            password = data.loc[data['email']==args['email'], 'password'][0]
            
            if check_password_hash(password, args['password']):
                expires = datetime.timedelta(hours=1)
                #give access token with 1 hour duration
                access_token = create_access_token(identity=str(data.loc[data['email']==args['email']].index[0]), expires_delta=expires)
                return {'status': 200, 'response': 'Successfully logged in', 'token': access_token}, 200
            else:
                return {'status': 401, 'response': f"Invalid password."}, 401
            

class Characters(Resource):
    def get(self):
        """Returns desired information based on inputed arguments"""
        parser = reqparse.RequestParser()
        #optional arguments 
        parser.add_argument('Character ID',type = int, action='append', help="Missing argument Character ID",location = 'args', required=False) 
        parser.add_argument('Character Name',type = str, action='append', help="Missing argument Character Name",location = 'args', required=False) 
        args = parser.parse_args() #parse arguments to dictionary

        df = pd.read_csv('data.csv') #read local CSV containing info about 30 Marvel characters - gathered by accessing Marvel API

        if args['Character ID'] is not None: #when character ID is provided
            if all(item in list(df['Character ID']) for item in args['Character ID']): #if ID is in those 30 records that we already got
                entry = df.loc[df['Character ID'].isin(args['Character ID'])] 
                entry = entry.to_dict(orient='records') 
                return {'status': 200, 'response': entry}, 200 #return info related with that id 
            else:
                return {'status': 404, 'response': "Incorrect value for Character ID."}, 404   
                     
        elif args['Character Name'] is not None: #when character name is provided
            if all(item in list(df['Character Name']) for item in args['Character Name']): #If name is in those 30 records that we already got
                entry = df.loc[df['Character Name'].isin(args['Character Name'])] 
                entry = entry.to_dict(orient='records') 
                return {'status': 200, 'response': entry}, 200 #return info related with that name 
            else:
                return {'status': 404, 'response': "Incorrect value for Character Name."}, 404          
            
        else: #when no argument is provided
            df_dict = df.to_dict(orient='records') 
            return {'status': 200, 'response': df_dict}, 200 #return all 30 records that we already got
    
    #access token required
    @jwt_required()
    def post(self):
        """Adds a new character to the existing DataFrame.

        Option 1 -> provide only character id and API fills the remaining information 
        by extracting it from Marvel's API and appending to the DataFrame.

        Option 2-> provide all necessary characteristics."""

        parser = reqparse.RequestParser()
        #arguments that can be given (id is mandatory) 
        parser.add_argument('Character ID', type=int, help='Missing argument Character ID',location = 'args', required=True) 
        parser.add_argument('Character Name', type=str, help='Missing argument Character Name',location = 'args', required=False) 
        parser.add_argument('Total Available Events', type=int, help='Missing argument Total Available Events',location = 'args', required=False)
        parser.add_argument('Total Available Series', type=int, help='Missing argument Total Available Series', location = 'args',required=False)
        parser.add_argument('Total Available Comics', type=int, help='Missing argument Total Available Comics', location = 'args',required=False)
        parser.add_argument('Price of the Most Expensive Comic', type=float, help='Missing argument Price of the Most Expensive Comic',location = 'args', required=False)
        args = parser.parse_args()  #Parse arguments to dictionary

        df = pd.read_csv('data.csv') #Read local CSV containing info about 30 Marvel characters - gathered accessing Marvel API

        if args['Character ID'] in list(df['Character ID']):
            return {'status': 409, 'response': f"'{args['Character ID']}' already exists."}, 409
        
        elif (args['Character Name'] is not None) and (args['Total Available Events'] is not None) and (args['Total Available Series'] is not None) and (args['Total Available Comics'] is not None) and (args['Price of the Most Expensive Comic'] is not None):
            entry = pd.DataFrame({
                'Character ID': [args['Character ID']],
                'Character Name': [args['Character Name']],
                'Total Available Events': [args['Total Available Events']],
                'Total Available Series': [args['Total Available Series']],
                'Total Available Comics': [args['Total Available Comics']],
                'Price of the Most Expensive Comic': [args['Price of the Most Expensive Comic']]}) #create new dataframe containing new values

            df = df.append(entry, ignore_index=True) 
            df.to_csv('data.csv', index=False) #add entry to csv  
            entry = entry.to_dict(orient='records') 
            return {'status': 200, 'response': entry}, 200 
            
        elif args['Character ID'] is not None: 
            entry = Get_info(args['Character ID']).filtered_info() #extract remaining info by accessing marvel api    
            df = df.append(entry, ignore_index=True) 
            df.to_csv('data.csv', index=False)  #add entry to CSV
            entry = entry.to_dict(orient='records') 
            return {'status': 200, 'response': entry}, 200  

    #access token required
    @jwt_required()    
    def delete(self):
        """Deletes a character by providing either the Character ID or the Character Name"""
        parser = reqparse.RequestParser() 
        #arguments given
        parser.add_argument('Character ID', type=int,location = 'args', help='Missing argument Character ID', required=False)  
        parser.add_argument('Character Name', type=str, location = 'args',help='Missing argument Character Name', required=False)  
        args = parser.parse_args()  #parse arguments to dictionary
        df = pd.read_csv('data.csv') 

        if args['Character ID'] is not None:
            if args['Character ID'] in list(df['Character ID']):
                df = df[df['Character ID'] != args['Character ID']] #remove data entry matching given character id
                df.to_csv('data.csv', index=False) 
                df = df.to_dict(orient='records') 
                return {'status': 200, 'response': f"Character {args['Character ID']} succesfully deleted"}, 200 
            else:
                return {'status': 404, 'response': f"Incorrect value {args['Character ID']} for Character ID."}, 404 
            
        elif args['Character Name'] is not None:
            if args['Character Name'] in list(df['Character Name']):
                df = df[df['Character Name'] != args['Character Name']] #remove data entry matching given name
                df.to_csv('data.csv', index=False) 
                df = df.to_dict(orient='records') 
                return {'status': 200, 'response': f"Character {args['Character Name']} succesfully deleted"}, 200 
            else:
                return {'status': 404, 'response': f"Incorrect value {args['Character Name']} for Character Name."}, 404
        else:
            return {'status': 404, 'response': f"No Character Name or Character ID provided."},404
         
api.add_resource(Characters, '/characters', endpoint='characters')
api.add_resource(SignUp, '/signup', endpoint='signup')
api.add_resource(LogIn, '/login', endpoint='login')

if __name__ == '__main__':
    app.run(debug=True)     