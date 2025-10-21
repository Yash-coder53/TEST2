# import libraries
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerChannel, ChannelParticipantsSearch
from telethon.errors.rpcerrorlist import (
    PeerFloodError, UserPrivacyRestrictedError, PhoneNumberBannedError,
    ChatAdminRequiredError, ChatWriteForbiddenError, UserBannedInChannelError,
    UserAlreadyParticipantError, FloodWaitError
)
from telethon.tl.functions.channels import InviteToChannelRequest, GetParticipantsRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, AddChatUserRequest
from telethon.tl.functions.channels import JoinChannelRequest
import sys
import os
import pickle
import time
import random
from colorama import init, Fore

init()

# Color definitions
r = Fore.RED
lg = Fore.GREEN
rs = Fore.RESET
w = Fore.WHITE
grey = '\033[97m'
cy = Fore.CYAN
ye = Fore.YELLOW
colors = [r, lg, w, ye, cy]
info = lg + '[' + w + 'i' + lg + ']' + rs
error = lg + '[' + r + '!' + lg + ']' + rs
success = w + '[' + lg + '*' + w + ']' + rs
INPUT = lg + '[' + cy + '~' + lg + ']' + rs
plus = w + '[' + lg + '+' + w + ']' + rs
minus = w + '[' + lg + '-' + w + ']' + rs

def banner():
    # fancy logo
    b = [
        ' _____     _            __   ___      __ _______    _____',
        '/ ____|   |  |          /\    \ \\   / / |  ____|  |   __ \\',
        '| (___ |  |  |         /  \    \ \\_/ /  | |__     |   |__) |',
        ' \\___ \\ |  |        / /\\ \   \   /    |  __|    |   _  /',
        ' ____) |  |  |____   / ____ \\   | |     | |____   | | \\ \\',
        '|_____/   |_______| /_/    \\_\\ |_|     |______|  |_|  \\_\\',
    ]
    for char in b:
        print(f'{random.choice(colors)}{char}{rs}')
    print(f'{lg}   Version: {w}1.2{lg} | Author: {w}Cryptonian{rs}\n')

# function to clear screen
def clr():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_accounts():
    """Load accounts from file with error handling"""
    accounts = []
    if not os.path.exists('vars.txt'):
        print(f'{error} {r}vars.txt file not found!{rs}')
        return accounts
    
    try:
        with open('vars.txt', 'rb') as f:
            while True:
                try:
                    accounts.append(pickle.load(f))
                except EOFError:
                    break
        print(f'{info}{lg} Loaded {w}{len(accounts)}{lg} accounts{rs}')
    except Exception as e:
        print(f'{error} {r}Error loading accounts: {e}{rs}')
    
    return accounts

def check_banned_accounts(accounts):
    """Check and remove banned accounts"""
    if not accounts:
        print(f'{error} {r}No accounts to check!{rs}')
        return []
    
    print('\n' + info + lg + ' Checking for banned accounts...' + rs)
    banned = []
    valid_accounts = []
    
    for a in accounts:
        phn = a[0]
        print(f'{plus}{grey} Checking {lg}{phn}{rs}', end=' ')
        try:
            clnt = TelegramClient(f'sessions/{phn}', 3910389, '86f861352f0ab76a251866059a6adbd6')
            clnt.connect()
            
            if not clnt.is_user_authorized():
                try:
                    clnt.send_code_request(phn)
                    print(f'{lg}OK{rs}')
                    valid_accounts.append(a)
                except PhoneNumberBannedError:
                    print(f'{r}BANNED{rs}')
                    banned.append(a)
                except Exception as e:
                    print(f'{r}ERROR: {e}{rs}')
                    # Keep account on other errors
                    valid_accounts.append(a)
            else:
                print(f'{lg}AUTHORIZED{rs}')
                valid_accounts.append(a)
                
        except Exception as e:
            print(f'{r}CONNECTION ERROR: {e}{rs}')
            valid_accounts.append(a)  # Keep account on connection errors
        finally:
            try:
                clnt.disconnect()
            except:
                pass
    
    # Show results
    if banned:
        print(f'\n{error} {r}Found {len(banned)} banned accounts:{rs}')
        for acc in banned:
            print(f'{minus} {r}{acc[0]}{rs}')
    else:
        print(f'\n{success} {lg}No banned accounts found!{rs}')
    
    return valid_accounts

def save_accounts(accounts):
    """Save accounts to file"""
    try:
        with open('vars.txt', 'wb') as f:
            for account in accounts:
                pickle.dump(account, f)
        return True
    except Exception as e:
        print(f'{error} {r}Error saving accounts: {e}{rs}')
        return False

