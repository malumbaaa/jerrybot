from pymongo import MongoClient
import pymongo
from config import MONGO_CONNECTION_STRING

from datetime import date, time, datetime
import calendar
import locale


from collections import Counter
import matplotlib.pyplot as plt
import xlsxwriter

locale.setlocale(locale.LC_ALL, 'ru_RU')


def get_database():
    client = MongoClient(MONGO_CONNECTION_STRING)
    return client['VanderTest']


def reserve_table(table_number, date, people_count, time, telegram_id):
    user = find_user_by_telegramid(telegram_id)
    reserve_data = {
        "user_name": user["name"],
        "user_phone": user["phone"],
        "date": date,
        "time": time,
        "table_number": table_number,
        "people_count": people_count,
        "telegram_id": str(telegram_id)
    }
    db = get_database()
    reservations = db["Reservations"]
    reservations.insert_one(reserve_data)
    print(reserve_data)


def get_reserved_time(date: str, table: str) -> list:
    db = get_database()
    reservations_collection = db["Reservations"]
    reservations = list(reservations_collection.find({'date': date, 'table_number': table}))
    times = [i['time'] for i in reservations]
    return times


def get_reservations(date: str) -> list:
    db = get_database()
    reservations_collection = db["Reservations"]
    reservations = list(reservations_collection.find({'date': date}))
    return reservations


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
    uid = users.find_one({"telegram_id": f"{telegram_id}"})
    if uid is not None:
        return True
    else:
        return False


def get_all_users() -> list:
    db = get_database()
    users_collection = db["Users"]
    users = list(users_collection.find())
    return users


def get_all_orders() -> list:
    db = get_database()
    reservation_collection = db["Reservations"]
    reservations = list(reservation_collection.find())
    return reservations


def get_category_by_name(category_name):
    db = get_database()
    categories = db["Categories"]
    category = categories.find_one({"name": f"{category_name}"})
    return category


def add_dish(name: str, category_name: str, description: str, price: str, photo_id: str):
    category = get_category_by_name(category_name)
    user_data = {
        "name": name,
        "category": category["name"],
        "description": description,
        "price": price,
        "photo_id": photo_id
    }
    db = get_database()
    dishes_collection = db["Dishes"]
    dishes_collection.insert_one(user_data)


def add_category(name: str):
    user_data = {
        "name": name
    }
    db = get_database()
    categories_collection = db["Categories"]
    categories_collection.insert_one(user_data)


def get_categories() -> list:
    db = get_database()
    categories_collection = db["Categories"]
    categories = list(categories_collection.find())
    return categories


def get_stat_order():  # можно соеденить 2 функции
    db = get_database()
    reservation_collection = db["Reservations"]
    reservations = list(reservation_collection.find())
    all_stat = {
        "В среднем людей": [],
        "days": []
    }
    for reservation in reservations:
        all_stat['В среднем людей'].append(int(reservation['people_count']))
        date_res = reservation['date'].split('-')
        all_stat['days'].append((date(int(date_res[0]), int(date_res[1]), int(date_res[2])).strftime('%A')))
    all_stat['Общее количество заказов'] = len(all_stat['В среднем людей'])
    all_stat['В среднем людей'] = sum(all_stat['В среднем людей'])/len(all_stat['В среднем людей'])
    max = -1
    for_graph = []
    for weekday in calendar.day_name:
        count = all_stat['days'].count(weekday)
        all_stat[weekday] = count
        for_graph.append(count)
        if max < count:
            all_stat['Самый популярный день'] = weekday
            max = count
    plt.plot(calendar.day_name, for_graph,
             color='red', label='Кол-во заказов')
    plt.xticks(rotation=90)
    plt.legend(loc='best')
    plt.grid(True)
    plt.savefig(f'all_days.png')
    plt.close('all')
    del all_stat['days']
    data = ''
    for key, value in all_stat.items():
        data += f'{key}: {value}\n'
    return data


