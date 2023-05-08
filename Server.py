import socket
from _thread import *
import csv
import json

ServerSideSocket = socket.socket()
host = '127.0.0.1'
port = 2223
ThreadCount = 0
users = []


def get_user(account_number):
    for user in users:
        if str(account_number) == user['AccountNumber']:
            return user
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
        print('The user list has been updated.')


def update_user_list(account):
    for user in users:
        if account['AccountNumber'] in user:
            user.update(account)
    update_users()


def deposit(account, amount):
    if amount > 0:
        account['Balance'] = float(account['Balance']) + amount
        update_user_list(account)
        print(f'Deposited {amount} into the account nr. {account["AccountNumber"]}')
        print(f'New balance: {account["Balance"]}')
        return True
    else:
        return False


def withdraw(account, amount):
    if amount > 0:
        account['Balance'] = float(account['Balance']) - amount
        update_user_list(account)
        print(f'{amount} has been withdrawn to account nr. {account["AccountNumber"]}')
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
            src_user['Balance'] -= amount
            dst_user['Balance'] += amount
            print(f'Transfered {amount} from account nr.{src_acc} to account nr. {dst_acc}.')
            return True
        else:
            return False
    else:
        return False


load_users()

try:
    ServerSideSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Socket is listening..')
ServerSideSocket.listen(5)


def multi_threaded_client(connection, client_id):
    connection.send(str.encode('Server is working:'))

    account_number = None
    password = None
    authorized = False

    while True:
        data = connection.recv(2048)

        if not data:
            break

        command = data.decode('utf-8').strip().split()

        if not authorized:
            if command[0] == 'account' and len(command) == 2:
                account_number = command[1]
                if account_exit(account_number):
                    connection.sendall(str.encode('Account exists'))
                else:
                    connection.sendall(str.encode(f'Account number {account_number} not found.'))
            elif command[0] == 'login' and len(command) == 2:
                password = command[1]
                user = login(password)
                if user is not None and user['AccountNumber'] == account_number:
                    authorized = True
                    # connection.sendall(str.encode('Login successful'))
                    json_user_data = json.dumps(user)
                    connection.sendall(json_user_data.encode('utf-8'))
                else:
                    connection.sendall(str.encode('Incorrect password or account number.'))
            else:
                connection.sendall(str.encode(f'Unauthorized. Please log in first.'))
        else:
            # user is authorized and can access bank functions
            if command[0] == 'deposit' and len(command) == 3:
                amount = float(command[2])
                account_number = int(command[1])
                account = get_user(account_number)
                if deposit(account, amount):
                    connection.sendall(f'Deposited {amount} into the account nr. {account_number}'.encode('utf-8'))
                    break
                else:
                    connection.sendall(str.encode(f'Invalid deposit amount.'))

            elif command[0] == 'withdraw' and len(command) == 3:
                amount = float(command[2])
                account_number = int(command[1])
                account = get_user(account_number)
                if withdraw(account, amount):
                    connection.sendall(
                        f'{amount} has been withdrawn from account nr. {account_number}. New balance: {account["Balance"]}'.encode(
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
            elif command[0] == 'logout':
                authorized = False
                account_number = None
                password = None
                connection.sendall(str.encode(f'Logged out.'))
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
