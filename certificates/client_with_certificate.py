import socket
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.hazmat.primitives.hashes import SHA256
import base64
import json
from pathlib import Path
import subprocess

#Info of the server
SERVER_ID = "server_very_sercure"
HOST = "127.0.0.1" 
PORT = 65432  


def check_certificate(certif_to_check) :

    server_id_to_check = certif_to_check["Server name"]

    #Save the certificate received by the serverr in the client database
    certif_to_check_path = "{}_to_check.json".format(server_id_to_check)
    with open(certif_to_check_path, 'w') as g :
        json.dump(certif_to_check, g)


    #Look if the server is in the database of the CA and check the certif
    signature_path = "certificate_data_base/{}_sign.bin".format(server_id_to_check)
    if Path(signature_path).is_file() :

        cmd = "openssl dgst -sha256 -verify CA_public.pem -signature {} {}".format(signature_path, certif_to_check_path)
        result = subprocess.run( cmd.split(),
                            capture_output = True)


        return "OK" in result.stdout.decode('utf-8')

    return False
    


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    #Connect to server
    s.connect((HOST, PORT))
    s.sendall(b"Start connection")

    #Receive the server's certificate and check it
    certif_from_server = s.recv(1024)
    certif_from_server = json.loads(certif_from_server.decode('utf-8'))

    print(check_certificate(certif_from_server))
    if check_certificate(certif_from_server) :

        public_key = certif_from_server["Public key"].encode('utf-8')
        public_key = b'\n'.join(public_key.splitlines()[1:-1] )
        public_key = base64.b64decode(public_key)
        public_key = load_der_public_key(public_key, default_backend())

        #Generate an symmetric key and encrypt it with the server's public key
        symmetric_key = Fernet.generate_key()
        encrypted_symmetric_key = public_key.encrypt(symmetric_key, 
                                                    padding.OAEP( mgf=padding.MGF1(algorithm=SHA256()),
                                                                algorithm=SHA256(),
                                                                label=None
                                                                )
                                                    ) #encrypted_symmetric_key is already of type bytes

        #Send this public key to the server
        s.sendall(encrypted_symmetric_key)
        
        #Send the file encrypted with the symmetric key
        fernet = Fernet(symmetric_key)
        with open("file_to_send.txt", "rb") as f :
            while True:
                data = f.read(1024)
                encrypted_data = fernet.encrypt(data)
                if not data:
                    break
                s.sendall(encrypted_data)

