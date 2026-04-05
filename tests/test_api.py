import random
import requests
import uuid
import time
import allure

base_url = "https://qa-internship.avito.com"

@allure.title("Создание объявления с валидными данными")
@allure.description("Проверка успешного создания объявления через POST запрос")
def test_create_item_positive():
    """Tест-кейс №1. Создание объявления с валидными данными"""

    print("\nTест-кейс №1")
    post_resource = "/api/1/item"
    seller_id = random.randint(111111, 999999)
    json_for_item = {
        "sellerID": seller_id,
        "name": "test_item",
        "price": 1000,
        "statistics": {
            "likes": 1,
            "viewCount": 1,
            "contacts": 1
        }
    }

    post_url = base_url + post_resource

    with allure.step("Отправка POST запроса на создание объявления"):
        result_post = requests.post(post_url, json=json_for_item)
        print(result_post.text)
        token = result_post.json()


    with allure.step("Проверка статус кода"):
        assert result_post.status_code == 200, "ОШИБКА, статус-код создания объявления не соответствует."
        print(f"Статус-код: {result_post.status_code}.")

    with allure.step("Проверка наличия поля status"):
        assert "status" in token, "ОШИБКА, поля status нет"
        print("Поле status есть.")


    with allure.step('Проверка наличия текст "Сохранили объявление" в поле status'):
        assert "Сохранили объявление" in token["status"], 'ОШИБКА, ответ в поле status не содержит "Сохранили объявление"'
        print('Текст "Сохранили объявление" в поле status есть.')


    with allure.step('Проверка наличия UUID идентификатора в поле status'):
        item_id = token["status"].split(" - ")[-1]
        try:
            uuid.UUID(item_id)
        except ValueError:
            assert False, "ОШИБКА, id не соответствует формату UUID"

        print(f'ID: {item_id} соответствует формату UUID')


@allure.title("Создание объявления без обязательного поля")
@allure.description("Проверка ошибки при создании объявления без обязательного поля name")
def test_create_item_without_field_negative():
    """Tест-кейс №2. Создание объявления без обязательного поля"""

    print("\nTест-кейс №2")
    post_resource = "/api/1/item"
    seller_id = random.randint(111111, 999999)
    json_for_item = {
        "sellerID": seller_id,
        "price": 1000,
        "statistics": {
            "likes": 1,
            "viewCount": 1,
            "contacts": 1
        }
    }

    post_negative_url = base_url + post_resource
    with allure.step("Отправка POST запроса на создание объявления"):
        result_negative_post = requests.post(post_negative_url, json=json_for_item)
        print(result_negative_post.text)
        token = result_negative_post.json()

    with allure.step("Проверка статус кода"):
        assert result_negative_post.status_code == 400, "ОШИБКА, статус-код создания объявления не соответствует."
        print(f"Статус-код: {result_negative_post.status_code}.")


    with allure.step("Проверка наличия поля result и наличия message внутри result"):
        assert "result" in token, "ОШИБКА, поля result нет"
        assert "message" in token["result"], "ОШИБКА, поля message нет"
        print("Поле message внутри ответа (внутри поля result есть)")


    with allure.step('Проверка наличия текст "поле name обязательно" в поле message'):
        message_text = token["result"]["message"]
        assert "поле name обязательно" in message_text, 'ОШИБКА, ответ в поле message не содержит "поле name обязательно"'
        print('Текст "поле name обязательно" в поле message есть.')


@allure.title("Идемпотентность создания объявления")
@allure.description("Проверка, что при повторной отправке одинакового POST запроса создаются разные объявления с уникальными id")
def test_idempotency_create():
    """Tест-кейс №3. Идемпотентность создания объявления"""

    print("\nTест-кейс №3")
    post_resource = "/api/1/item"
    seller_id = random.randint(111111, 999999)
    json_for_item = {
        "sellerID": seller_id,
        "name": "test_item",
        "price": 1000,
        "statistics": {
            "likes": 1,
            "viewCount": 1,
            "contacts": 1
        }
    }

    post_url = base_url + post_resource
    with allure.step("Отправка POST запроса на создание объявления"):
        result_post_1 = requests.post(post_url, json=json_for_item)
        print(result_post_1.text)
        result_post_2 = requests.post(post_url, json=json_for_item)
        print(result_post_2.text)

    token_1 = result_post_1.json()
    token_2 = result_post_2.json()


    with allure.step("Проверка статус кода"):
        assert result_post_1.status_code == 200, "ОШИБКА, статус-код в 1 запросе не соответствует."
        assert result_post_2.status_code == 200, "ОШИБКА, статус-код в 2 запросе не соответствует."
        print(f"Статус-код 1 и 2 объявления: {result_post_1.status_code}.")


    with allure.step("Проверка наличия поля status"):
        assert "status" in token_1, "ОШИБКА, поля status в 1 запросе нет"
        assert "status" in token_2, "ОШИБКА, поля status в 2 запросе нет"
        print("Поле status есть.")

    with allure.step("Проверка наличия UUID идентификатора в поле status"):
        item_id_1 = token_1["status"].split(" - ")[-1]
        item_id_2 = token_2["status"].split(" - ")[-1]
        try:
            uuid.UUID(item_id_1)
            uuid.UUID(item_id_2)
        except ValueError:
            assert False, "ОШИБКА, 1 id не соответствует формату UUID"

        print(f'ID соответствуют формату UUID')


    with allure.step("Проверка идемпотентности"):
        assert item_id_1 != item_id_2, "ОШИБКА, создано 2 одинаковых ID подряд"
        print("Созданы 2 объявления с разными id")


