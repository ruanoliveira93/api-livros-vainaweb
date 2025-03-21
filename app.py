from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Criando conexão sem database primeiro
db = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASS')
)

cursor = db.cursor()

# Criando banco de dados, se não existir
cursor.execute("CREATE DATABASE IF NOT EXISTS livros_vai_na_web")
db.close()  # Fechamos para reconectar já dentro do banco

# Conecta-se ao banco de dados
db = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASS'),
    database=os.getenv('DB_NAME')
)

cursor = db.cursor()

# Criando a tabela livros, caso não exista
cursor.execute("""
    CREATE TABLE IF NOT EXISTS livros (
        id INT AUTO_INCREMENT PRIMARY KEY,
        titulo TEXT NOT NULL,
        categoria TEXT NOT NULL,
        autor TEXT NOT NULL,
        imagem_url TEXT NOT NULL,
        publicado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
print("Banco de dados e tabela criados com sucesso!")

cursor.close()

app = Flask(__name__)
CORS(app)

# Rota doar para adicionar livros ao banco de dados
@app.route('/doar', methods=['POST'])
def doar_livro():
    data = request.get_json()
    print(f"AQUI ESTÃO OS DADOS RETORNADOS DO CLIENTE {data}")

    titulo = data.get('titulo')
    categoria = data.get('categoria')
    autor = data.get('autor')
    imagem_url = data.get('imagem_url')

    if not titulo or not categoria or not autor or not imagem_url:
        return jsonify({"erro": "Todos os campos são obrigatórios!"}), 400

    try:
        db = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME')
        )
        cursor = db.cursor()

        sql = "INSERT INTO livros (titulo, categoria, autor, imagem_url) VALUES (%s, %s, %s, %s)"
        valores = (titulo, categoria, autor, imagem_url)

        cursor.execute(sql, valores)
        db.commit()

        return jsonify({"mensagem": "Livro cadastrado com sucesso!"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        cursor.close()
        db.close()

# Rota doar para buscar livros no banco de dados
@app.route('/livros', methods=['GET'])
def load_livros():
    cursor = None
    db = None
    try:
        db = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME')
        )
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM livros")
        livros = cursor.fetchall()
        return jsonify(livros)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()


# Rota doar para deletar livro por ID
@app.route('/doar/<int:id>', methods=["DELETE"])
def del_item(id):
    try:
        db = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME')
        )
        cursor = db.cursor()

        # Verifica se o livro existe antes de deletar
        cursor.execute("SELECT * FROM livros WHERE id = %s", (id,))
        livro = cursor.fetchone()

        if not livro:
            return jsonify({"erro": "Livro não encontrado"}), 404

        cursor.execute("DELETE FROM livros WHERE id = %s", (id,))
        db.commit()

        return jsonify({"mensagem": f"Livro com ID {id} deletado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        cursor.close()
        db.close()


if __name__ == "__main__":
    app.run(debug=True)
