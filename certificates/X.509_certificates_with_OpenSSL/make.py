import subprocess
import sys
import os

def gen_certif(nb_mates = 2):

    print("\n"*30 + "="*10 +" SELF-SIGNED CRT FOR ROOT" + "="*10)
    subprocess.run("openssl req -config cert.conf -new -sha256 -newkey rsa:2048 -nodes -keyout private_myroot.key -x509 -days 3650 -out cert_myroot.crt", shell=True, check=True)

    for i in range(1, nb_mates + 1) :

        subprocess.run("openssl genrsa -out private_mate_{}.key 2048".format(i), shell=True, check=True)
        print("\n"*30 + "="*10 +" CSR FOR MATE {}".format(i) + "="*10)
        subprocess.run("openssl req -new -key private_mate_{}.key -out cert_mate_{}.csr -subj '/C=FR/ST=Ile-de-France/L=Paris/O=mate{}/CN=mate{}.site'".format(i,i,i,i), shell=True, check=True)   
        subprocess.run("openssl x509 -req -days 365 -in cert_mate_{}.csr -CA cert_myroot.crt -CAkey private_myroot.key -set_serial 01 -out cert_mate_{}.crt".format(i,i), shell=True, check=True)

        subprocess.run("mv private_mate_{}.key mate{}_res/".format(i,i), shell=True, check=True)
        subprocess.run("mv cert_mate_{}.csr mate{}_res/".format(i,i), shell=True, check=True)
        subprocess.run("mv cert_mate_{}.crt mate{}_res/".format(i,i), shell=True, check=True)
        subprocess.run("cp cert_myroot.crt mate{}_res/".format(i), shell=True, check=True)

    subprocess.run("mv cert_myroot.crt root_res/", shell=True, check=True)
    subprocess.run("mv private_myroot.key root_res/", shell=True, check=True)

def clean():
    subprocess.run("find {} -name '*.key' -type f -delete".format(os.getcwd()), shell=True, check=True)
    subprocess.run("find {} -name '*.crt' -type f -delete".format(os.getcwd()), shell=True, check=True)
    subprocess.run("find {} -name '*.pem' -type f -delete".format(os.getcwd()), shell=True, check=True)
    subprocess.run("find {} -name '*.csr' -type f -delete".format(os.getcwd()), shell=True, check=True)


def error_args() :

    print("Must contain correct arguments :")
    print("$ python make.py : generate the certificats\n")
    print("$ python make.py clean : clean all the certificats in the directory\n")
    exit()


if __name__ == "__main__" :

    try :
        if len(sys.argv) < 2 :
            gen_certif(nb_mates = 2)
        elif sys.argv[1] == "clean" :
            clean()
        else :
            error_args()
    except Exception as e: 
        error_args()