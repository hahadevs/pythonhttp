
from helpers import Database


if __name__ == '__main__':
    db = Database()
    db.connect()
    all_users = db.get_all_for_admin()
    print(all_users)