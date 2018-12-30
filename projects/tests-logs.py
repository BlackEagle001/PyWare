import time
import logging

log_filename = "hello.log"


class InputOutput:
    def __init__(self, filename: str):
        self.filename = filename
        if filename != "":
            self.flag_log = True
            self.info("INFO : Logging activate")
            logging.basicConfig(filename=self.filename, level=logging.DEBUG)
        else:
            self.flag_log = False
            self.info("INFO : no logging")

    def info(self, string_in: str, mode=""):
        if mode != "":
            mode = mode.upper() + " :"
        time_now = time.localtime()
        time_now_format = "{hour}:{min} {day}/{month}/{year}".format(hour=time_now.tm_hour, min=time_now.tm_min,
                                                                     day=time_now.tm_mday, month=time_now.tm_mday,
                                                                     year=time_now.tm_year)
        string_info = "[ {time} ]  {message}".format(time=time_now_format, message=string_in)
        print(mode, string_info)
        if self.flag_log:
            if mode == "ERROR :":
                logging.error(string_info)
            else:
                logging.info(string_info)


input_output = InputOutput(log_filename)