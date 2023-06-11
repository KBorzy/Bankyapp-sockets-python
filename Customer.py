import socket
import json

ClientMultiSocket = socket.socket()
host = '127.0.0.1'
port = 2223
user_data = {}

print('Waiting for connection response')

try:
    ClientMultiSocket.connect((host, port))
except socket.error as e:
    print(str(e))
res = ClientMultiSocket.recv(1024)

# prompt user for account number
account_number = ''
while not account_number:
    account_number = input('Please enter your account number: ').strip()
# send account number to server
ClientMultiSocket.send(str.encode(f'account {account_number}'))
res = ClientMultiSocket.recv(1024)


# check if account number exists on server
if res.decode('utf-8') == 'Account exists':

# prompt user for password
    password = input('Please enter your password: ')
    # send password to server
    ClientMultiSocket.send(str.encode(f'login {password}'))
    res = ClientMultiSocket.recv(1024)

    # check if login was successful
    if res.decode('utf-8') != 'Incorrect password or account number.':
        user = json.loads(res.decode('utf-8'))

        welcome_message = f"**** Welcome, {user['Name']} ! ****"
        balance_message = f"  ** balance: {user['Balance']} **"

        print(welcome_message)
        print(balance_message)
        print("\nCommands:")
        print("- - - - \"balance\"    |    to check balance")
        print("- - - - \"deposit {amount}\"    |    to deposit funds")
        print("- - - - \"withdraw {amount}\"    |    to withdraw funds")
        print("- - - - \"transfer {{destination account number}} {{amount}}\"    |    to transfer funds")
        print("- - - - \"logout\"    |    to log out of your account")

        while True:
            # prompt user for command
            command = input('Please enter a command (balance, deposit, withdraw, transfer, logout): ').strip().split()
            if len(command) > 0:
                # handle deposit command
                if command[0] == 'balance' and len(command) == 1:
                    ClientMultiSocket.send(str.encode('balance'))
                    res = ClientMultiSocket.recv(1024)
                    print(res.decode('utf-8'))
                    continue

                elif command[0] == 'deposit' and len(command) == 2:
                    amount = int(command[1])
                    if amount <= 0:
                        print('Wrong amount. Must be above 0.')
                    else:
                        ClientMultiSocket.send(str.encode(f'deposit {amount}'))
                        res = ClientMultiSocket.recv(1024)
                        print(res.decode('utf-8'))
                    continue

                # handle withdraw command
                elif command[0] == 'withdraw' and len(command) == 2:
                    amount = int(command[1])
                    ClientMultiSocket.send(str.encode(f'withdraw {amount}'))
                    res = ClientMultiSocket.recv(1024)
                    print(res.decode('utf-8'))
                    continue

                # handle transfer command
                elif command[0] == 'transfer' and len(command) == 3:
                    dst_acc = command[1]
                    amount = int(command[2])
                    ClientMultiSocket.send(str.encode(f'transfer {dst_acc} {amount}'))
                    res = ClientMultiSocket.recv(1024)
                    print(res.decode('utf-8'))
                    continue

                elif command[0] == 'logout' and len(command) == 1:
                    ClientMultiSocket.send(str.encode(f'logout'))
                    res = ClientMultiSocket.recv(1024)
                    print(res.decode('utf-8'))
                    break

                    # handle invalid command
                else:
                    print('Invalid command. Please try again.')
                    continue
            else:
                print('Please enter a command.')
            ClientMultiSocket.close()
            break

            # handle login failure
    else:
        print('Incorrect password. Please try again.')

        # handle account number not found on server
else:
    print('Account number not found on server.')
