import pytest
from app.calculator import InsufficientFunds, add, subtract, multipy, divide, BankAccount


# 利用pytest.fixture，就可以不用再每次每個test function當中再create object，
# 可以直接呼叫這個function來做object的建立，減少repitive code
# 在測試database的程式碼當中，很常可以利用fixture來去減少錯誤。
@pytest.fixture
def zero_bank_account():
    print("creating empty bank account")
    return BankAccount()


@pytest.fixture
def bank_account():
    return BankAccount(50)

# $ pytest -v -s 可以將print指令給顯示出來


@pytest.mark.parametrize("num1, num2, expected", [  # 會變成像是variables，來表示傳入的數字，這個variables要怎麼set都可以
    (3, 2, 5),  # first test
    (7, 1, 8),
    (12, 4, 16)
])
def test_add(num1, num2, expected):
    print("testing add function")
    # if code run fine, it will return True and nothing happen. If it is False, and it will raise an error.
    assert add(num1, num2) == expected


def test_subtract():
    assert subtract(9, 4) == 5


def test_multipy():
    assert multipy(2, 4) == 8


def test_divide():
    assert divide(8, 4) == 2


def test_bank_set_initial_amount(bank_account):
    assert bank_account.balance == 50


def test_bank_default_amount(zero_bank_account):
    assert zero_bank_account.balance == 0


def test_withdraw(bank_account):
    bank_account.withdraw(20)
    assert bank_account.balance == 30


def test_deposit(bank_account):
    bank_account.deposit(20)
    assert bank_account.balance == 70


def test_collect_interest(bank_account):
    bank_account.collect_interest()
    assert round(bank_account.balance, 6) == 55


@pytest.mark.parametrize("deposited, withdrew, expected", [
    (200, 100, 100),
    (50, 20, 30),
    (4000, 2000, 2000),
    # (20, 50, -30)
])
def test_bank_transaction(zero_bank_account, deposited, withdrew, expected):
    zero_bank_account.deposit(deposited)
    zero_bank_account.withdraw(withdrew)
    assert zero_bank_account.balance == expected


def test_insufficient_funds(bank_account):
    # 如果code會raise exception，那麼在pytest當中使用with pytest.raises(Exception)的方式來去抓取exception
    with pytest.raises(InsufficientFunds):
        bank_account.withdraw(600)
