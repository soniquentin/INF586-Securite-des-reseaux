import socket
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.hazmat.primitives.hashes import SHA256
import base64

#Info of the server
HOST = "127.0.0.1"
PORT = 65432  



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    #Doing the security handshake with the client
    s.connect((HOST, PORT))
    s.sendall(b"Start connection")

    public_key_bytes = s.recv(1024)
    derdata = base64.b64decode(public_key_bytes)
    public_key = load_der_public_key(derdata, default_backend()) #Convert into a <cryptography.hazmat.backends.openssl.rsa._RSAPublicKey object>

    symmetric_key = Fernet.generate_key()

    encrypted_symmetric_key = public_key.encrypt(symmetric_key, 
                                                padding.OAEP( mgf=padding.MGF1(algorithm=SHA256()),
                                                            algorithm=SHA256(),
                                                            label=None
                                                            )
                                                ) #encrypted_symmetric_key is already of type bytes
    s.sendall(encrypted_symmetric_key)
    
    #Ask for shell command
    print("======= Initializing Shell ======= ")
    data = ""
    fernet = Fernet(symmetric_key)
    while True :
        data = input("\n>> ")
        if data == "quit()" :
            break
        data = str.encode(data)
        encrypted_data = fernet.encrypt(data)

        s.sendall(encrypted_data)

        encrypted_print_data = s.recv(1024)

        if encrypted_print_data:  
            print_data = fernet.decrypt(encrypted_print_data)
            print(print_data.decode())

        

