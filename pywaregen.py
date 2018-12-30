import os
import sys
try:
    import hello  # Personal module
except ModuleNotFoundError:
    pass

EXTENSION = ".cfg"


# Get 'y', 'n', 'yes' or 'no' from the user
# Return y or n
def yes_no(default=""):
    try:
        default = default[0].lower()
    except IndexError:
        pass
    ret = ""
    while ret != "y" and ret != "n":
        if default == "y":
            ret = input(" [Y/n] : ")
        elif default == "n":
            ret = input(" [y/N] : ")
        else:
            ret = input(" [y/n] : ")
        ret = ret.lower()
        if ret == "":
            ret = default
        else:
            ret = ret[0]
    return ret


# Get the filename from the user.
# Return the filename as a string with EXTENSION extension
def get_filename():
    global EXTENSION
    name = ""
    pyfile_exist = False
    file_exist = True
    while not pyfile_exist or file_exist or name == "":
        try:
            name = input("Enter the file name without extension. It must be the same as the python file : ")

            if name == "":
                print("\"\" is not acceptable")
            else:
                # Checks the existence of the corresponding python file
                if os.path.exists(name + ".py"):
                    pyfile_exist = True
                else:
                    print("Warning : The corresponding python file was not found.\nDo you want to continue?", end="")
                    choice = yes_no("n")
                    if choice == "y":
                        pyfile_exist = True
                    else:
                        pyfile_exist = False

                # Checks if the file already exists
                if not os.path.exists(name + EXTENSION):
                    file_exist = False
                else:
                    print("Warning : {} already exist.\nDo you want to continue?".format(name + EXTENSION), end="")
                    choice = yes_no("n")
                    if choice == "y":
                        if os.path.isfile(name + EXTENSION):
                            file_exist = False
                        else:
                            print("{} is not a file.".format(name + EXTENSION))
                            file_exist = True
                    else:
                        file_exist = True
        except (KeyboardInterrupt, EOFError):
            print("Ctrl^C or Ctrl^D : Exit software.")
            sys.exit(1)

    return name + EXTENSION


# Select mode to open file. Get it from the user if the file exist
# Return the mode as a string
def get_mode(filename):
    if os.path.exists(filename):
        print("{} already exists. Do you want to add new lines or overwrite the current file?")
        choice = ""
        while choice != "1" and choice != "2":
            print(" 1. Append\n"
                  " 2. Overwrite")
            try:
                choice = input("$>")
            except (KeyboardInterrupt, EOFError):
                choice = ""
        if choice == "1":
            mode = "at"
        else:
            mode = "wt"
    else:
        mode = "wt"
    return mode


# Get the name of the server
# Return the name as string
def get_servername():
    return input("Server name : ")


# Get the ip or domain name of the server
# return the host as string
def get_host():
    return input("Host : ")


# Get the connection port for the server from the user
# Return the part as a string
def get_port():
    port = ""
    port_ok = False
    while not port_ok:
        port = input("Port [4444] : ")
        if port == "":
            # Default value
            port = "4444"

        # Check if the port is acceptable
        if port.isdigit():
            if 1 <= int(port) <= 65535:
                port_ok = True
            else:
                print("he port must be between 1 and 65535 included.")
                port_ok = False
        else:
            print("You must enter a positive number.")
            port_ok = False

    return port


# Get the delay between two attempts to connect to the server, in seconds
# Return the delay as a string
def get_retry_interval():
    retry_interval = ""
    retry_interval_ok = False
    while not retry_interval_ok:
        retry_interval = input("Delay between two attempts to connect to the server, in seconds [3600] : ")
        if retry_interval == "":
            # Default value
            retry_interval = "3600"

        # Check if the delay is acceptable
        if retry_interval.isdigit():
            if int(retry_interval) >= 0:
                retry_interval_ok = True
            else:
                print("The delay must be positive.")
                retry_interval_ok = False
        else:
            print("The delay must be a positive number.")
            retry_interval_ok = False

    return retry_interval


def main():
    try:
        hello.hello()
    except NameError:
        print("*----------*\n"
              "|  PyWare  |\n"
              "*==========*\n")

    filename = get_filename()
    filemode = get_mode(filename)
    try:
        file = open(filename, filemode)

        # Write default value if the file is new or overwrite.
        if filemode == "wt":
            file.write(";; CONFIG FILE FOR THE TARGET\n"
                       ";; FILE NAME WILL BE THE SAME AS THE MALWARE WITH .cfg EXTENSION\n\n"
                       ";; DEFAULT VALUES USED IF NOT OTHER PARAMETERS ARE SET OR UNUSABLE\n"
                       "[DEFAULT]\nHost = localhost\nPort = 4444\nRetryInterval = 3600\n\n"
                       ";; PERSONAL SERVER LISTE\n\n")

        # Add new sections
        new_section = "y"
        while new_section == "y":
            try:
                # Get information from the user.
                server_name = get_servername()
                if server_name != "":
                    host = get_host()
                    port = get_port()
                    retry_interval = get_retry_interval()

                    # Write information in the file
                    file.write("\n[{}]\nHost = {}\nPort = {}\nRetryInterval = {}\n".format(
                        server_name, host, port, retry_interval))
            except (KeyboardInterrupt, EOFError):
                print("Ctrl^C or Ctrl^D : Section cancelled.")

            # Add another section ?
            try:
                print("Add another section ?", end="")
                new_section = yes_no("y")
            except (KeyboardInterrupt, EOFError):
                print("Ctrl^C or Ctrl^D : Write file finish")

        file.close()
        if os.name == "nt":
            file_location = os.getcwd() + "\\" + filename
        else:
            file_location = os.getcwd() + "/" + filename
        print("Write the completed configuration file :\n"
              "  {}".format(file_location))

    # Errors when opening the file
    except PermissionError:
        print("[x] Unable to open or create file. Please, check permissions.")
    except FileNotFoundError:
        print("[x] Unable to find the repertory.")


if __name__ == "__main__":
    main()
