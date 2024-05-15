# SSH Postgres Installer

This script automates the installation and configuration of PostgreSQL on a remote server via SSH.

## Usage

To use this script, execute the following command:

```bash
python install_postgres.py <host>
```

Replace <host> with the hostname or IP address of the target server.

## Requirements

    Python 3.x
    paramiko library (`pip install paramiko`)

## Implementation Details

    - The script provides two ways to connect to the provided host - via an SSH key, or via username/password if the former attempt is unsuccesfull.
    - `sudo` support:
        - You **cannot** simply use `sudo su - username` in an `exec_command` before the command that needs root access, because each call to `exec_command` runs in its own subshell, as such the changes will not propagate back to the main session.
        - I tried to overcome this issue by writing a simple function-wrapper around `exec_command`, which (along side proper exceptions handling) checks if the command requires sudo perms, and if it does, handles admin password input if needed.
    - Script is designed to work on Debian-based distros and on the latest postgresql version (usage of `apt` and the hardcoded path to the .conf file).
        - It is possible to adapt the solution to check both for an existing package manager by checking the distro first (debian/SuSE/redhat/gentoo/alpine/arch/..) in the folder `/etc/os-release

## Author

Tkachenko Nikita, Moscow, Higher School of Economics: 3-rd year, Applied Mathematics, GPA: 7.3
My CV: [link](https://drive.google.com/file/d/1-f2QIuVbLOe0MWIgp7u80G45PKlaL0cL/view?usp=sharing)