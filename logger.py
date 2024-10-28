import datetime

class Logger:

    def __init__(self):

        self.software = "Doc2Talk"
        self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.version = "v1.0"

        self.file_log = True


    def send_log(self, message, client_ip, client_hostname, r_code) :

        log = "[" + self.software + " " + self.version + "] - " + self.date + " - " + message + " | From : " + client_ip + " - Hostname : " + client_hostname + " | Code " + str(r_code)

        if self.file_log : 

            self.write_log(log, r_code)
        
        print(log)


    def write_log(self, log, code) : 

        logs_file = open("logs/logs_code" + str(code) + ".txt", "a")
        logs_file.write(log + "\n")
        logs_file.close()
    