@allure.title("Получение объявления по id (e2e)")
@allure.description("Проверка создания объявления и последующего получения его по id с валидацией данных")
def test_create_and_check_item():
    """Tест-кейс №4. Получение объявления по валидному id (e2e)"""

    print("\nTест-кейс №4")
    post_resource = "/api/1/item"
    seller_id = random.randint(111111, 999999)
    name = "test_item"
    price = 1000
    json_for_item = {
        "sellerID": seller_id,
        "name": name,
        "price": price,
        "statistics": {
            "likes": 1,
            "viewCount": 1,
            "contacts": 1
        }
    }

    post_url = base_url + post_resource
    with allure.step("Отправка POST запроса на создание объявления"):
        result_post = requests.post(post_url, json=json_for_item)
        print(result_post.text)
        post_token = result_post.json()

    with allure.step("Проверка статус кода"):
        assert result_post.status_code == 200, "ОШИБКА, статус-код создания объявления не соответствует."
        print(f"Статус-код: {result_post.status_code}.")

    with allure.step("Проверка соответствия формата id"):
        try:
            item_id = post_token["status"].split(" - ")[-1]
            uuid.UUID(item_id)
        except ValueError:
            assert False, "ОШИБКА, id не соответствует формату UUID"



    # Отправка GET запроса
    get_resource = "/api/1/item/"
    item_id = post_token["status"].split(" - ")[-1]
    get_url = base_url + get_resource + item_id
    print(f"Ссылка: {get_url}")

    with allure.step("Отправка GET запроса"):
        result_get = requests.get(get_url)
        print(result_get.text)
        get_token = result_get.json()[0]

    with allure.step("Проверка статус кода"):
        assert result_get.status_code == 200, "ОШИБКА, статус-код не соответствует."
        print(f"Статус-код: {result_get.status_code}.")

    with allure.step("Проверка соответствия значения id"):
        assert get_token["id"] == item_id, "ОШИБКА, id из запроса не соответствует id из ответа"
        print("ID соответствует")

    with allure.step("Проверка соответствия значения name"):
        assert get_token["name"] == name, "ОШИБКА, name из запроса не соответствует id из ответа"
        print("name соответствует")

    with allure.step("Проверка соответствия значения price"):
        assert get_token["price"] == price, "ОШИБКА, price из запроса не соответствует id из ответа"
        print("price соответствует")


@allure.title("Получение объявления по несуществующему id")
@allure.description("Проверка ошибки при запросе объявления с несуществующим UUID идентификатором")
def test_get_item_with_incorrect_uuid_id():
    """Tест-кейс №5. Получение объявления по несуществующему id в формате uuid"""

    print("\nTест-кейс №5")
    get_resource = "/api/1/item/"
    random_uuid_id = str(uuid.uuid4())

    get_url_uuid = base_url + get_resource + random_uuid_id
    print(f"Ссылка: {get_url_uuid}")

    with allure.step("Отправка GET запроса на получение объявления по id"):
        req_uuid = requests.get(get_url_uuid)
        print(req_uuid.text)
        token = req_uuid.json()

    with allure.step("Проверка статус кода"):
        assert req_uuid.status_code == 404, "ОШИБКА, статус-код не соответствует."
        print(f"Статус-код: {req_uuid.status_code}.")


    with allure.step("Проверка наличия поля result и наличия message внутри result"):
        assert "result" in token, "ОШИБКА, поля result нет"
        assert "message" in token["result"], "ОШИБКА, поля message нет"
        print("Поле message внутри ответа (внутри поля result есть)")


    with allure.step('Проверка наличия текст "not found" в поле message'):
        message_text = token["result"]["message"]
        assert f"not found" in message_text, 'ОШИБКА, ответ в поле message не содержит "not found"'
        print('Текст "not found" в поле message есть.')


