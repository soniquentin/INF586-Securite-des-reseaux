import subprocess
import sys
from cryptography.hazmat.primitives import serialization
import socket
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.hashes import SHA256
import json


HOST = "127.0.0.1"
PORT = 65431

def generate_public_private_keys() :

    subprocess.run("openssl genrsa -out CA_private.pem 2048", shell=True, check=True)
    subprocess.run("openssl rsa -in CA_private.pem -pubout -out CA_public.pem", shell=True, check=True)


def sign_certificate(id_server):

    #Import the certificate
    signature_path = "certificate_data_base/{}_sign.bin".format(id_server)
    certificate_path = "{}.json".format(id_server)
        
    with open(certificate_path, 'r') as g :
        certif = json.load(g)

        #Sign the certificate with CA's private key and save it
        subprocess.run("openssl dgst -sha256 -sign CA_private.pem -out {} {}".format(signature_path, certificate_path) , shell=True, check=True)




def error_args() :

    print("Must contain correct arguments :")
    print("$ python certication_authority.py <OPTION>\n")
    print("\n <OPTION> :")
    print("-gen_keys    generates public and private keys of the certification authority")
    print("-gen_certif <SERVER ID> <SERVER'S PUBLIC KEY FILE>   create a certificate for server")
    exit()



if __name__ == "__main__" :

    if len(sys.argv) < 2 :
        error_args()
    
    mode = sys.argv[1]

    if mode == "-gen_keys" :
        generate_public_private_keys()
        print("Public and private keys generated ! (CA_public.pem & CA_private.pem)")
    
    elif mode == "-gen_certif" :
        if len(sys.argv) < 3 :
            error_args()
        else :
            server_id = sys.argv[2]

            #Sign the certificate of the server
            sign_certificate(server_id)         
    
    



                    

                    