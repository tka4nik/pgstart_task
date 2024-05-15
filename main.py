import sys

import paramiko


def connect(host: str):
    client = paramiko.SSHClient()
    try:
        key = input("SSH key path:")
        pkey = paramiko.RSAKey.from_private_key_file(key)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, port=22, pkey=pkey)
        return client
    except Exception as e:
        print("RSA file error: ", e)

    try:
        print("SSH key was not found, input credentials:")
        username = input("Username: ")
        password = input("Password: ")
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password)
        return client
    except Exception as e:
        print("Error:", e)
        return None


def execute_command_ssh(client: paramiko.SSHClient, command, sudo=False):
    try:
        if sudo:
            stdin, stdout, stderr = client.exec_command("sudo -S %s" % command, get_pty=True)
            if stdout.channel.closed is False:
                stdin.write('%s\n' % input("Admin password: "))
                stdin.flush()
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
        else:
            stdin, stdout, stderr = client.exec_command(command, get_pty=True)

            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

        return exit_status, output, error
    except paramiko.SSHException as e:
        print(f"SSHException: {e}")
        return None, None, "SSHException: {e}"
    except Exception as e:
        print(f"Error: {e}")
        return None, None, f"Error: {e}"


def install_and_configure_postgresql(client: paramiko.SSHClient):
    execute_command_ssh(client, "apt-get update", True)
    execute_command_ssh(client, "apt-get -y install postgresql postgresql-contrib", True)
    execute_command_ssh(client,
                        "sed -i 's/#listen_addresses = 'localhost'/listen_addresses = '*'/' /etc/postgresql/13/main/postgresql.conf",
                        True)  # Assuming ubuntu, that's the default location of the config; version number is hardcoded
    execute_command_ssh(client, "echo 'host all all 0.0.0.0/0 md5' >> /etc/postgresql/13/main/pg_hba.conf", True)
    execute_command_ssh(client, "systemctl restart postgresql", True)
    print("Installation complete!")


def check_installation(client: paramiko.SSHClient):
    try:
        stdin, stdout, stderr = execute_command_ssh(client, "psql -c 'SELECT 1;'")
        print("Testing installation, running 'SELECT 1;': ", stdout)
        return True
    except Exception as e:
        print("Error:", e)
        return False


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python install_postgres.py <host>")
        sys.exit(1)

    host = sys.argv[1]
    client = connect(host)
    if client is None:
        print("Invalid credentials.")
        sys.exit(2)

    install_and_configure_postgresql(client)
    if check_installation(client):
        print("Success!")
        sys.exit(0)
