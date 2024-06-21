import glob
import subprocess
import threading
from colorama import just_fix_windows_console
from sys import argv, exit
from time import perf_counter
import ctypes

# Fix Windows console colors
just_fix_windows_console()

# Ignore PowerShell errors
IGNORE_POWERSHELL_ERROR = True
# Version counter
VERSION: float = 2.0

def check_admin():  # Check if the script is running as admin
    def is_admin():  # Function to check if the script is running as administrator
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    if not is_admin():
        print(f"{Colors.RED}Error: This script must be run as an administrator.{Colors.RESET}")
        exit(1)

class Colors:  # Define escape sequences for colors
    ESC = '\033'
    RED = f'{ESC}[31m'
    GREEN = f'{ESC}[32m'
    ORANGE = f'{ESC}[38;5;208m'
    PURPLE = f'{ESC}[35m'
    ITALIC = f'{ESC}[3m'
    RESET = f'{ESC}[0m'
    YELLOW = f'{ESC}[33m'

class Action:  # Define actions
    class Allow: aname = "Allow"
    class Block: aname = "Block"
    class Clear: aname = "Clear"

class Settings:  # Define settings
    class ClearBeforeOperation: sname = "ClearBeforeOperation"
    class ModeInbound: sname = "ModeInbound"
    class ModeOutbound: sname = "ModeOutbound"

class RuleMethods:  # Define methods to get, remove and add firewall rules
    @staticmethod
    def run_command(command, verbose=False):
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            if (result.returncode == 1) and (verbose == True):
                 print(f"{Colors.YELLOW}Warning ({result.returncode}): Rule not found. Proceeding with normal operation.{Colors.RESET}")
            elif (verbose == True):
                print(f"{Colors.RED}Error ({result.returncode}): Could not perform firewall operation.{Colors.RESET}")
                if not IGNORE_POWERSHELL_ERROR:
                    raise subprocess.CalledProcessError(result.returncode, command)
        return result.stdout

    @staticmethod
    def clear(fileName: str, v: bool):
        def allow_clear_thread(fileName: str, v):
            try:
                RuleMethods.run_command(
                    ["powershell", "-command", f"Get-NetFirewallRule -DisplayName 'Allow {fileName}' -ErrorAction SilentlyContinue | Remove-NetFirewallRule"],
                    verbose=v
                )
            except subprocess.CalledProcessError as e:
                if IGNORE_POWERSHELL_ERROR:
                    pass
                else:
                    raise e

        def block_clear_thread(fileName: str, v):
            try:
                RuleMethods.run_command(
                    ["powershell", "-command", f"Get-NetFirewallRule -DisplayName 'Block {fileName}' -ErrorAction SilentlyContinue | Remove-NetFirewallRule"],
                    verbose=v
                )
            except subprocess.CalledProcessError as e:
                if IGNORE_POWERSHELL_ERROR:
                    pass
                else:
                    raise e

        aclear, bclear = (
            threading.Thread(target=allow_clear_thread, args=(fileName, v)),
            threading.Thread(target=block_clear_thread, args=(fileName, v))
        )
        
        aclear.start()
        bclear.start()
        aclear.join()
        bclear.join()

    @staticmethod
    def allow(filePath: str, ruleName: str, v: bool, mode: str = "Outbound"):
        RuleMethods.run_command(
            ["powershell", "-command", f"New-NetFirewallRule -DisplayName '{ruleName}' -Direction {mode} -Program '{filePath}' -Action Allow"],
            verbose=v
        )

    @staticmethod
    def block(filePath: str, ruleName: str, v: bool, mode: str = "Outbound"):
        RuleMethods.run_command(
            ["powershell", "-command", f"New-NetFirewallRule -DisplayName '{ruleName}' -Direction {mode} -Program '{filePath}' -Action Block"],
            verbose=v
        )