@allure.title("Получение объявлений продавца")
@allure.description("Проверка получения списка объявлений по sellerId после создания нескольких объявлений")
def test_get_items_by_seller_id():
    """Tест-кейс №6. Получение объявлений продавца (e2e)"""

    print("\nTест-кейс №6")

    post_resource = "/api/1/item"
    seller_id = random.randint(111111, 999999)

    # Данные для двух объявлений
    json_for_item_1 = {
        "sellerID": seller_id,
        "name": "item_1",
        "price": 1000,
        "statistics": {
            "likes": 1,
            "viewCount": 1,
            "contacts": 1
        }
    }

    json_for_item_2 = {
        "sellerID": seller_id,
        "name": "item_2",
        "price": 2000,
        "statistics": {
            "likes": 2,
            "viewCount": 2,
            "contacts": 2
        }
    }

    post_url = base_url + post_resource

    with allure.step("Отправка POST запроса на создание объявления"):
        result_post_1 = requests.post(post_url, json=json_for_item_1)
        print(result_post_1.text)

        result_post_2 = requests.post(post_url, json=json_for_item_2)
        print(result_post_2.text)

    with allure.step("Проверка статус кода"):
        assert result_post_1.status_code == 200, "ОШИБКА, статус-код в 1 запросе не соответствует."
        assert result_post_2.status_code == 200, "ОШИБКА, статус-код в 2 запросе не соответствует."
        print("Оба объявления созданы")

    # GET запрос по sellerId
    get_resource = f"/api/1/{seller_id}/item"
    get_url = base_url + get_resource
    print(f"Ссылка: {get_url}")

    with allure.step("Отправка GET запроса на получение объявлений продавца"):
            result_get = requests.get(get_url)
            print(result_get.text)

    with allure.step("Проверка статус кода"):
        assert result_get.status_code == 200, "ОШИБКА, статус-код не соответствует"
        print(f"Статус-код: {result_get.status_code}")

    items = result_get.json()

    with allure.step("Проверка, что ответ список"):
        assert isinstance(items, list), "ОШИБКА, ответ не список"
        assert len(items) >= 2, "ОШИБКА, вернулось меньше 2 объявлений"
        print("Список объявлений получен")


    with allure.step("Проверка sellerId у всех объявлений"):
        for item in items:
            assert item["sellerId"] == seller_id, "ОШИБКА, sellerId не совпадает"
        print("Все объявления принадлежат нужному sellerId")


@allure.title("Получение статистики объявления")
@allure.description("Проверка получения статистики объявления и корректности структуры и типов данных")
def test_get_item_statistics():
    """Tест-кейс №7. Получение статистики по объявлению (e2e)"""

    print("\nTест-кейс №7")

    post_resource = "/api/1/item"
    seller_id = random.randint(111111, 999999)

    json_for_item = {
        "sellerID": seller_id,
        "name": "stat_item",
        "price": 1500,
        "statistics": {
            "likes": 5,
            "viewCount": 10,
            "contacts": 3
        }
    }

    post_url = base_url + post_resource
    with allure.step("Отправка POST запроса на создание объявления"):
        result_post = requests.post(post_url, json=json_for_item)
        print(result_post.text)

    with allure.step("Проверка статус кода"):
        assert result_post.status_code == 200, "ОШИБКА, статус-код создания объявления не соответствует."
        print("Объявление создано")

    post_token = result_post.json()

    with allure.step("Проверка формата ID"):
        try:
            item_id = post_token["status"].split(" - ")[-1]
            uuid.UUID(item_id)
        except ValueError:
            assert False, "ОШИБКА, id не соответствует формату UUID"

        print(f"ID: {item_id}")

    # GET статистики
    get_resource = f"/api/1/statistic/{item_id}"
    get_url = base_url + get_resource
    print(f"Ссылка: {get_url}")

    with allure.step("GET запрос на получение статистики"):
        result_get = requests.get(get_url)
        print(result_get.text)

    with allure.step("Проверка статус кода"):
        assert result_get.status_code == 200, "ОШИБКА, статус-код не соответствует"
        print(f"Статус-код: {result_get.status_code}")

    stats = result_get.json()[0]


    with allure.step("Проверка наличия полей"):
        assert "likes" in stats, "ОШИБКА, нет поля likes"
        assert "viewCount" in stats, "ОШИБКА, нет поля viewCount"
        assert "contacts" in stats, "ОШИБКА, нет поля contacts"
        print("Все поля статистики присутствуют")


    with allure.step("Проверка типов"):
        assert isinstance(stats["likes"], int), "ОШИБКА, likes не int"
        assert isinstance(stats["viewCount"], int), "ОШИБКА, viewCount не int"
        assert isinstance(stats["contacts"], int), "ОШИБКА, contacts не int"
        print("Типы данных корректны")


