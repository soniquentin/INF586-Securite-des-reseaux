import socket
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.hazmat.primitives.hashes import SHA256
import base64

#Info of the server
HOST = "192.168.1.220" 
PORT = 65432  



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    #Connect to server
    s.connect((HOST, PORT))
    s.sendall(b"Start connection")

    #Receive the public key
    public_key_bytes = s.recv(1024)
    derdata = base64.b64decode(public_key_bytes)
    public_key = load_der_public_key(derdata, default_backend()) #Convert into a <cryptography.hazmat.backends.openssl.rsa._RSAPublicKey object>

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

