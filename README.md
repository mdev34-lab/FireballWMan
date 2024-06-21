# Fireball

## Overview
**Fireball** is a Python script designed to facilitate bulk firewall rule management for executable files within a specified directory. The script provides functionalities to allow, block, or clear firewall rules for `.exe` files, offering options for inbound and outbound rule settings. Fireball is especially useful for administrators who need to automate firewall rule configurations in a Windows environment.

## Features
- **Allow**: Permit all firewall connections for found `.exe` files.
- **Block**: Deny all firewall connections for found `.exe` files.
- **Clear**: Remove all firewall rules previously established by Fireball for the found `.exe` files.
- **Clear Before Operation**: Optionally clear existing rules before performing the selected operation.
- **Verbose Mode**: Display detailed warnings and errors during operation.
- **Custom Folder Path**: Specify a folder to search for `.exe` files; defaults to the current directory.
- **Inbound and Outbound Rules**: Set firewall rule direction to inbound or outbound (default).

## Requirements
- Python 3.x
- `colorama` library (for colored console output)
- Administrator privileges

### Options
- `allow`: Allow all firewall connections for the found `.exe` files.
- `block`: Block all firewall connections for the found `.exe` files.
- `clear`: Remove all firewall rules previously established by Fireball.
- `--clear-before-operation` or `-cbo`: Clear existing rules before performing the operation.
- `--inbound`: Set the firewall rule direction to inbound.
- `--outbound`: Set the firewall rule direction to outbound (default).
- `--verbose`: Show all warnings and errors available during operation.
- `--folder <path>`: Specify a folder to perform the operation on; defaults to the current directory.

## Implementation Details
The script performs the following steps:
1. **Admin Check**: Verifies if the script is running with administrator privileges.
2. **Argument Parsing**: Parses command line arguments to determine the action, settings, mode, and path.
3. **File Search**: Searches for `.exe` files in the specified or current directory.
4. **Rule Management**: Based on the selected action, it allows, blocks, or clears firewall rules for each found `.exe` file using PowerShell commands.
5. **Multi-threading**: Utilizes threading to handle multiple `.exe` files simultaneously for faster execution.
