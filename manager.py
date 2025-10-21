from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import PhoneNumberBannedError
import pickle
import os
from colorama import init, Fore
from time import sleep
import requests
import random
import sys

init()

n = Fore.RESET
lg = Fore.LIGHTGREEN_EX
r = Fore.RED
w = Fore.WHITE
cy = Fore.CYAN
ye = Fore.YELLOW
colors = [lg, r, w, cy, ye]

def banner():
    # fancy logo
    b = [
        ' __  __ _____     _____ _____ _  __          _   _ _____  ______ _____ ',
        ' |  \/  |  __ \   / ____|_   _| |/ /    /\   | \ | |  __ \|  ____|  __ \ ',
        ' | \  / | |__) | | (___   | | |  /    /  \  |  \| | |  | | |__  | |__) | ',
        ' | |\/| |  _  /   \___ \  | | |  <    / /\ \ | . ` | |  | |  __| |  _  / ',
        ' | |  | | | \ \   ____) |_| |_| . \  / ____ \| |\  | |__| | |____| | \ \ ',
        ' |_|  |_|_|  \_\ |_____/|_____|_|\_\/_/    \_\_| \_|_____/|______|_|  \_\ ',
    ]
    for char in b:
        print(f'{random.choice(colors)}{char}{n}')
    print(f'   Version: 1.3 | Author: @SLAYER{n}\n')

def clr():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def ensure_sessions_dir():
    """Ensure sessions directory exists"""
    if not os.path.exists('sessions'):
        os.makedirs('sessions')

def load_accounts():
    """Load accounts from vars.txt"""
    accounts = []
    if not os.path.exists('vars.txt'):
        return accounts
    
    try:
        with open('vars.txt', 'rb') as f:
            while True:
                try:
                    accounts.append(pickle.load(f))
                except EOFError:
                    break
    except Exception as e:
        print(f'{r}[!] Error loading accounts: {e}{n}')
    
    return accounts

def save_accounts(accounts):
    """Save accounts to vars.txt"""
    try:
        with open('vars.txt', 'wb') as f:
            for account in accounts:
                pickle.dump(account, f)
        return True
    except Exception as e:
        print(f'{r}[!] Error saving accounts: {e}{n}')
        return False

def add_accounts():
    """Add new accounts"""
    new_accs = []
    try:
        number_to_add = int(input(f'\n{lg}[~] Enter number of accounts to add: {r}'))
        if number_to_add <= 0:
            print(f'{r}[!] Please enter a positive number{n}')
            return
    except ValueError:
        print(f'{r}[!] Please enter a valid number{n}')
        return

    for i in range(number_to_add):
        phone_number = input(f'\n{lg}[~] Enter Phone Number: {r}')
        parsed_number = ''.join(phone_number.split())
        new_accs.append(parsed_number)

    # Save all accounts at once
    accounts = load_accounts()
    accounts.extend([[phone] for phone in new_accs])
    
    if save_accounts(accounts):
        print(f'\n{lg}[i] Saved all accounts in vars.txt{n}')
    
    clr()
    print(f'\n{lg}[*] Logging in from new accounts\n')
    
    ensure_sessions_dir()
    successful_logins = 0
    
    for number in new_accs:
        try:
            client = TelegramClient(f'sessions/{number}', 3910389, '86f861352f0ab76a251866059a6adbd6')
            client.connect()
            
            if not client.is_user_authorized():
                client.send_code_request(number)
                code = input(f'{lg}[+] Enter verification code for {number}: {r}')
                client.sign_in(number, code)
            
            print(f'{lg}[+] Login successful for {number}{n}')
            client.disconnect()
            successful_logins += 1
            
        except Exception as e:
            print(f'{r}[!] Failed to login {number}: {e}{n}')
    
    print(f'\n{lg}[i] Successfully logged into {successful_logins}/{len(new_accs)} accounts{n}')
    input(f'\nPress enter to goto main menu...')