def log_status(scraped, index):
    """Log scraping progress"""
    try:
        with open('status.dat', 'wb') as f:
            pickle.dump([scraped, int(index)], f)
        print(f'{info}{lg} Progress saved to {w}status.dat{rs}')
    except Exception as e:
        print(f'{error} {r}Error saving progress: {e}{rs}')

def load_status():
    """Load scraping progress"""
    try:
        with open('status.dat', 'rb') as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError, Exception):
        return None

def exit_window():
    """Graceful exit"""
    input(f'\n{cy} Press enter to exit...{rs}')
    clr()
    banner()
    sys.exit()

def get_user_input():
    """Get user input for scraping and adding"""
    status = load_status()
    
    if status:
        scraped_grp, index = status
        resume = input(f'{INPUT}{cy} Resume scraping members from {w}{scraped_grp}{lg}? [y/n]: {r}')
        if resume.lower() in ['y', 'yes']:
            return scraped_grp, index
        else:
            try:
                os.remove('status.dat')
            except:
                pass
    
    scraped_grp = input(f'{INPUT}{cy} Public/Private group link to scrape members: {r}')
    return scraped_grp, 0

def scrape_members(client, scraped_grp):
    """Scrape members from a group"""
    members = []
    try:
        # Join the group to scrape
        if '/joinchat/' in scraped_grp:
            g_hash = scraped_grp.split('/joinchat/')[1]
            try:
                client(ImportChatInviteRequest(g_hash))
                print(f'{plus}{grey} Joined private group to scrape{rs}')
            except UserAlreadyParticipantError:
                pass
        else:
            client(JoinChannelRequest(scraped_grp))
            print(f'{plus}{grey} Joined public group to scrape{rs}')
        
        # Get group entity
        scraped_grp_entity = client.get_entity(scraped_grp)
        
        # Scrape members
        print(f'{info}{lg} Scraping members...{rs}')
        offset = 0
        limit = 200
        
        while True:
            participants = client(GetParticipantsRequest(
                channel=scraped_grp_entity,
                filter=ChannelParticipantsSearch(''),
                offset=offset,
                limit=limit,
                hash=0
            ))
            
            if not participants.users:
                break
                
            members.extend(participants.users)
            offset += len(participants.users)
            print(f'{info}{lg} Scraped {w}{len(members)}{lg} members so far...{rs}')
            
            if len(participants.users) < limit:
                break
                
        return members, scraped_grp_entity
        
    except Exception as e:
        print(f'{error} {r}Error scraping members: {e}{rs}')
        return [], None

def add_members_to_group(client, target, choice, members, start_index, acc_name, sleep_time):
    """Add members to target group"""
    adding_status = 0
    peer_flood_count = 0
    max_peer_flood = 5
    
    try:
        # Join target group
        if choice == 0:  # Public group
            client(JoinChannelRequest(target))
            target_entity = client.get_entity(target)
            target_details = InputPeerChannel(target_entity.id, target_entity.access_hash)
            print(f'{plus}{grey} Joined public target group{rs}')
        else:  # Private group
            if '/joinchat/' in target:
                grp_hash = target.split('/joinchat/')[1]
                client(ImportChatInviteRequest(grp_hash))
            target_entity = client.get_entity(target)
            target_details = target_entity
            print(f'{plus}{grey} Joined private target group{rs}')
            
    except UserAlreadyParticipantError:
        print(f'{info}{lg} Already in target group{rs}')
        target_entity = client.get_entity(target)
        target_details = InputPeerChannel(target_entity.id, target_entity.access_hash) if choice == 0 else target_entity
    except Exception as e:
        print(f'{error} {r}Failed to join target group: {e}{rs}')
        return adding_status, start_index
    
    # Add members
    end_index = min(start_index + 50, len(members))  # Reduced batch size
    
    for i in range(start_index, end_index):
        user = members[i]
        
        if peer_flood_count >= max_peer_flood:
            print(f'{error} {r}Too many Peer Flood Errors! Stopping...{rs}')
            break
            
        try:
            if choice == 0:  # Public group
                client(InviteToChannelRequest(target_details, [user]))
            else:  # Private group
                client(AddChatUserRequest(target_details, user, fwd_limit=10))
            
            user_name = user.first_name or f"User{user.id}"
            print(f'{plus}{grey} {cy}{user_name} {lg}--> {cy}{target_entity.title}{rs}')
            adding_status += 1
            
            if sleep_time > 0:
                time.sleep(sleep_time)
                
        except UserPrivacyRestrictedError:
            print(f'{minus} {r}User privacy restricted{rs}')
        except PeerFloodError:
            print(f'{error} {r}Peer Flood Error{rs}')
            peer_flood_count += 1
        except UserAlreadyParticipantError:
            print(f'{minus} {r}User already in group{rs}')
        except FloodWaitError as e:
            print(f'{error} {r}Flood wait: {e} seconds{rs}')
            break
        except ChatWriteForbiddenError:
            print(f'{error} {r}No permission to add users{rs}')
            break
        except ChatAdminRequiredError:
            print(f'{error} {r}Admin rights needed{rs}')
            break
        except Exception as e:
            print(f'{error} {r}Error adding user: {e}{rs}')
            continue
    
    return adding_status, end_index

