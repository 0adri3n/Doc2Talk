import datetime

class Logger:

    def __init__(self, filename="logs", write_file=True):

        self.software = "Doc2Talk"
        self.version = "v1.0"
        self.filename = filename

        self.file_log = write_file


    def send_log(self, message, client_ip, client_hostname, r_code, answer) :

        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log = "[" + self.software + " " + self.version + "] - " + date + " - " + message + " | From : " + client_ip + " - Hostname : " + client_hostname + " | Answer : " + answer

        if self.file_log : 

            self.write_log(log)
        
        print(log)


    def write_log(self, log) : 

        logs_file = open("logs/" + self.filename + ".txt", "a")
        logs_file.write(log + "\n")
        logs_file.close()
    
