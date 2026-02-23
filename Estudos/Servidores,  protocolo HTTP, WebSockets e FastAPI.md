# Fundamentos web e arquitetura cliente-servidor
Um servidor é um programa que fica 24h escutando portas TCP/UDP
### **O paradigma cliente-servidor**
A internet utiliza o modelo arquitetural cliente-servidor. Onde o cliente é aquele que faz um requerimento/solicitação, já o servidor recebe essa solicitação, interpreta, executa o que deve ser executado e devolve as informações depois de processadas (ele aguarda a chegada das requisições)
Tem uma analogia muito boa sobre essa dinamica cliente-servidor utilizando um restaurante como exemplo: O cliente é o freguês do restaurante analisando o cardápio e decidindo o que vai pedir, a requisição é o pedido anotado e levado pra cozinha, a cozinha é o servidor que faz o prato que o cliente pediu e o prato finalizado é a resposta do servidor que é entregue ao cliente após o processamento do pedido
Existe todo um processo "debaixo dos panos" que vai do usuário digitar o DNS, esse DNS ser transformado em IP, o protocolo TCP/IP estabelecer uma rota até o servidor....
O que o servidor faz? Ele possui dados e os recursos, funciona através de uma API. Apenas processa a lógica e responde para o cliente
O que o cliente faz? Envia uma pergunta para o endereço /ws, é a interface (web, mobile, etc) e consome os serviços oferecidos pelo servidor 
### **Protocolo HTTP**
O HTTP é o idioma da camada 7 do modelo OSI (camada de aplicação)
O HTTP é um protocolo sem estado, ou seja, cada requisição é tratada como um evento isolado, não retém memória e cada requisição é tratada de modo isolado. HTTP é como se fosse o idioma entre o cliente e o servidor. O cliente faz o request ao servidor, podendo ser do tipo GET (GET é tipo falar: Eu quero) e o servidor se tudo der certo retorna com o que o cliente solicitou e com o código 200
### **Protocolo WebSocket**
Diferenças entre HTTP e o WebSocket: O HTTP funciona como uma Walkie-Talkie onde um lado aperta o botão, fala (envia requisição), solta o botão e o outro lado processa aperta o botão e responde (não é possível que os dois lados se comuniquem ao mesmo tempo). Já o WebSocket opera como um telefone fixo, uma vez que a chamada é atendida a linha permanece aberta, ambos os lados podem falar ao mesmo tempo e se escutar e não há necessidade de discar o número a cada nova frase. 

|                   | Arquitetura HTTP (REST)                                          | Arquitetura WebSocket                                                              |
| ----------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Padrão de conexão | Uma nova conexão para cada requisição e encerra após a resposta. | Uma única conexão estabelecida no início mantida viva até o encerramento explícito |
| Direcionalidade   | Unidirecional. Apenas o cliente inicia a conversa                | Bidimencional                                                                      |
| Comunicação       | Síncrona                                                         | Assíncrona                                                                         |
O WebSocket usa um processo chamado handshake para estabelecer a conexão
### Comunicação síncrona vs. assíncrona 
Na comunicação síncrona, quem faz a requisição(cliente) fica parado esperando a resposta antes de continuar e na comunicação assíncrona quem faz a requisição não fica parado ele pode continuar executando outras tarefas enquanto a resposta não chega
No sincrono cada pergunta congela o servidor e gera e fila (atrasos) e no assincrono o servidor delega tarefas. Exemplo:
![[assincrono.png]]
Lida com várias tarefas ao mesmo tempo, alternando entre elas (aproveita tempo de espera do usuario A para começar a processar o B)bolo e 