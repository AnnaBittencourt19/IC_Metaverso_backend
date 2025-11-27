- Os testes devem ficar dentro de uma pasta chamada tests e começar ou terminar com  ``test_`` ou  ``_test.py``
- As funções dentro do arquivo .py devem começar com ``test_``
### Estrutura de um teste
- Primeiro para termos o teste precisamos ter o arquivo principal
- Depois criamos o código de teste que possui a seguinte estrutura:
```python
from http import HTTPStatus # simplificar o status 200 para HHTPStatus.OK
from fastapi.testclient import TestClient # Ele simula um postman para fazer as requisições sem precisar rodar o servidor de verdade
from fast_zero.app import app # importa o nosso arquivo principal o alvo (fast_zero/app.py)

def test_root_retornar_ola_mundo():
	client = TestClient(app) # Estamos ligando o nosso simulador/robô
	response = client.get('/') # Essa parte é o ACT ele manda o client acessar a rota raiz usando o metodo GET, é a mesma coisa de abrir a raíz no navegador, toda a resposta do navegador será salva no response (status, texto, cabeçalho)
	assert response.status_code == HTTPStatus.OK # Esse é o Assert ele vai testar que o servidor devolveu o código 200, caso devolva 404 ou 500 o teste vai falhar aqui (primeira verificação)
	assert response.json() == {'message': 'Olá Mundo!'} # Testa se o servidor retornou Olá Mundo! a resposta deve ser EXATAMENTE essa caso contrário o teste falha aqui
```

### Resumindo: 
- Os testes importam nosso código original (tem acesso a ele), com isso podemos criar uma função para testar as funcionalidades do nosso servidor/aplicação (essa função deve se chamar test_objetivo), nessa função chamamos o nosso TestClient(app) que é o comando que liga o robô/simulador (o nosso teste será rodado pelo client), depois temos uma ACT que é aquilo que o robô deve fazer/acessar no caso acima usamos um get na raíz do nosso servidor (isso significa que a variavel que armazena o client.get vai armazenar todas as informações que um GET passaria para o navegador), já na parte de assert é como se fosse um if/else(a diferença é que no assert não existe o else, caso a condição não seja satisfeita o código para), no exemplo acima estamos testando duas coisas se o servidor retornou o status 200 e se ele retornou a mensagem desejada
- Arrange (client) -> Act (o que o client vai fazer/testar) -> Assert (o que vai ser conferido) (Essa estrutura fica dentro da função)

