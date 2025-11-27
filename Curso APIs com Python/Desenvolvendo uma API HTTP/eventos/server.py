from http.server import HTTPServer, BaseHTTPRequestHandler
from evento_online import EventoOnline 
from evento import Evento 
import json

ev_online = EventoOnline("Live de Python")
ev2_online = EventoOnline("Live de JavaScript")
ev = Evento("Aula de Python", "Rio de Janeiro")
eventos = [ev_online, ev2_online, ev] 

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/": 
            print ("Recebida uma requisição GET")
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8") 
            self.end_headers() 
            data = f"""
            <html>
                <head>
                    <title>Servidor HTTP Simples</title>
                </head>
                <body>
                    <h1>Olá, mundo!</h1>
                    <p> Diretorio: {self.path} </p>
                </body>
            </html>
            """.encode()
            self.wfile.write(data) 

        elif self.path == "/eventos": 
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers() 
            
            eventos_html = "" 

            for ev in eventos: 
                eventos_html += f"""
                    <tr>
                        <td> {ev.id} </td>
                        <td> {ev.nome} </td>
                        <td> {ev.local} </td>
                    </tr>
                """
            data = f""" 
            <html>
                <table>
                    <tr>
                        <th> ID </th>
                        <th> Nome </th>
                        <th> Local </th>
                    </tr>
            {eventos_html} 
            </html>
            """.encode()
            self.wfile.write(data)

        elif self.path == "/api/eventos": #caminho que diz que é uma API então os dados serão retornados em JSON, esses arquivos servem para comunicação entre sistemas
            self.send_response(200)
            self.send_header("Content-type", "text/json; charset=utf-8") #text/json indica que o conteúdo é JSON
            self.end_headers() 
            
            #Montar o json:
            lista_eventos = []
            for ev in eventos:
               lista_eventos.append({ # append adiciona um elemento a lista
                    "id": ev.id,
                    "nome": ev.nome,
                    "local": ev.local
               }) #criando um dicionário para cada evento e adicionando na lista 

               data = json.dumps(lista_eventos).encode() #transforma a lista em uma string no formato JSON e em bytes, para enviar pela rede
               self.wfile.write(data)
server = HTTPServer(('localhost', 8000), SimpleHandler)
server.serve_forever() 

# em mais ferramentas no chrome -> Ferramentas do desenvolvedor -> aba Network -> clicar na requisição feita para /api/eventos
#webframeworks facilitam a criação de APIs REST, esse servidor HTTP simples é apenas para fins didáticos e não é o recomendado para projetos 
# API REST por padrão retorna dados em JSON