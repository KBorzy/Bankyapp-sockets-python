import socket
from _thread import *
import csv
import json
import random

ServerSideSocket = socket.socket()
host = '127.0.0.1'
port = 2223
ThreadCount = 0
users = []
client_ports = {}
ADMIN_LOGIN = 'admin'
ADMIN_PASSWORD = 'password'


def get_user(account_number):
    for user in users:
        if str(account_number) == user['AccountNumber']:
            return user
    return None


def get_balance(account_number):
    user = get_user(account_number)
    if user:
        return user['Balance']
    else:
        return None


def account_exist(account_number):
    for user in users:
        if user['AccountNumber'] == account_number:
            return True
    return False


def login(password):
    for user in users:
        if user['Password'] == password:
            return user
    return None


def load_users():
    with open('users.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            users.append(row)
        print('The user list has been loaded.')


def update_users():
    with open('users.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['AccountNumber', 'Name', 'Password', 'Balance'])
        writer.writeheader()
        writer.writerows(users)
        print('The users list has been updated.')


def update_user_list(account):
    for user in users:
        if account['AccountNumber'] == user['AccountNumber']:
            user.update(account)
    update_users()


def deposit(account, amount):
    if amount > 0:
        account['Balance'] = float(account['Balance']) + amount
        update_user_list(account)
        print(f'Deposited {amount} into the account nr: {account["AccountNumber"]}')
        print(f'New balance: {account["Balance"]}')
        return True
    else:
        return False


def withdraw(account, amount):
    if 0 < amount < float(account['Balance']):
        account['Balance'] = float(account['Balance']) - amount
        update_user_list(account)
        print(f'{amount} has been withdrawn from account nr: {account["AccountNumber"]}')
        print(f'New balance: {account["Balance"]}')
        return True
    else:
        return False


def transfer(src_acc, dst_acc, amount):
    src_user = get_user(src_acc)
    if 0 < amount < float(src_user['Balance']):
        src_user = None
        dst_user = None
        for user in users:
            if user['AccountNumber'] == src_acc:
                src_user = user
            if user['AccountNumber'] == dst_acc:
                dst_user = user
        if src_user is not None and dst_user is not None:
            src_user['Balance'] = float(src_user['Balance']) - amount
            dst_user['Balance'] = float(dst_user['Balance']) + amount
            update_user_list(src_user)
            update_user_list(dst_user)
            print(f'Transferred {amount} from account nr: {src_acc} to account nr: {dst_acc}.')
            return True
        else:
            return False
    else:
        return False


def create_account(name, password, balance):
    account_number = ''.join(random.choices('0123456789', k=3))
    account = {'AccountNumber': account_number, 'Name': name, 'Password': password, 'Balance': balance}
    users.append(account)
    print(f'Account has been created: Account nr: {account_number}, name: {name}, balance: {balance}')
    update_users()
    return account


def change_name(account_number, name):
    user = get_user(account_number)
    if user:
        user['Name'] = name
        update_user_list(user)
        print(f'Name updated for account nr: {account_number}. New name: {name}')
        return True
    else:
        return False


load_users()

try:
    ServerSideSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Socket is listening...')
ServerSideSocket.listen(5)


def multi_threaded_client(connection, client_id, port):
    connection.send(str.encode('Server is working:'))

    account_number = None
    password = None
    authorized = False
    is_admin = False

    def handle_account(command):
        nonlocal account_number, authorized, is_admin
        if command[0] == 'account' and len(command) == 2:
            account_number = command[1]
            if account_exist(account_number) or account_number == 'admin':
                connection.sendall(str.encode('Account exists'))
            else:
                connection.sendall(str.encode(f'Account nr: {account_number} not found.'))
        elif command[0] == 'login' and len(command) == 2:
            password = command[1]
            if password == ADMIN_PASSWORD and account_number == ADMIN_LOGIN:
                authorized = True
                is_admin = True

                connection.sendall(str.encode('Admin login successful.'))
                print('Admin has been authorized. Open access')
            else:
                user = login(password)
                if user is not None and user['AccountNumber'] == account_number:
                    authorized = True
                    client_ports[port] = account_number
                    print(f'Account nr: {account_number} authorized. Port: {[port]}. Open access.')
                    json_user_data = json.dumps(user)
                    connection.sendall(json_user_data.encode('utf-8'))
                else:
                    connection.sendall(str.encode('Incorrect password or account number.'))
                    print('Login attempt... Incorrect password or account number.')
        else:
            connection.sendall(str.encode(f'Unauthorized. Please log in first.'))

    def handle_authorized(command):
        nonlocal account_number, authorized, is_admin
        if is_admin:
            if command[0] == 'accounts' and len(command) == 1:
                print('Sending accounts details to client (admin)')
                b = json.dumps(users).encode('utf-8')
                connection.sendall(b)
                print('Accounts details has been sent to admin client')
            elif command[0] == 'create' and len(command) == 4:
                account_name = command[1]
                account_password = command[2]
                account_balance = command[3]
                create_account(account_name, account_password, account_balance)
                connection.sendall(str.encode('Account created successfully.'))
            elif command[0] == 'modify' and len(command) == 2:
                account_number = command[1]
                user = get_user(account_number)
                if user is not None:
                    connection.sendall(f'Account {user}'.encode('utf-8'))
                else:
                    connection.sendall('Account not found'.encode('utf-8'))
            elif command[0] == 'change' and len(command) == 4:
                account_number = command[2]
                new_name = command[3]
                if change_name(account_number, new_name):
                    connection.sendall(f'Changed name for account: {account_number}'.encode('utf-8'))
                else:
                    connection.sendall('Something went wrong...'.encode('utf-8'))
            elif command[0] == 'show' and len(command) == 2:
                account_number = command[1]
                connection.sendall(f'Details: {get_user(account_number)}'.encode('utf-8'))
            elif command[0] == 'logout' and len(command) == 1:
                authorized = False
                client_ports.pop(port)
                connection.sendall(str.encode('Logged out.'))
                print('Admin has been logged out.')

            else:
                connection.sendall(str.encode(f'Unknown command: {data.decode("utf-8")}'))
        else:
            if command[0] == 'balance' and len(command) == 1:
                print(f'Balance checking for account nr: {account_number}')
                connection.sendall(
                    f'Your balance: {get_balance(account_number)}'.encode('utf-8'))
            elif command[0] == 'deposit' and len(command) == 2:
                amount = float(command[1])
                account_number = client_ports.get(port)
                account = get_user(account_number)
                if deposit(account, amount):
                    connection.sendall(
                        f'Deposited {amount} into the account nr: {account_number}'.encode('utf-8'))

                else:
                    connection.sendall(str.encode('Invalid deposit amount.'))
            elif command[0] == 'withdraw' and len(command) == 2:
                amount = float(command[1])
                account_number = client_ports.get(port)
                account = get_user(account_number)
                if withdraw(account, amount):
                    connection.sendall(
                        f'{amount} has been withdrawn from account nr: {account_number}. New balance: {account["Balance"]}'.encode(
                            'utf-8'))
                else:
                    connection.sendall(str.encode('Invalid withdraw amount.'))
            elif command[0] == 'transfer' and len(command) == 3:
                src_acc = client_ports.get(port)
                dst_acc = command[1]
                amount = float(command[2])
                if transfer(src_acc, dst_acc, amount):
                    connection.sendall(
                        f'Successfully transferred {amount} from {src_acc} to {dst_acc}.'.encode('utf-8'))
                else:
                    connection.sendall(str.encode('Transfer failed. Invalid amount.'))
            elif command[0] == 'logout' and len(command) == 1:
                authorized = False
                account_number = None
                password = None
                connection.sendall(str.encode('Logged out.'))
                print(f'Account nr: {client_ports.get(port)} has been logged out.')
            else:
                connection.sendall(str.encode(f'Unknown command: {data.decode("utf-8")}'))

    def handle_command(command):
        if not authorized:
            handle_account(command)
            return
        else:
            handle_authorized(command)

    while True:
        data = connection.recv(2048)

        if not data:
            break
        command = data.decode('utf-8').strip().split()
        handle_command(command)

    connection.close()


while True:
    Client, address = ServerSideSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(multi_threaded_client, (Client, ThreadCount + 1, address[1]))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))

ServerSideSocket.close()
