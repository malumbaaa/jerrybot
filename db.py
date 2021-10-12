from pymongo import MongoClient
import pymongo
from config import MONGO_CONNECTION_STRING


def get_database():
    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(MONGO_CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['VanderTest']


def reserve_table(table_number, date, people_count, telegram_id):
    user = find_user_by_telegramid(telegram_id)
    reserve_data = {
        "user_name": user["name"],
        "user_phone": user["phone"],
        "date": date,
        "table_number": table_number,
        "people_count": people_count,
        "telegram_id": str(telegram_id)
    }
    db = get_database()
    reservations = db["Reservations"]
    reservations.insert_one(reserve_data)
    print(reserve_data)


def get_reservations(date: str) -> list:
    db = get_database()
    reservations_collection = db["Reservations"]
    reservations = reservations_collection.find({"date" : f"{date}"})
    reservation_list = []
    for reservation in reservations:
        reservation_list.append(reservation)
    return reservation_list


def register_new_user(name: str, phone: str, telegram_id: str) -> bool:
    user_data = {
        "name": name,
        "phone": phone,
        "telegram_id": telegram_id
    }
    if not is_registered(telegram_id):
        db = get_database()
        users = db["Users"]
        users.insert_one(user_data)
        print(user_data)
        return True
    return False


def find_user_by_telegramid(telegram_id: str):
    db = get_database()
    users = db["Users"]
    uid = users.find_one({"telegram_id": f"{telegram_id}"})
    return uid


def is_registered(telegram_id: str) -> bool:
    db = get_database()
    users = db["Users"]
    uid = users.find_one({"telegram_id" : f"{telegram_id}"})
    if uid is not None:
        return True
    else:
        return False



