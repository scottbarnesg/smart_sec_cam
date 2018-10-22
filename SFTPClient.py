import os
import paramiko
import scp
from auth.auth import Auth

class Client():
    def __init__(self, host="media-server", port=22):
        self.host = host
        self.port = port
        self.auth = Auth()
        self.ssh = paramiko.SSHClient()
        # self.ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.WarningPolicy())

    def send(self, localpath, remotepath):
        self.ssh.connect(self.host, self.port, self.auth.username, self.auth.password)
        sftp = self.ssh.open_sftp()
        try:
            sftp.chdir(remotepath)
        except IOError:
            sftp.mkdir(remotepath)
        sftp.put(localpath, remotepath)
        sftp.close()
        self.ssh.close()

if __name__ == '__main__':
    client = Client()
    client.send("bin/videos7/recording0.avi", "videos/recording0.avi")