def get_stat_users():
    db = get_database()
    users = get_all_users()
    reservations = get_all_orders()
    users = dict.fromkeys([tg['telegram_id'] for tg in users], [])
    print(users)
    for reservation in reservations:
        date_res = reservation['date'].split('-')
        reservation['date'] = (date(int(date_res[0]), int(date_res[1]), int(date_res[2])).strftime('%A'))
        print(users[reservation['telegram_id']])
        users[reservation['telegram_id']] = users[reservation['telegram_id']]+[reservation,]
    stat_users = []
    workbook = xlsxwriter.Workbook('clients.xlsx')
    index = 1
    worksheet = workbook.add_worksheet('all_clients')
    worksheet.write(0, 0, 'Имя')
    worksheet.write(0, 1, 'Телефон')
    worksheet.write(0, 2, 'Количество заказов')
    worksheet.write(0, 3, 'Любимый столик')
    worksheet.write(0, 4, 'Любимый день недели')
    worksheet.write(0, 5, 'Среднее кол-во людей')
    for key, value in users.items():
        print(key)
        print(value)
        # stat_users.append({
        #     'Количество заказов: ': len(value),
        #     'Любимый столик: ': Counter([i['table_number'] for i in value]).most_common()[0],
        #     'Любимый день недели:': Counter([i['date'] for i in value]).most_common()[0],
        #     'Среднее кол-во людей: ': sum([int(i['people_count']) for i in value])/len(value),
        #     'Имя': value[0]['user_name'],
        #     'Телефон': value[0]['user_phone']  на случай, если нам всё-таки понадобится вид слловаря
        # })
        if len(value) == 0:
            pass
        else:
            worksheet.write(index, 0, f"{value[0]['user_name']}")
            worksheet.write(index, 1, f"{value[0]['user_phone']}")
            worksheet.write(index, 2, f'{len(value)}')
            worksheet.write(index, 3, f"{Counter([i['table_number'] for i in value]).most_common()[0][0]}")
            worksheet.write(index, 4, f"{Counter([i['date'] for i in value]).most_common()[0][0]}")
            worksheet.write(index, 5, f"{sum([int(i['people_count']) for i in value]) / len(value)}")
            index += 1
            stat_users.append(
                f'Количество заказов:  {len(value)}\n'+
                f"Любимый столик:  {Counter([i['table_number'] for i in value]).most_common()[0][0]}\n"+
                f"Любимый день недели: {Counter([i['date'] for i in value]).most_common()[0][0]}\n"+
                f"Среднее кол-во людей:  {sum([int(i['people_count']) for i in value]) / len(value)}\n"+
                f"Имя: {value[0]['user_name']}\n"+
                f"Телефон: {value[0]['user_phone']}\n"
            )
    workbook.close()
    return stat_users


def get_food_by_category(category):
    db = get_database()
    food_collection = db['Dishes']
    food = list(food_collection.find({"category": category}))
    return food


def get_food_by_name(name):
    db = get_database()
    food_collection = db['Dishes']
    food = food_collection.find_one({"name": name})
    return food


def get_stat_time():
    db = get_database()
    reservations = get_all_orders()
    time = []
    for hour in range(18, 24 + 4):
        if hour >= 24:
            hour -= 24
            hour = str(f"0{hour}")
        for minute in ['00', '30']:
            time.append(f'{hour}:{minute}')
    time_stat = dict.fromkeys(calendar.day_name)
    count_people = dict.fromkeys(calendar.day_name)
    for stat in time_stat:
        time_stat[stat] = dict.fromkeys(time, 0)
        count_people[stat] = dict.fromkeys(time, 0)
    for reservation in reservations:
        date_res = reservation['date'].split('-')
        reservation['date'] = (date(int(date_res[0]), int(date_res[1]), int(date_res[2])).strftime('%A'))
        time_stat[reservation['date']][reservation['time']] += 1
        count_people[reservation['date']][reservation['time']] += int(reservation['people_count'])
    for weekday in calendar.day_name:
        plt.plot(list(time_stat[weekday].keys()), list(time_stat[weekday].values()),
                 color='red', label='Кол-во заказов')
        plt.plot(list(count_people[weekday].keys()), list(count_people[weekday].values()),
                 color='green', label='Кол-во людей')
        plt.xticks(rotation=90)
        plt.legend(loc='best')
        plt.grid(True)
        plt.savefig(f'{weekday}.png')
        plt.close('all')
    returned_data = [time_stat, count_people]
    return returned_data


def add_order(telegram_id, food, table=4):
    print(food)
    user = find_user_by_telegramid(telegram_id)
    foods = food.split(";")
    food_to_db = ','.join(foods)
    price = 0
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    date_today = date.today()
    for food in foods:
        price += int(get_food_by_name(food)['price'])
    data = {
        'user_name': user['name'],
        'user_phone': user['phone'],
        'telegram_id': user['telegram_id'],
        'food': food_to_db,
        'price': price,
        'date': date_today.strftime("%d-%m-%Y"),
        'time': current_time,
        'table': table
    }
    db = get_database()
    orders_collection = db["Orders"]
    orders_collection.insert_one(data)


def stat_tables(table: int) -> None:
    db = get_database()
    orders_collection = db["Orders"]
    orders_table = list(orders_collection.find({"table": table}))
    workbook = xlsxwriter.Workbook('orders.xlsx')
    index = 1
    worksheet = workbook.add_worksheet(f'table_{table}')
    worksheet.write(0, 0, 'Имя')
    worksheet.write(0, 1, 'Телефон')
    worksheet.write(0, 2, 'Еда')
    worksheet.write(0, 3, 'Стоимость')
    worksheet.write(0, 4, 'Дата')
    worksheet.write(0, 5, 'Время')
    for order in orders_table:
        worksheet.write(index, 0, f"{order['user_name']}")
        worksheet.write(index, 1, f"{order['user_phone']}")
        worksheet.write(index, 2, f'{order["food"]}')
        worksheet.write(index, 3, f"{order['price']}")
        worksheet.write(index, 4, f"{order['date']}")
        worksheet.write(index, 5, f"{order['time']}")
        index += 1
    workbook.close()