def main():
    # Initial setup
    clr()
    banner()
    
    # Load and check accounts
    accounts = load_accounts()
    if not accounts:
        print(f'{error} {r}No accounts found! Please add accounts first.{rs}')
        exit_window()
    
    accounts = check_banned_accounts(accounts)
    if not accounts:
        print(f'{error} {r}No valid accounts remaining!{rs}')
        exit_window()
    
    # Save cleaned accounts
    if not save_accounts(accounts):
        print(f'{error} {r}Failed to save accounts!{rs}')
        exit_window()
    
    print(f'{success} {lg}Sessions created!{rs}')
    time.sleep(2)
    clr()
    banner()
    
    # Get user input
    scraped_grp, index = get_user_input()
    
    # Reload accounts (in case they were modified)
    accounts = load_accounts()
    
    print(f'{info}{lg} Total accounts: {w}{len(accounts)}{rs}')
    
    try:
        number_of_accs = int(input(f'{INPUT}{cy} Enter number of accounts to use: {r}'))
        number_of_accs = min(number_of_accs, len(accounts))
    except ValueError:
        print(f'{error} {r}Invalid number!{rs}')
        number_of_accs = 1
    
    print(f'{info}{cy} Choose an option:{rs}')
    print(f'{cy}[0]{lg} Add to public group{rs}')
    print(f'{cy}[1]{lg} Add to private group{rs}')
    
    try:
        choice = int(input(f'{INPUT}{cy} Enter choice: {r}'))
        if choice not in [0, 1]:
            choice = 0
    except ValueError:
        choice = 0
    
    target = input(f'{INPUT}{cy} Enter {"public" if choice == 0 else "private"} group link: {r}')
    
    try:
        sleep_time = int(input(f'{INPUT}{cy} Enter delay time per request{w}[{lg}0 for None{w}]: {r}'))
        sleep_time = max(0, sleep_time)
    except ValueError:
        sleep_time = 5
    
    print(f'{grey}_'*50)
    
    # Select accounts to use
    to_use = accounts[:number_of_accs]
    remaining_accounts = accounts[number_of_accs:]
    
    # Save account rotation
    if not save_accounts(remaining_accounts + to_use):
        print(f'{error} {r}Warning: Failed to save account rotation!{rs}')
    
    print(f'{success}{lg} Adding members using {w}{len(to_use)}{lg} account(s){rs}')
    
    total_added = 0
    current_index = index
    
    for i, acc in enumerate(to_use):
        print(f'\n{plus}{lg} Account {w}{i+1}{lg} of {w}{len(to_use)}{rs}')
        print(f'{plus}{grey} User: {cy}{acc[0]}{rs}')
        
        try:
            client = TelegramClient(f'sessions/{acc[0]}', 3910389, '86f861352f0ab76a251866059a6adbd6')
            client.start(acc[0])
            acc_name = client.get_me().first_name
            print(f'{plus}{lg} Logged in as: {cy}{acc_name}{rs}')
            
            # Scrape members
            members, scraped_grp_entity = scrape_members(client, scraped_grp)
            
            if not members:
                print(f'{error} {r}No members scraped!{rs}')
                client.disconnect()
                continue
            
            print(f'{info}{lg} Found {w}{len(members)}{lg} members to add{rs}')
            
            # Add members
            added, new_index = add_members_to_group(
                client, target, choice, members, current_index, 
                acc_name, sleep_time
            )
            
            total_added += added
            current_index = new_index
            
            # Save progress
            if current_index < len(members):
                log_status(scraped_grp, current_index)
            
            client.disconnect()
            
            print(f'{success}{lg} Account completed: {w}{added}{lg} users added{rs}')
            
        except Exception as e:
            print(f'{error} {r}Account error: {e}{rs}')
            continue
    
    print(f'\n{success}{lg} Session completed!{rs}')
    print(f'{info}{lg} Total users added: {w}{total_added}{rs}')
    print(f'{info}{lg} Progress saved: {w}{current_index}{lg} of {w}{len(members) if 'members' in locals() else 'N/A'}{rs}')
    
    exit_window()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f'\n{error} {r}Operation cancelled by user{rs}')
        exit_window()
    except Exception as e:
        print(f'\n{error} {r}Unexpected error: {e}{rs}')
        exit_window()