def filter_banned_accounts():
    """Filter out banned accounts"""
    accounts = load_accounts()
    
    if len(accounts) == 0:
        print(f'{r}[!] There are no accounts! Please add some and retry{n}')
        sleep(3)
        return

    banned_accs = []
    valid_accs = []
    
    ensure_sessions_dir()
    
    for account in accounts:
        phone = str(account[0])
        client = TelegramClient(f'sessions/{phone}', 3910389, '86f861352f0ab76a251866059a6adbd6')
        
        try:
            client.connect()
            
            if not client.is_user_authorized():
                try:
                    client.send_code_request(phone)
                    print(f'{lg}[+] {phone} is not banned{n}')
                    valid_accs.append(account)
                except PhoneNumberBannedError:
                    print(f'{r}[!] {phone} is banned!{n}')
                    banned_accs.append(account)
                except Exception as e:
                    print(f'{r}[!] Error checking {phone}: {e}{n}')
                    # Keep account if we're not sure it's banned
                    valid_accs.append(account)
            else:
                print(f'{lg}[+] {phone} is authorized and not banned{n}')
                valid_accs.append(account)
                
        except Exception as e:
            print(f'{r}[!] Connection error for {phone}: {e}{n}')
            valid_accs.append(account)  # Keep account on connection error
        finally:
            try:
                client.disconnect()
            except:
                pass

    if len(banned_accs) == 0:
        print(f'{lg}[i] Congrats! No banned accounts found{n}')
    else:
        if save_accounts(valid_accs):
            print(f'{lg}[i] Removed {len(banned_accs)} banned accounts{n}')
        else:
            print(f'{r}[!] Failed to save updated account list{n}')
    
    input('\nPress enter to goto main menu...')

def delete_account():
    """Delete specific account"""
    accounts = load_accounts()
    
    if len(accounts) == 0:
        print(f'{r}[!] No accounts found!{n}')
        input('\nPress enter to goto main menu...')
        return

    print(f'{lg}[i] Choose an account to delete\n')
    for i, acc in enumerate(accounts):
        print(f'{lg}[{i}] {acc[0]}{n}')
    
    try:
        index = int(input(f'\n{lg}[+] Enter a choice: {n}'))
        if index < 0 or index >= len(accounts):
            print(f'{r}[!] Invalid selection{n}')
            input('\nPress enter to goto main menu...')
            return
    except ValueError:
        print(f'{r}[!] Please enter a valid number{n}')
        input('\nPress enter to goto main menu...')
        return

    phone = str(accounts[index][0])
    session_file = f'sessions/{phone}.session'
    
    # Remove session file
    if os.path.exists(session_file):
        try:
            os.remove(session_file)
            print(f'{lg}[+] Removed session file: {session_file}{n}')
        except Exception as e:
            print(f'{r}[!] Could not remove session file: {e}{n}')
    
    # Remove from account list
    del accounts[index]
    
    if save_accounts(accounts):
        print(f'{lg}[+] Account {phone} deleted successfully{n}')
    else:
        print(f'{r}[!] Failed to update account list{n}')
    
    input(f'\nPress enter to goto main menu...')

def check_updates():
    """Check for updates"""
    print(f'\n{lg}[i] Checking for updates...{n}')
    try:
        version = requests.get('https://raw.githubusercontent.com/Cryptonian007/Astra/main/version.txt', timeout=10)
        version.raise_for_status()
        latest_version = float(version.text.strip())
    except Exception as e:
        print(f'{r}[!] Update check failed: {e}{n}')
        print(f'{r}[!] Please check your internet connection{n}')
        input('\nPress enter to goto main menu...')
        return

    current_version = 1.3
    
    if latest_version > current_version:
        prompt = input(f'{lg}[~] Update available [Version {latest_version}]. Download? [y/n]: {r}')
        if prompt.lower() in ['y', 'yes']:
            print(f'{lg}[i] Downloading updates...{n}')
            # Note: This would need to be implemented based on your update mechanism
            print(f'{lg}[i] Update functionality would download new version here{n}')
        else:
            print(f'{lg}[!] Update aborted.{n}')
    else:
        print(f'{lg}[i] Your tool is already up to date{n}')
    
    input('\nPress enter to goto main menu...')

def main():
    while True:
        clr()
        banner()
        print(f'{lg}[1] Add new accounts{n}')
        print(f'{lg}[2] Filter all banned accounts{n}')
        print(f'{lg}[3] Delete specific accounts{n}')
        print(f'{lg}[4] Check for updates{n}')
        print(f'{lg}[5] Quit{n}')
        
        try:
            choice = int(input(f'\n{lg}Enter your choice: {n}'))
        except ValueError:
            print(f'{r}[!] Please enter a valid number (1-5){n}')
            sleep(2)
            continue

        if choice == 1:
            add_accounts()
        elif choice == 2:
            filter_banned_accounts()
        elif choice == 3:
            delete_account()
        elif choice == 4:
            check_updates()
        elif choice == 5:
            clr()
            banner()
            print(f'{lg}[i] Thank you for using the tool!{n}')
            break
        else:
            print(f'{r}[!] Invalid choice. Please select 1-5{n}')
            sleep(2)

if __name__ == "__main__":
    # Ensure required modules are installed
    try:
        import telethon
        import colorama
    except ImportError as e:
        print(f'{r}[!] Missing required module: {e}{n}')
        print(f'{lg}[i] Please install required modules:{n}')
        print(f'{lg}[i] pip install telethon colorama requests{n}')
        sys.exit(1)
    
    # Ensure sessions directory exists
    ensure_sessions_dir()
    
    main()
