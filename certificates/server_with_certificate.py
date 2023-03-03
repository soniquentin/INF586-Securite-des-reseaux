import subprocess
from cryptography.hazmat.primitives import serialization
import socket
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.hashes import SHA256
import json
import sys

SERVER_ID = "server_very_sercure"
HOST = "127.0.0.1" 
PORT = 65432


def generate_public_private_keys() :

    subprocess.run("openssl genrsa -out private.pem 2048", shell=True, check=True)
    subprocess.run("openssl rsa -in private.pem -pubout -out public.pem", shell=True, check=True)


def generate_certificate(public_key_server):

    #Generate the certificate
    certificate_path = "{}.json".format(SERVER_ID)
    certif = {"Server name" : SERVER_ID,
                "Public key" : public_key_server.decode("utf-8")}
        
    with open(certificate_path, 'w') as g :
        json.dump(certif, g)


def generate_certificate() :
    certificate_path = "{}.json".format(SERVER_ID)
    with open(certificate_path, 'r') as g :
        return json.load(g)




def get_public_private_keys() :

    with open('public.pem', 'rb') as f, open('private.pem', 'rb') as g:
        private_object = serialization.load_pem_private_key(g.read(), password=None)
        public_object = serialization.load_pem_public_key(f.read())

        private_pem = private_object.private_bytes(encoding = serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm = serialization.NoEncryption())
        public_pem = public_object.public_bytes(encoding = serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
    

        # Drop the first line and last line
        private_key = b'\n'.join(private_pem.splitlines()[1:-1] )
        public_key = b'\n'.join(public_pem.splitlines()[1:-1] )

        #print("\nPRIVATE KEY GENERATED :\n{}".format(private_key))
        #print("\nPUBLIC KEY GENERATED :\n{}\n".format(public_key))

 
        return public_pem, private_pem, public_object, private_object

def error_args() :

    print("Must contain correct arguments :")
    print("$ python server_with_certificate.py <OPTION>\n")
    print("\n <OPTION> :")
    print("-gen_keys    generates public and private keys of the server and its certificate")
    print("-run   run the server")
    exit()


if __name__ == "__main__" :

    if len(sys.argv) < 2 :
        error_args()
    
    mode = sys.argv[1]

    if mode == "-gen_keys" :
        generate_public_private_keys()
        
        public_pem, private_pem, public_object, private_object = get_public_private_keys()
        my_certif = generate_certificate(public_pem)

    elif mode == "-run" :
        #get the bytes from the .pem files and generate its certificate
        public_pem, private_pem, public_object, private_object = get_public_private_keys()
        my_certif = generate_certificate()


        #wait for client to connect
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()

            #once a client is connected :
            step = 0
            with open("file_received.txt", "wb") as g :
                while True :
                    data = conn.recv(1024)

                    if not data:
                        break

                    #Send its certificate
                    if step == 0 :
                        conn.sendall(json.dumps(my_certif).encode('utf-8'))
                        step += 1

                    #Receive the encrypted symetric key and decrypt it
                    elif step == 1 :
                        symmetric_key = private_object.decrypt(data, padding.OAEP(mgf=padding.MGF1(algorithm=SHA256()), algorithm=SHA256(), label=None))
                        f = Fernet(symmetric_key)
                        step += 1
                    
                    #Write new file after decrypt
                    elif step == 2 :
                        decrypted_data = f.decrypt(data)
                        g.write(decrypted_data)