class MiscellaneousText:  # Define miscellaneous text
    HELP_TEXT = f"""
{Colors.ORANGE}Fireball Rules{Colors.RESET} {Colors.GREEN}{VERSION}{Colors.RESET}
Bulk firewall-blocking of executables on a folder? Let Fireball do it for you.
Usage: {Colors.ORANGE}{Colors.ITALIC}fireball{Colors.RESET} {Colors.GREEN}allow{Colors.RESET} | {Colors.RED}block{Colors.RESET} | {Colors.PURPLE}clear{Colors.RESET} [--clear-before-operation] [--inbound | --outbound]

{Colors.GREEN}allow{Colors.RESET}   ==   Allow all firewall connections for the found .exe files
{Colors.RED}block{Colors.RESET}   ==   Block all firewall connections for the found .exe files
{Colors.PURPLE}clear{Colors.RESET}   ==   Remove all firewall rules previously established by {Colors.ORANGE}Fireball{Colors.RESET} for the found .exe files

--clear-before-operation  ==  Clear existing rules before performing the operation
-cbo
--inbound                 ==  Set the firewall rule direction to inbound (default is outbound)
--outbound                ==  Set the firewall rule direction to outbound (default)
--verbose                 ==  Show all warnings and errors available during operation      
--folder <path>           ==  Specify a folder to perform the operation on, default is
                              the current directory.
"""

class NoArgumentsError(Exception): pass

def main():
    start_time = perf_counter()
    check_admin()  # Check if the script is running as admin

    # Check command line arguments and convert them to lowercase
    try:
        Arguments = [arg.lower() for arg in argv]
        ACTION = None
        SETTING = []
        VERBOSE = False
        MODE = "Outbound"
        PATH = "."
        USE_PATH = False

        if "allow" in Arguments: ACTION = Action.Allow
        elif "block" in Arguments: ACTION = Action.Block
        elif "clear" in Arguments: ACTION = Action.Clear
        else: raise NoArgumentsError

        if "--clear-before-operation" in Arguments or "-cbo" in Arguments: SETTING.append(Settings.ClearBeforeOperation)
        if "--verbose" in Arguments: VERBOSE = True
        if "--inbound" in Arguments: MODE = "Inbound"
        if "--outbound" in Arguments: MODE = "Outbound"

        for id, arg in enumerate(argv):  # Use original argv to get the correct path
            if arg == "--folder" and id + 1 < len(argv):
                PATH = argv[id + 1]
                USE_PATH = True

    except NoArgumentsError:
        print(f"{MiscellaneousText.HELP_TEXT}")
        exit()

    # Process .exe files based on the action
    threads = []
    fileFound = False
    search_path = f"{PATH}/**/*.exe" if USE_PATH else "**/*.exe"
    for filePath in glob.glob(search_path, recursive=True):
        fileFound = True
        fileName = filePath.split("\\")[-1]
        ruleName = f"{ACTION.aname} {fileName}"
        print()

        if Settings.ClearBeforeOperation in SETTING:
            print(f"Clearing existing rules for: {Colors.ORANGE}{fileName}{Colors.RESET}")
            RuleMethods.clear(fileName, VERBOSE)

        if ACTION == Action.Clear:
            print(f"Removing existing rules for: {Colors.ORANGE}{fileName}{Colors.RESET}")
            thread = threading.Thread(target=RuleMethods.clear, args=(fileName, VERBOSE))
        elif ACTION == Action.Allow:
            print(f"{Colors.GREEN}Allowing {filePath}{Colors.RESET}...")
            thread = threading.Thread(target=RuleMethods.allow, args=(filePath, ruleName, VERBOSE, MODE))
        elif ACTION == Action.Block:
            print(f"{Colors.RED}Blocking {filePath}{Colors.RESET}...")
            thread = threading.Thread(target=RuleMethods.block, args=(filePath, ruleName, VERBOSE, MODE))
        
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    if not fileFound:
        print(f"{Colors.PURPLE}No files found when scanning.{Colors.RESET}")
    else:
        end_time = perf_counter()
        finish_time = end_time - start_time
        print(f"\n{Colors.GREEN}Finished operation.{Colors.RESET}")
        print(f"{Colors.ITALIC + Colors.GREEN}Rule operation took {finish_time:.2f} seconds.{Colors.RESET}")

if __name__ == "__main__":
    main()
