import socket
import json
import struct
import pickle

ClientMultiSocket = socket.socket()
host = '127.0.0.1'
port = 2223
user_data = {}


def receive_data(conn):
    data = b""
    while True:
        packet = conn.recv(4096)
        data += packet
        if len(packet) < 4096:
            break
    return data.decode('utf-8')

def show_accounts(accounts):
    for acc in accounts:
        for val in acc.values():
            print(val, end=' ')
        print()

print('Waiting for connection response')

try:
    ClientMultiSocket.connect((host, port))
except socket.error as e:
    print(str(e))

res = ClientMultiSocket.recv(1024)
# prompt user for account number
login = input('Please enter your login: ')

# send login to server
ClientMultiSocket.send(str.encode(f'admin {login}'))
res = ClientMultiSocket.recv(1024)

# check if account number exists on server
if res.decode('utf-8') == 'Admin exists':

    # prompt user for password
    password = input('Please enter your password: ')

    # send password to server
    ClientMultiSocket.send(str.encode(f'login {password}'))
    res = ClientMultiSocket.recv(1024)

    # check if login was successful
    if res.decode('utf-8') != 'Incorrect password or account number.':
        print(res.decode('utf-8'))
        welcome_message = f"**** Welcome, Admin ! ****"

        print(welcome_message)
        print("  ** Control Panel **")
        print("\nCommands:")
        print("- - - - \"accounts\"    |    to print accounts details ")
        print("- - - - \"create\"    |    to create account")
        print("- - - - \"modify {number_of_account}\"    |    to modify account")
        print("- - - - \"logout\"    |    to log out of your account")

        while True:

            # prompt user for command
            command = input('Please enter a command (accounts, create, modify, logout): ').strip().split()
            if len(command) > 0:
                if command[0] == 'accounts' and len(command) == 1:
                    res = receive_data(ClientMultiSocket)

                    try:
                        accounts = json.loads(res)
                        show_accounts(accounts)
                    except json.JSONDecodeError as e:
                        print("Błąd parsowania JSON:", e)


                elif command[0] == 'create' and len(command) == 1:
                    print("Enter account details.")
                    account_name = input("Enter name: ")
                    account_password = input("Enter password: ")
                    account_balance = float(input("Enter balance: "))
                    ClientMultiSocket.send(str.encode(f'create {account_name} {account_password} {account_balance}'))
                    res = ClientMultiSocket.recv(1024)
                    print(res.decode('utf-8'))
                    continue

                elif command[0] == 'modify' and len(command) == 2:
                    account_number = int(command[1])
                    ClientMultiSocket.send(str.encode(f'modify {account_number}'))
                    res = ClientMultiSocket.recv(1024)
                    print(res.decode('utf-8'))

                    print("Select an option:")
                    print("- - - - \"change name\" | to change account name")
                    print("- - - - \"show details\" | to show account details")
                    sub_command = input().strip()

                    if sub_command == 'change name':
                        new_name = input("Enter new name: ")
                        ClientMultiSocket.send(str.encode(f"change_name {account_number} {new_name}"))
                        res = ClientMultiSocket.recv(1024)
                        print(res.decode('utf-8'))
                    elif sub_command == 'show details':
                        ClientMultiSocket.send(str.encode(f"show_details {account_number}"))
                        res = ClientMultiSocket.recv(1024)
                        print(res.decode('utf-8'))
                    else:
                        print('Invalid command. Please try again.')

                elif command[0] == 'logout' and len(command) == 1:
                    ClientMultiSocket.send(str.encode(f'logout {login}'))
                    res = ClientMultiSocket.recv(1024)
                    print(res.decode('utf-8'))
                    break

                else:
                    print('Invalid command. Please try again.')
            else:
                print('Please enter a command.')
        ClientMultiSocket.close()
    # handle login failure
    else:
        print('Incorrect password. Please try again.')

# handle account number not found on server
else:
    print('Login not found on server.')
