import subprocess
from cryptography.hazmat.primitives import serialization
import socket
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.hashes import SHA256


HOST = "127.0.0.1"
PORT = 65432


def generate_public_private_keys() :

    subprocess.run("openssl genrsa -out private.pem 2048", shell=True, check=True)
    subprocess.run("openssl rsa -in private.pem -pubout -out public.pem", shell=True, check=True)


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

 
        return public_key, private_key, public_object, private_object


if __name__ == "__main__" :

    #Step 1 : when the server opens, generate a pair of public/private keys
    generate_public_private_keys()

    #Step 2 : get the bytes from the .pem files
    public_key, private_key, public_object, private_object = get_public_private_keys()

    #Step 3 : wait for client to connect
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()

        #Step 4 : once a client is connected :
        step = 0
        with open("file_received.txt", "wb") as g :
            while True :
                data = conn.recv(1024)

                if not data:
                    break

                #print('Received from client:', data)
                
                #Step 5 : Send the public key to the client
                if step == 0 :
                    conn.sendall(public_key)
                    step += 1

                #Step 6 : Receive the encrypted symetric key and decrypt it
                elif step == 1 :
                    symmetric_key = private_object.decrypt(data, padding.OAEP(mgf=padding.MGF1(algorithm=SHA256()), algorithm=SHA256(), label=None))
                    f = Fernet(symmetric_key)
                    step += 1
                
                #Step 7 : Write new file after decrypt
                elif step == 2 :
                    decrypted_data = f.decrypt(data)
                    g.write(decrypted_data)





