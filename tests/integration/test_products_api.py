import sqlite3
import threading
import pytest
import requests
from werkzeug.serving import make_server
from my_app.app import create_app


@pytest.fixture(scope="function")
def db_connection():
    """Створює таблицю products у тестовій БД SQLite в пам'яті та видаляє її після тесту."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
        """
    )
    conn.commit()

    yield conn

    cursor.execute("DROP TABLE IF EXISTS products")
    conn.commit()
    conn.close()


@pytest.fixture(scope="function")
def base_url(db_connection):
    """Запускає тестовий HTTP-сервер Flask на вільному порту для requests."""
    app = create_app(db_conn=db_connection)
    server = make_server("127.0.0.1", 0, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    yield f"http://127.0.0.1:{server.server_port}"

    server.shutdown()
    thread.join(timeout=2)


def test_create_and_get_product(base_url):
    """Сценарій: Створення та отримання товару (POST -> 201, GET -> 200)."""
    payload = {"name": "Laptop", "price": 1500}
    create_resp = requests.post(f"{base_url}/api/products", json=payload, timeout=5)

    assert create_resp.status_code == 201, "POST /api/products має повертати 201 Created"
    created_data = create_resp.json()
    assert "id" in created_data, "Відповідь має містити ідентифікатор id створеного товару"
    assert created_data["name"] == "Laptop"
    assert created_data["price"] == 1500

    product_id = created_data["id"]
    get_resp = requests.get(f"{base_url}/api/products/{product_id}", timeout=5)

    assert get_resp.status_code == 200, "GET /api/products/{id} має повертати 200 OK"
    fetched_data = get_resp.json()
    assert fetched_data["id"] == product_id
    assert fetched_data["name"] == payload["name"]
    assert fetched_data["price"] == payload["price"]


def test_update_product(base_url):
    """Сценарій: Оновлення товару (PUT -> 200, повторний GET перевіряє нову ціну)."""
    create_resp = requests.post(
        f"{base_url}/api/products",
        json={"name": "Laptop", "price": 1500},
        timeout=5,
    )
    product_id = create_resp.json()["id"]

    update_resp = requests.put(
        f"{base_url}/api/products/{product_id}",
        json={"price": 1450},
        timeout=5,
    )
    assert update_resp.status_code == 200, "PUT /api/products/{id} має повертати 200 OK"

    get_resp = requests.get(f"{base_url}/api/products/{product_id}", timeout=5)
    assert get_resp.status_code == 200
    assert get_resp.json()["price"] == 1450, "Ціна товару після оновлення має дорівнювати 1450"


def test_delete_product(base_url):
    """Сценарій: Видалення товару (DELETE -> 204, повторний GET -> 404)."""
    create_resp = requests.post(
        f"{base_url}/api/products",
        json={"name": "Laptop", "price": 1500},
        timeout=5,
    )
    product_id = create_resp.json()["id"]

    delete_resp = requests.delete(f"{base_url}/api/products/{product_id}", timeout=5)
    assert delete_resp.status_code == 204, "DELETE /api/products/{id} має повертати 204 No Content"

    get_resp = requests.get(f"{base_url}/api/products/{product_id}", timeout=5)
    assert get_resp.status_code == 404, "GET видаленого товару має повертати 404 Not Found"

def test_list_products_and_validation_errors(base_url):
    """Перевірка отримання списку товарів та валідації некоректних даних (400 Bad Request)."""
    # Створення двох товарів
    requests.post(f"{base_url}/api/products", json={"name": "Mouse", "price": 50}, timeout=5)
    requests.post(f"{base_url}/api/products", json={"name": "Keyboard", "price": 120}, timeout=5)

    list_resp = requests.get(f"{base_url}/api/products", timeout=5)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 2, "GET /api/products має повертати список усіх товарів"

    # Некоректні дані при POST (400)
    bad_name_resp = requests.post(f"{base_url}/api/products", json={"name": "", "price": 100}, timeout=5)
    assert bad_name_resp.status_code == 400

    bad_price_resp = requests.post(f"{base_url}/api/products", json={"name": "Monitor", "price": -10}, timeout=5)
    assert bad_price_resp.status_code == 400


def test_update_and_delete_nonexistent_product(base_url):
    """Перевірка обробки 404 та 400 при оновленні та видаленні товарів."""
    # Спроба оновити та видалити неіснуючий товар (404)
    put_missing = requests.put(f"{base_url}/api/products/999", json={"price": 500}, timeout=5)
    assert put_missing.status_code == 404

    del_missing = requests.delete(f"{base_url}/api/products/999", timeout=5)
    assert del_missing.status_code == 404

    # Некоректні дані при PUT (400)
    created = requests.post(f"{base_url}/api/products", json={"name": "Desk", "price": 300}, timeout=5).json()
    pid = created["id"]

    bad_put_name = requests.put(f"{base_url}/api/products/{pid}", json={"name": ""}, timeout=5)
    assert bad_put_name.status_code == 400

    bad_put_price = requests.put(f"{base_url}/api/products/{pid}", json={"price": -5}, timeout=5)
    assert bad_put_price.status_code == 400


def test_create_app_default_db(tmp_path, monkeypatch):
    """Перевірка ініціалізації додатку зі стандартною БД за замовчуванням."""
    monkeypatch.chdir(tmp_path)
    app = create_app()
    client = app.test_client()
    resp = client.get("/api/products")
    assert resp.status_code == 200
    assert resp.get_json() == []
