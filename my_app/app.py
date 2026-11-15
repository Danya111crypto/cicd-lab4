import sqlite3
from flask import Flask, jsonify, request


def create_app(db_conn=None):
    app = Flask(__name__)

    if db_conn is None:
        db_conn = sqlite3.connect("products.db", check_same_thread=False)
        db_conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
            """
        )
        db_conn.commit()

    app.config["DB_CONN"] = db_conn

    @app.route("/api/products", methods=["POST"])
    def create_product():
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        price = data.get("price")

        if not name or not isinstance(name, str):
            return jsonify({"error": "Invalid product name"}), 400
        if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
            return jsonify({"error": "Invalid product price"}), 400

        conn = app.config["DB_CONN"]
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price) VALUES (?, ?)",
            (name, float(price)),
        )
        conn.commit()
        product_id = cursor.lastrowid

        return jsonify({"id": product_id, "name": name, "price": price}), 201

    @app.route("/api/products", methods=["GET"])
    def list_products():
        conn = app.config["DB_CONN"]
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price FROM products")
        rows = cursor.fetchall()
        products = [{"id": r[0], "name": r[1], "price": r[2]} for r in rows]
        return jsonify(products), 200

    @app.route("/api/products/<int:product_id>", methods=["GET"])
    def get_product(product_id):
        conn = app.config["DB_CONN"]
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, price FROM products WHERE id = ?",
            (product_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return jsonify({"error": "Product not found"}), 404

        return jsonify({"id": row[0], "name": row[1], "price": row[2]}), 200

    @app.route("/api/products/<int:product_id>", methods=["PUT"])
    def update_product(product_id):
        conn = app.config["DB_CONN"]
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, price FROM products WHERE id = ?",
            (product_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return jsonify({"error": "Product not found"}), 404

        data = request.get_json(silent=True) or {}
        new_name = data.get("name", row[1])
        new_price = data.get("price", row[2])

        if not new_name or not isinstance(new_name, str):
            return jsonify({"error": "Invalid product name"}), 400
        if isinstance(new_price, bool) or not isinstance(new_price, (int, float)) or new_price < 0:
            return jsonify({"error": "Invalid product price"}), 400

        cursor.execute(
            "UPDATE products SET name = ?, price = ? WHERE id = ?",
            (new_name, float(new_price), product_id),
        )
        conn.commit()

        return jsonify({"id": product_id, "name": new_name, "price": new_price}), 200

    @app.route("/api/products/<int:product_id>", methods=["DELETE"])
    def delete_product(product_id):
        conn = app.config["DB_CONN"]
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
        if cursor.fetchone() is None:
            return jsonify({"error": "Product not found"}), 404

        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        return "", 204

    return app
