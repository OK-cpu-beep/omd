from collections import Counter
from itertools import groupby


def task_1_solve(moscow: set, kazan: set):
    moscow_and_kazan = moscow.intersection(kazan)
    only_moscow = moscow.difference(kazan)
    only_kazan = kazan.difference(moscow)
    moscow_or_kazan = moscow.union(kazan)
    return moscow_and_kazan, only_moscow, only_kazan, len(moscow_or_kazan)


def task_2_solve(queries: list[str]):
    if not queries:
        return 0, None, None, 0, []
    amount_queries = len(queries)
    query_counter = Counter(queries)
    most_common_query_count = query_counter.most_common(1)[0]
    most_common_query = most_common_query_count[0]
    share_search = most_common_query_count[1] / amount_queries
    query_one_time = [query for query, count in query_counter.items()
                      if count == 1]
    return (amount_queries, dict(query_counter),
            most_common_query, share_search, query_one_time)


def task_3_solve(orders: list[dict]):
    if not orders:
        return 0, set(), dict(), 0
    returned_orders = [order for order in orders
                       if order["status"] == "returned"]
    delivered_orders = [order for order in orders
                        if order["status"] == "delivered"]
    returned_orders_sum = sum(order["amount"] for order in returned_orders)
    buyers_with_returns = {order["buyer"] for order in orders
                           if order["status"] == "returned"}
    delivered_orders.sort(key=lambda x: x["buyer"], reverse=True)
    delivered_orders_for_buyer = {buyer: len(list(orders)) for buyer, orders
                                  in groupby(delivered_orders,
                                             key=lambda x: x["buyer"])}
    if len(delivered_orders) == 0:
        mean_check = 0
    else:
        mean_check = sum(order["amount"]
                         for order in delivered_orders) / len(delivered_orders)

    return (returned_orders_sum, buyers_with_returns,
            len(delivered_orders_for_buyer), mean_check)


def task_4_solve(days: list[dict]):
    if not days:
        return 0, None, [], []
    revenue_week = sum(day["revenue"] for day in days)
    day_max_revenue = max(days, key=lambda x: x["revenue"])["day"]
    daily_revenues = {day["day"]: day["revenue"] / day["orders"]
                      for day in days if day["orders"] != 0}
    days_many_returns = [day["day"] for day in days
                         if day["orders"] != 0 and
                         day["returns"] / day["orders"] > 0.2]
    return (revenue_week, day_max_revenue, daily_revenues, days_many_returns)


def task_5_solve(reviews: list[dict]):
    if not reviews:
        return [], [], None, 0
    sorted_reviews = sorted(reviews, key=lambda x: x["id"])
    grouped_items_id = groupby(sorted_reviews, key=lambda x: x["id"])
    mean_rating_per_item = list()
    mean_rating_per_item_at_least_twice = list()
    for id, group in grouped_items_id:
        group_list = list(group)
        title = group_list[0]["product"].lower()
        stars_sum = sum(item["stars"] for item in group_list)
        amount_items = len(group_list)

        if amount_items != 0:
            mean_rating_per_item.append([id, title, stars_sum / amount_items])

        if len(group_list) >= 2:
            mean_rating_per_item_at_least_twice.append([
                id, title, stars_sum / amount_items
                ])

    worst_item = min(mean_rating_per_item_at_least_twice, key=lambda x: x[2])
    star_cnt = Counter([review["stars"] for review in reviews])
    one_two_star_reviews = star_cnt[1] + star_cnt[2]
    share_to_all = one_two_star_reviews / len(reviews)
    return (mean_rating_per_item, worst_item,
            one_two_star_reviews, share_to_all)


if __name__ == "__main__":
    moscow = {201, 202, 203, 204}
    kazan = {203, 204, 205, 206}
    print("Решение 1 задачи", task_1_solve(moscow, kazan))

    queries = ["чехол", "iphone", "чехол",
               "наушники", "iphone", "iphone",
               "кабель", "чехол", "iphone"]
    print("Решение 2 задачи", task_2_solve(queries))

    orders = [
        {"id": 1, "buyer": "anya", "status": "delivered", "amount": 900},
        {"id": 2, "buyer": "boris", "status": "returned", "amount": 4_500},
        {"id": 3, "buyer": "anya", "status": "delivered", "amount": 1_500},
        {"id": 4, "buyer": "vera", "status": "delivered", "amount": 3_200},
        {"id": 5, "buyer": "boris", "status": "delivered", "amount": 700},
        {"id": 6, "buyer": "gleb", "status": "returned", "amount": 2_100}
    ]
    print("Решение 3 задачи", task_3_solve(orders))

    days = [
        {"day": "пн", "orders": 20, "revenue": 40_000, "returns": 2},
        {"day": "вт", "orders": 16, "revenue": 19_200, "returns": 4},
        {"day": "ср", "orders": 25, "revenue": 55_000, "returns": 1},
        {"day": "чт", "orders": 10, "revenue": 12_000, "returns": 3},
        {"day": "пт", "orders": 30, "revenue": 48_000, "returns": 3}
    ]
    print("Решение 4 задачи", task_4_solve(days))

    reviews = [
        {"id": 1, "product": "Чехол", "stars": 5},
        {"id": 1, "product": "Чехол", "stars": 3},
        {"id": 1, "product": "Чехол", "stars": 4},
        {"id": 2, "product": "Наушники", "stars": 2},
        {"id": 2, "product": "наушники", "stars": 2},
        {"id": 2, "product": "НАУШНИКИ", "stars": 5},
        {"id": 3, "product": "Планшет", "stars": 5},
        {"id": 4, "product": "Колонка", "stars": 4},
        {"id": 4, "product": "Колонка", "stars": 4},
        {"id": 5, "product": "Кабель", "stars": 1}
    ]
    print("Решение 5 задачи", task_5_solve(reviews))
