import os
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "aula_prova")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "123456")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))

def get_conn():
  return psycopg2.connect(
    host=DB_HOST,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    port=DB_PORT
  )

@app.route("/", methods=["GET"])
def health():
  return "Aplicação Flask no Docker – Prova de DevOps", 200

@app.route("/produtos", methods=["GET"])
def listar_produtos():
  with get_conn() as conn:
    with conn.cursor() as cur:
      cur.execute("SELECT id, nome, preco FROM produtos ORDER BY id;")
      rows = cur.fetchall()
      return jsonify([{"id": r[0], "nome": r[1], "preco": float(r[2])} for r in rows]), 200

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
