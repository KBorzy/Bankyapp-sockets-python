# Socket Server-Client Program

This is a Python program that demonstrates a socket server-client application. The program allows clients to connect to the server and perform various banking operations, such as checking balances, depositing, withdrawing, transferring funds, creating accounts, and modifying account details.

## Connection Information

The server uses the following connection details:

- **Host**: 127.0.0.1
- **Port**: 2223

## Getting Started

To get started with this program, follow the steps below:

1. Clone the repository:

   ```shell
   git clone https://github.com/KBorzy/Bankyapp-sockets-python
   ```

2. Change into the cloned directory:

   ```shell
   cd Bankyapp-sockets-python
   ```

3. Install any required dependencies:

   _No additional dependencies are required for this program._

4. Start the server:

   ```shell
   python Server.py
   ```

5. Connect to the server using the client:

   ```shell
   python Customer.py
   ```
   ```shell
   python Admin.py
   ```

## Commands

### Admin (admin.py)

The following commands are available for the admin:

- **accounts**: Print account details of all users.
- **create**: Create a new account. Usage: `create {name} {password} {balance}`.
- **modify**: Modify an existing account. Usage: `modify {account_number}`.
- **change**: Change the name of an account. Usage: `change {account_number} {new_name}`.
- **show details**: Show details of an account. Usage: `show details {account_number}`.
- **logout**: Log out from the admin account.

### Customer (customer.py)

The following commands are available for customers:

- **balance**: Check the account balance.
- **deposit**: Deposit funds into the account. Usage: `deposit {account_number} {amount}`.
- **withdraw**: Withdraw funds from the account. Usage: `withdraw {account_number} {amount}`.
- **transfer**: Transfer funds between accounts. Usage: `transfer {source_account} {destination_account} {amount}`.
- **logout**: Log out from the customer account.

Note: Replace `{}` placeholders with the appropriate values.
