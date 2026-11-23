"""Testes com fake de repositório: executam sem uma conta Azure real."""
import unittest
from unittest.mock import patch

from backend.app import app
from backend.livros_iniciais import LIVROS_INICIAIS


class TestLivrariaAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_livros_iniciais_tem_10_ids_unicos(self):
        self.assertEqual(len(LIVROS_INICIAIS), 10)
        self.assertEqual(len({livro["_id"] for livro in LIVROS_INICIAIS}), 10)

    @patch("backend.app.repositorio.listar_livros", return_value=[
        {"id": "livro-001", "titulo": "Dom Casmurro", "autor": "Machado de Assis", "preco": 29.90}
    ])
    def test_listagem(self, _mock):
        response = self.client.get("/livros")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)

    @patch("backend.app.repositorio.cadastrar_livro", return_value={
        "id": "novo-123", "titulo": "Novo", "autor": "Pessoa", "preco": 20.0
    })
    def test_cadastro(self, mock_cadastrar):
        response = self.client.post("/livros", json={"titulo": "Novo", "autor": "Pessoa", "preco": 20})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["id"], "novo-123")
        mock_cadastrar.assert_called_once_with("Novo", "Pessoa", 20.0)

    def test_nao_aceita_preco_invalido(self):
        response = self.client.post("/livros", json={"titulo": "X", "autor": "Y", "preco": -1})
        self.assertEqual(response.status_code, 400)

    @patch("backend.app.repositorio.excluir_livro", return_value=True)
    def test_exclusao(self, mock_excluir):
        response = self.client.delete("/livros/novo-123")
        self.assertEqual(response.status_code, 200)
        mock_excluir.assert_called_once_with("novo-123")

    @patch("backend.app.repositorio.excluir_livro", return_value=False)
    def test_exclusao_inexistente(self, _mock):
        response = self.client.delete("/livros/nao-existe")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
