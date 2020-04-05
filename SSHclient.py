# Based on https://hackersandslackers.com/ssh-scp-in-python-with-paramiko/
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException
from scp import SCPClient, SCPException
from io import StringIO
from flask import flash

class Client:
    def __init__(self, request):
        self.targetHost = request.form.get('targetHost', '')
        self.targetHostUser = request.form.get('targetHostUser', '')
        self.targetHostPassword = request.form.get('targetHostPassword', '')
        self.targetHostSSHKey = request.form.get('targetHostSSHKey', '')
        self.targetHostPassphrase = request.form.get('targetHostPassphrase', '')
        self.shouldUseExistingSSHKey = request.form.get('shouldUseExistingSSHKey', False)
        self.client = None

    def get_ssh_key(self):
        """Get our SSh key."""

        if self.shouldUseExistingSSHKey == True or self.targetHostSSHKey == '':
            self.pkey = None
        else:
            keyFile = open(self.targetHostSSHKey, 'r')
            if self.targetHostPassphrase != '':
                self.pkey = RSAKey.from_private_key(keyFile, password=self.targetHostPassphrase)
            else:
                self.pkey = RSAKey.from_private_key(keyFile)
            keyFile.close()

    def connect(self):
        """Connect to remote."""
        if self.client is None:
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            if self.shouldUseExistingSSHKey == True:
                client.load_system_host_keys()
            if self.pkey != None:
                client.connect(self.targetHost,
                               username=self.targetHostUser,
                               pkey=self.pkey)
            else:
                client.connect(self.targetHost,
                               username=self.targetHostUser,
                               password=self.targetHostPassword)      
            return client
        return self.client

    def upload(self, file, remote_directory):
        """Upload a single file to a remote directory"""
        self.client = self.connect()
        scp = SCPClient(self.client.get_transport())
        try:
            scp.put(file,
                    recursive=True,
                    remote_path=remote_directory)
        except SCPException:
            raise SCPException.message
        finally:
            scp.close()

    def execute(self, cmd):
        """Executes a single unix command."""
        self.client = self.connect()
        stdin, stdout, stderr = self.client.exec_command(cmd)
        return [stdout.readlines(), stderr.readlines()]

    def disconnect(self):
        """Close ssh connection."""
        self.client.close()
        self.client = None

    def test_connection(self):
        try:
            self.get_ssh_key()
            self.client = self.connect()
            self.disconnect()
        except AuthenticationException as e:
            flash('Error: Test connection failed, job not scheduled: Unable to authenticate')
            return False
        except Exception as e:
            flash('Error: Test connection failed, job not scheduled due to unexpected error ' + str(e))
            return False
