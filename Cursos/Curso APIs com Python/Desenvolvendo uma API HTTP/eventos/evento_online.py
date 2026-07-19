import json # Json já está disponível na biblioteca padrão do Python
from evento import Evento

class EventoOnline(Evento):
    def __init__(self, nome, _=""):
        local = f"https://tamercado.com/eventos?id={EventoOnline.id}"
        super().__init__(nome, local)

    def imprime_informacoes(self):
        return json.dumps({ #dumps transforma um dicionário em uma string no formato JSON
            "ID do evento": self.id,
            "Nome do evento": self.nome,
            "Local do evento": self.local   
        })