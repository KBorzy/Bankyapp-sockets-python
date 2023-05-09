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


def account_exit(account_number):
    for user in users:
        if user['AccountNumber'] == account_number:
            return True


def login(password):
    for user in users:
        if user['Password'] == password:
            return user


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
        for user in users:
            writer.writerow(user)
        print('The users list has been updated.')


def update_user_list(account):
    for user in users:
        if account['AccountNumber'] in user:
            user.update(account)
    update_users()


def deposit(account, amount):
    if amount > 0:
        account['Balance'] = float(account['Balance']) + amount
        update_user_list(account)
        print(f'Deposited {amount} into the account nr:{account["AccountNumber"]}')
        print(f'New balance: {account["Balance"]}')
        return True
    else:
        return False


def withdraw(account, amount):
    if amount > 0:
        account['Balance'] = float(account['Balance']) - amount
        update_user_list(account)
        print(f'{amount} has been withdrawn to account nr:{account["AccountNumber"]}')
        print(f'New balance: {account["Balance"]}')
        return True
    else:
        return False


def transfer(src_acc, dst_acc, amount):
    if amount > 0:
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
            print(f'Transfered {amount} from account nr:{src_acc} to account nr:{dst_acc}.')
            return True
        else:
            return False
    else:
        return False


def create_account(name, password, balance):
    account_number = ''.join(random.choices('0123456789', k=3))
    account = {'AccountNumber': account_number, 'Name': name, 'Password': password, 'Balance': balance}
    users.append(account)
    print(f'Account has been created: Account nr:{account_number}, name: {name}, balance:{balance}')
    update_users()
    return account


load_users()

try:
    ServerSideSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Socket is listening..')
ServerSideSocket.listen(10)


def multi_threaded_client(connection, client_id):
    connection.send(str.encode('Server is working:'))

    account_number = None
    password = None
    authorized_user = False
    authorized_admin = False

    while True:
        data = connection.recv(1024)

        if not data:
            break

        command = data.decode('utf-8').strip().split()

        if not authorized_admin:
            if command[0] == 'admin' and len(command) == 2:
                admin_login = command[1]
                if admin_login == ADMIN_LOGIN:
                    connection.sendall(str.encode('Admin exists'))
                else:
                    connection.sendall(str.encode('Login not found on server.'))
            elif command[0] == 'login' and len(command) == 2:
                password = command[1]
                if password == ADMIN_PASSWORD:
                    authorized_admin = True
                    print(f'Admin authorized. Open access.')
                    json_user_data = json.dumps(users)
                    connection.sendall(json_user_data.encode('utf-8'))
                    continue
                else:
                    connection.sendall(str.encode('Incorrect password or account number.'))
            else:
                connection.sendall(str.encode(f'Unauthorized. Please log in first.'))
        else:
            # admin is authorized

            if command[0] == 'accounts' and len(command) == 1:
                print('Sending accounts details to client (admin)')
                b = json.dumps(users).encode('utf-8')
                connection.sendall(b)



            if command[0] == 'create' and len(command) == 4:
                account_name = command[1]
                account_password = command[2]
                account_balance = command[3]

        if not authorized_user:
            if command[0] == 'account' and len(command) == 2:
                account_number = command[1]
                if account_exit(account_number):
                    connection.sendall(str.encode('Account exists'))
                else:
                    connection.sendall(str.encode(f'Account nr:{account_number} not found.'))
            elif command[0] == 'login' and len(command) == 2:
                password = command[1]
                user = login(password)
                if user is not None and user['AccountNumber'] == account_number:
                    authorized_user = True
                    print(f'Account nr:{account_number} authorized. Open access.')
                    json_user_data = json.dumps(user)
                    connection.sendall(json_user_data.encode('utf-8'))
                else:
                    connection.sendall(str.encode('Incorrect password or account number.'))
            else:
                connection.sendall(str.encode(f'Unauthorized. Please log in first.'))
        else:
            # user is authorized and can access bank functions

            if command[0] == 'balance' and len(command) == 1:
                print(f'Balance checking for account nr:{account_number}')
                connection.sendall(f'Your balance: {get_balance(account_number)}'.encode('utf-8'))

            elif command[0] == 'deposit' and len(command) == 3:
                amount = float(command[2])
                account_number = int(command[1])
                account = get_user(account_number)
                if deposit(account, amount):
                    connection.sendall(
                        f'Deposited {amount} into the account nr:{account_number}. New balance: {account["Balance"]}'.encode(
                            'utf-8'))
                else:
                    connection.sendall(str.encode(f'Invalid deposit amount.'))

            elif command[0] == 'withdraw' and len(command) == 3:
                amount = float(command[2])
                account_number = int(command[1])
                account = get_user(account_number)
                if withdraw(account, amount):
                    connection.sendall(
                        f'{amount} has been withdrawn from account nr:{account_number}. New balance: {account["Balance"]}'.encode(
                            'utf-8'))
                else:
                    connection.sendall(str.encode(f'Invalid withdraw amount.'))
            elif command[0] == 'transfer' and len(command) == 4:
                src_acc = command[1]
                dst_acc = command[2]
                amount = float(command[3])
                if transfer(src_acc, dst_acc, amount):
                    connection.sendall(
                        f'Successfully transferred {amount} from {src_acc} to {dst_acc}.'.encode('utf-8'))
                else:
                    connection.sendall(str.encode(f'Transfer failed.'))
            elif command[0] == 'logout' and len(command) == 2:
                authorized_user = False
                account_number = None
                password = None
                connection.sendall(str.encode(f'Logged out.'))
                print(f'Account nr:{command[1]} has been logged out.')
            else:
                connection.sendall(str.encode(f'Unknown command: {data.decode("utf-8")}'))

    connection.close()


while True:
    Client, address = ServerSideSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(multi_threaded_client, (Client, ThreadCount + 1))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))

ServerSideSocket.close()
