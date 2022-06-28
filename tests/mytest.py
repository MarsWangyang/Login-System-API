from app.calculator import add

# if file name is not test_* or *_test, you can use $pytest <filename> in terminal

# function的名稱也會有指定，需要是test prefix才可以


def test_add():
    print("testing add function")

    # if code run fine, it will return True and nothing happen. If it is False, and it will raise an error.
    assert add(1, 3) == 4
