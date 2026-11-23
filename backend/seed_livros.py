"""Executar uma única vez (ou repetir com segurança): python -m backend.seed_livros."""
from .repositorio_mongo import obter_colecao, inserir_livros_iniciais


def main():
    # obter_colecao já pode semear automaticamente; a segunda tentativa não duplica.
    colecao = obter_colecao()
    adicionais = inserir_livros_iniciais(colecao)
    total = colecao.count_documents({})
    print(f"Catálogo sincronizado. Novos livros nesta execução: {adicionais}. Total no banco: {total}.")
    if total < 10:
        raise SystemExit("O catálogo ainda tem menos de 10 livros.")


if __name__ == "__main__":
    main()
