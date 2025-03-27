import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home_page():
    return "<h1>Seja Bem-vindo(a)</h1>"

def init_db():
    with sqlite3.connect("database.db") as conn:
        conn.execute(
            """
                CREATE TABLE IF NOT EXISTS livros(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    autor TEXT NOT NULL,
                    imagem_url TEXT NOT NULL            
                )
            """
    )

init_db()

@app.route("/doar", methods=["POST"])
def doar():
    dados = request.get_json()

    titulo = dados.get("titulo")
    categoria = dados.get("categoria")
    autor = dados.get("autor")
    imagem_url = dados.get("imagem_url")

    if not titulo or not categoria or not autor or not imagem_url:
        return jsonify({"Erro": "Todos os campos são obrigatórios"}), 400
    
    with sqlite3.connect("database.db") as conn:
        conn.execute(f"""
            INSERT INTO livros (titulo, categoria, autor, imagem_url) VALUES ("{titulo}", "{categoria}", "{autor}", "{imagem_url}")
        """)

        conn.commit()

        return jsonify({"mensagem": "Livro cadastrado com sucesso!"}, 201)
    
@app.route("/livros", methods=["GET"])
def busca_livros():
    with sqlite3.connect("database.db") as conn:
        livros = conn.execute("SELECT * FROM livros").fetchall()

        livros_formatados = []

        for item in livros:
            dicio_livros = {
                "id": item[0],
                "titulo": item[1],
                "categoria": item[2],
                "autor": item[3],
                "imagem_url": item[4]
            }

            livros_formatados.append(dicio_livros)

    return jsonify(livros_formatados), 200

if __name__ == "__main__":
    app.run(debug=True)