@allure.title("Проверка времени ответа при получении статистики")
@allure.description("Проверка, что время ответа API при получении статистики не превышает допустимое значение")
def test_statistic_response_time():
    """Tест-кейс №8. Проверка времени ответа API при получении статистики (e2e)"""

    print("\nTест-кейс №8")

    post_resource = "/api/1/item"
    seller_id = random.randint(111111, 999999)

    json_for_item = {
        "sellerID": seller_id,
        "name": "perf_item",
        "price": 1000,
        "statistics": {
            "likes": 1,
            "viewCount": 1,
            "contacts": 1
        }
    }

    post_url = base_url + post_resource
    with allure.step("Отправка POST запроса на создание объявления"):
        result_post = requests.post(post_url, json=json_for_item)
        print(result_post.text)

    with allure.step("Проверка статус кода"):
        assert result_post.status_code == 200, "ОШИБКА, статус-код не соответствует."
        print(f"Статус-код: {result_post.status_code}")

    post_token = result_post.json()
    item_id = post_token["status"].split(" - ")[-1]

    get_resource = f"/api/1/statistic/{item_id}"
    get_url = base_url + get_resource

    start_time = time.time()
    result_get = requests.get(get_url)
    end_time = time.time()

    response_time = end_time - start_time
    print(f"Время ответа: {response_time}")

    with allure.step("Проверка статус кода"):
        assert result_get.status_code == 200, "ОШИБКА, статус-код не соответствует"

    with allure.step("Проверка времени ответа"):
        assert response_time < 1, "ОШИБКА, время ответа превышает 1 секунду"
        print("Время ответа до 1 секунды")


@allure.title("Проверка формата ответа API")
@allure.description("Проверка, что ответ API приходит в формате JSON и содержит корректный Content-Type")
def test_create_item_response_format():
    """Tест-кейс №9. Проверка формата ответа API (POST)"""

    print("\nTест-кейс №9")

    post_resource = "/api/1/item"
    seller_id = random.randint(111111, 999999)

    json_for_item = {
        "sellerID": seller_id,
        "name": "format_item",
        "price": 1000,
        "statistics": {
            "likes": 1,
            "viewCount": 1,
            "contacts": 1
        }
    }

    post_url = base_url + post_resource
    with allure.step("Отправка POST запроса на создание объявления"):
        result_post = requests.post(post_url, json=json_for_item)
        print(result_post.text)

    with allure.step("Проверка статус кода"):
        assert result_post.status_code == 200, "ОШИБКА, статус-код не соответствует"
        print(f"Статус-код: {result_post.status_code}")


    with allure.step("Проверка Content-Type"):
        content_type = result_post.headers.get("Content-Type")
        assert "application/json" in content_type, "ОШИБКА, неверный Content-Type"
        print(f"Content-Type корректный: {content_type}")


    with allure.step("Проверка, что это JSON"):
        try:
            token = result_post.json()
        except:
            assert False, "ОШИБКА, ответ не является JSON"

        print("Ответ в формате JSON")


    with allure.step("Проверка структуры ответа"):
        assert "status" in token, "ОШИБКА, нет поля status"
        print("Поле status есть")


@allure.title("Создание объявления с отрицательной ценой")
@allure.description("Проверка валидации поля price: отрицательное значение не должно приниматься системой")
def test_create_item_price_boundary():
    """Tест-кейс №10. Проверка граничных значений price"""

    print("\nTест-кейс №10")

    post_resource = "/api/1/item"
    seller_id = random.randint(111111, 999999)

    # Набор тестовых значений
    test_prices = [-1, 0]

    for price in test_prices:
        print(f"\nПроверка price = {price}")

        json_for_item = {
            "sellerID": seller_id,
            "name": "boundary_item",
            "price": price,
            "statistics": {
                "likes": 1,
                "viewCount": 1,
                "contacts": 1
            }
        }

        post_url = base_url + post_resource
        with allure.step("Отправка POST запроса на создание объявления"):
            result_post = requests.post(post_url, json=json_for_item)
            print(result_post.text)

        with allure.step("Проверка статус кода"):
            assert result_post.status_code == 400, f"ОШИБКА, price={price} не должен быть допустим"
            print(f"price={price} корректно отклонён")




