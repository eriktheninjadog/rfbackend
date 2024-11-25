import subprocess
import paramiko

import os

def run_command_on_remote( command, remote_dir):
    # create an SSH client with the given credentials
    try:
        ssh =  paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('localhost', 9001, username=os.getenv('HOMEUSERNAME'), password=os.getenv('HOMEPASSWORD'))
        full_command = f"cd {remote_dir} && nohup {command} > /dev/null 2>&1 &"
        ssh.exec_command(full_command)

        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if output:
            print(f"Output: {output}")
        if error:
            print(f"Error: {error}")

        print("Command sent to remote server.")
    except paramiko.AuthenticationException:
        print("Authentication failed, please verify your credentials.")
    except paramiko.SSHException as ssh_ex:
        print(f"Error connecting to the server: {ssh_ex}")
    except paramiko.BadHostKeyException as bad_host_ex:
        print(f"Unable to verify server's host key: {bad_host_ex}")
    except IOError as io_ex:
        print(f"IOError: {io_ex}")
    finally:
        # Close the SSH client
        ssh.close()

# use the function with specified port
run_command_on_remote( 'touch hithere.txt', '/home/erik')
