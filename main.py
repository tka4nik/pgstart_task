import sys

import paramiko
import psycopg2


def connect(host: str):
    client = paramiko.SSHClient()
    try:
        # k = paramiko.RSAKey.from_private_key_file("id_rsa")
        # print(k)
        k = None
        if k is not None:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=host, port=22)
            return client
        else:
            print("SSH key was not found, input credentials:")
            username = input("Username: ")
            password = input("Password: ")
            client.connect(hostname=host, username=username, password=password)
            return client
    except Exception as e:
        print("Error:", e)
        return None


def execute_command_ssh(ssh_client, command, sudo=False):
    """
    Execute a command on a remote server using SSH.

    Args:
        ssh_client (paramiko.SSHClient): SSH client object connected to the remote server.
        command (str): Command to execute.
        sudo (bool, optional): Whether to execute the command with sudo. Defaults to False.

    Returns:
        tuple: A tuple containing the command exit status, the command output, and any error message.
    """
    try:
        if sudo:
            stdin, stdout, stderr = connection.exec_command("sudo -S %s" % command, get_pty=True)
            if stdout.channel.closed is False:
                stdin.write('%s\n' % input("Admin password: "))
                stdin.flush()
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
        else:
            stdin, stdout, stderr = ssh_client.exec_command(command, get_pty=True)

            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

        return exit_status, output, error
    except paramiko.SSHException as e:
        return None, None, f"SSHException: {e}"
    except Exception as e:
        return None, None, f"Error: {e}"


def install_and_configure_postgresql(client: paramiko.SSHClient):
    execute_command_ssh(client, "apt-get update", True)
    execute_command_ssh(client, "apt-get -y install postgresql postgresql-contrib", True)
    execute_command_ssh(client, "sed -i 's/#listen_addresses = 'localhost'/listen_addresses = '*'/' /etc/postgresql/13/main/postgresql.conf",True)  # Assuming ubuntu, that's the default location of the config
    execute_command_ssh(client, "echo 'host all all 0.0.0.0/0 md5' >> /etc/postgresql/13/main/pg_hba.conf", True)
    execute_command_ssh(client, "systemctl restart postgresql", True)


def check_installation(client: paramiko.SSHClient):
    try:
        stdin, stdout, stderr = execute_command_ssh(client, "psql -c 'SELECT 1;'")
        print(stdout)
    except Exception as e:
        return None, None, f"Error: {e}"


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python install_postgres.py <host>")
        sys.exit(1)

    host = sys.argv[1]
    connection = connect(host)
    if connection is None:
        print("Invalid credentials.")
        sys.exit(2)

    install_and_configure_postgresql(connection)
    if check_installation(connection):
        sys.exit(0)
    sys.exit(1)