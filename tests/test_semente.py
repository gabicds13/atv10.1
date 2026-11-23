import unittest
from backend.repositorio_mongo import inserir_livros_iniciais

class FakeResultado:
    def __init__(self, upserted_id):
        self.upserted_id = upserted_id

class FakeColecao:
    def __init__(self):
        self.docs={}
    def update_one(self, filtro, operacao, upsert=False):
        id=filtro['_id']
        if id in self.docs:
            return FakeResultado(None)
        self.docs[id]=dict(operacao['$setOnInsert'])
        return FakeResultado(id)

class TestSemente(unittest.TestCase):
    def test_10_sem_duplicatas(self):
        colecao=FakeColecao()
        self.assertEqual(inserir_livros_iniciais(colecao),10)
        self.assertEqual(inserir_livros_iniciais(colecao),0)
        self.assertEqual(len(colecao.docs),10)

if __name__=='__main__':
    unittest.main()
