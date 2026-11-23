"""Repositório do catálogo em Azure Cosmos DB for MongoDB (driver PyMongo).

A credencial vem exclusivamente de variável de ambiente. Nenhuma conexão é
criada no momento do import, facilitando testes e inicialização no App Service.
"""

import os
from functools import lru_cache
from uuid import uuid4

from pymongo import MongoClient

from .livros_iniciais import LIVROS_INICIAIS


class BancoNaoConfigurado(RuntimeError):
    """A URI privada do MongoDB ainda não foi configurada."""


def inserir_livros_iniciais(colecao):
    """Cria os dez livros de demonstração sem duplicar nem alterar os existentes."""
    inseridos = 0
    for livro in LIVROS_INICIAIS:
        resultado = colecao.update_one(
            {"_id": livro["_id"]},
            {"$setOnInsert": livro},
            upsert=True,
        )
        if resultado.upserted_id is not None:
            inseridos += 1
    return inseridos


@lru_cache(maxsize=1)
def obter_colecao():
    uri = os.environ.get("COSMOS_MONGO_URI", "").strip()
    if not uri:
        raise BancoNaoConfigurado(
            "A variável COSMOS_MONGO_URI não foi configurada no servidor."
        )

    banco = os.environ.get("COSMOS_DB_NAME", "livraria_exercicio10")
    colecao_nome = os.environ.get("COSMOS_COLLECTION_NAME", "livros")

    # A própria URI fornecida pela Azure especifica autenticação e TLS.
    # Não desabilitar validação de certificados TLS.
    cliente = MongoClient(uri, serverSelectionTimeoutMS=6000, connectTimeoutMS=6000)
    cliente.admin.command("ping")
    colecao = cliente[banco][colecao_nome]

    # Idempotente: a primeira visita cria os 10 registros de exemplo.
    if os.environ.get("SEED_DEMO_BOOKS", "true").lower() in ("true", "1", "yes"):
        inserir_livros_iniciais(colecao)

    return colecao


def converter_livro(documento):
    return {
        "id": str(documento["_id"]),
        "titulo": documento["titulo"],
        "autor": documento["autor"],
        "preco": float(documento["preco"]),
    }


def listar_livros():
    livros = [converter_livro(d) for d in obter_colecao().find({})]
    return sorted(livros, key=lambda livro: livro["titulo"].casefold())


def consultar_livro(livro_id):
    doc = obter_colecao().find_one({"_id": livro_id})
    return converter_livro(doc) if doc is not None else None


def cadastrar_livro(titulo, autor, preco):
    doc = {"_id": str(uuid4()), "titulo": titulo, "autor": autor, "preco": preco}
    obter_colecao().insert_one(doc)
    return converter_livro(doc)


def excluir_livro(livro_id):
    return obter_colecao().delete_one({"_id": livro_id}).deleted_count > 0


def testar_conexao():
    # Contagem real, útil para verificar se há no mínimo 10 livros no banco.
    return obter_colecao().count_documents({})
