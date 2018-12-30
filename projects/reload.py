# Server
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

# Victim
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
