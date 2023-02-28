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


def my_shell(cmd):
    result = subprocess.run( cmd.split(),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=False,
                            check=True)
    
    return result.stdout.decode().strip()
    


if __name__ == "__main__" :
    
    #Doing the security handshake
    generate_public_private_keys()
    public_key, private_key, public_object, private_object = get_public_private_keys()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()

        step = 0
        with open("file_received.txt", "wb") as g :
            while True :
                data = conn.recv(1024)

                if not data:
                    break

                if step == 0 :
                    conn.sendall(public_key)
                    step += 1

                elif step == 1 :
                    symmetric_key = private_object.decrypt(data, padding.OAEP(mgf=padding.MGF1(algorithm=SHA256()), algorithm=SHA256(), label=None))
                    f = Fernet(symmetric_key)
                    step += 1
                
                elif step == 2 :
                    #Write command in the shell
                    decrypted_data = f.decrypt(data)
                    try :
                        print_data = str.encode( my_shell(decrypted_data) )
                    except Exception as e : #Error in the shell
                        print_data = str.encode( str(e) )

                    encrypted_print_data = f.encrypt(print_data)
                    conn.sendall(encrypted_print_data)
                    






