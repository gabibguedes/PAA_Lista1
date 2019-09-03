from twitterRequests import *
from twitterGraph import *
from shutil import copyfile
import os

def addUser(username):
    source_path = 'data/ids/' + username + '.json'
    target_path = 'data/ale/' + username + '.json'
    copyfile(source, target)

def transferToAle():
    directory = 'data/ids/'
    friends_list = get_list('aleronupe', 'friends')
    direct_list = os.listdir(directory)
    for friend in friends_list:
        username = friend['screen_name']
        for file in direct_list:
            if(username in filename):
                  
        
        

     
    


if __name__ == "__main__":
    createAleFolder()