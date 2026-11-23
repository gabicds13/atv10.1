"""Exercício 10.1: cliente-servidor com Flask + Cosmos DB for MongoDB."""
import math
import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pymongo.errors import PyMongoError

from . import repositorio_mongo as repositorio

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app = Flask(__name__)

origens = os.environ.get("CORS_ORIGINS", "*")
CORS(app, resources={r"/*": {"origins": origens if origens == "*" else [o.strip() for o in origens.split(",")]}})


@app.errorhandler(repositorio.BancoNaoConfigurado)
def erro_configuracao(_erro):
    return jsonify({"erro": "Banco de dados não configurado. Defina COSMOS_MONGO_URI no servidor."}), 503


@app.errorhandler(PyMongoError)
def erro_banco(_erro):
    # Não divulga senhas ou a URI de conexão ao navegador.
    app.logger.exception("Falha ao acessar o catálogo no banco MongoDB")
    return jsonify({"erro": "Banco indisponível. Confira a conexão e as permissões da Azure."}), 503


@app.get("/")
def pagina_inicial():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/script.js")
def js():
    return send_from_directory(FRONTEND_DIR, "script.js")


@app.get("/style.css")
def css():
    return send_from_directory(FRONTEND_DIR, "style.css")


@app.get("/api")
def informacoes():
    return jsonify({"mensagem": "API da Livraria - Exercício 10.1", "banco": "Cosmos DB for MongoDB", "rotas": ["GET /livros", "GET /livros/<id>", "POST /livros", "DELETE /livros/<id>", "GET /health"]})


@app.get("/health")
def health():
    quantidade = repositorio.testar_conexao()
    return jsonify({"status": "ok", "banco": "conectado", "livros": quantidade})


@app.get("/livros")
def listar_livros():
    return jsonify(repositorio.listar_livros()), 200


@app.get("/livros/<livro_id>")
def consultar_livro(livro_id):
    livro = repositorio.consultar_livro(livro_id)
    if livro is None:
        return jsonify({"erro": "Livro não encontrado."}), 404
    return jsonify(livro), 200


@app.post("/livros")
def cadastrar_livro():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie os dados em JSON."}), 400
    titulo = dados.get("titulo")
    autor = dados.get("autor")
    if not isinstance(titulo, str) or not titulo.strip() or not isinstance(autor, str) or not autor.strip():
        return jsonify({"erro": "Informe título e autor válidos."}), 400
    if len(titulo.strip()) > 120 or len(autor.strip()) > 120:
        return jsonify({"erro": "Título e autor devem ter até 120 caracteres."}), 400
    try:
        # bool é um subtipo de int em Python, mas não representa preço.
        if isinstance(dados.get("preco"), bool):
            raise ValueError
        preco = float(dados.get("preco"))
    except (TypeError, ValueError):
        return jsonify({"erro": "O preço deve ser um número válido."}), 400
    if not math.isfinite(preco) or preco < 0:
        return jsonify({"erro": "O preço deve ser finito e não negativo."}), 400

    livro = repositorio.cadastrar_livro(titulo.strip(), autor.strip(), round(preco, 2))
    return jsonify(livro), 201


@app.delete("/livros/<livro_id>")
def excluir_livro(livro_id):
    if not repositorio.excluir_livro(livro_id):
        return jsonify({"erro": "Livro não encontrado."}), 404
    return jsonify({"mensagem": "Livro excluído com sucesso."}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
