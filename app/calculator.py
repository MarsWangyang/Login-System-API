# 結合tests/test_calculations.py所使用
# 這邊是寫出範例function and class，在test時候可以直接做使用
def add(num1: int, num2: int):
    return num1 + num2


def subtract(num1: int, num2: int):
    return num1 - num2


def multipy(num1: int, num2: int):
    return num1 * num2


def divide(num1: int, num2: int):
    return num1 // num2


class InsufficientFunds(Exception):
    pass


class BankAccount():
    def __init__(self, starting_balance=0):
        self.balance = starting_balance

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFunds("Insufficient funds in account")
        self.balance -= amount

    def collect_interest(self):
        self.balance *= 1.1
