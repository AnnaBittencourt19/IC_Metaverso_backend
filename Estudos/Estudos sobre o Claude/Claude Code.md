- Roda no terminal e no aplicativo do claude
- Terminal instala no próprio terminal com o código: (MAC)
	```shell
	curl -fsSL https://claude.ai/install.sh | bash
	```
### Configurar
```shell
claude
```
- Escolhe tema, entra na conta
### No terminal ![[Captura de Tela 2026-07-19 às 13.45.46.png]]
```/model``` : Escolhe o modelo
```Tab + shift``` : Muda o tipo que vai funcionar:
	- Manual: Claude pede aprovação antes de cada edição de arquivo ou comando. Mais seguro, ideal para código sensível (auth, billing, migrations) ou quando você quer revisar tudo passo a passo
	- Accept edits: Claude aplica as edições de arquivo automaticamente, sem pedir confirmação a cada uma. Bom para tarefas repetitivas ou de baixo risco, quando você já confia na direção do trabalho.
	- Plan mode: Modo somente leitura: Claude explora o código, pesquisa e propõe um plano completo, mas não edita nem executa nada até você aprovar. Ideal para entender o escopo antes de mexer refactors grandes, código desconhecido, ou mudanças que tocam vários arquivos.
	- Auto mode: modo mais recente e avançado; deixa Claude decidir e executar com mais autonomia (incluindo aprovações), pensado para sessões mais longas e automatizadas. É mais "hands-off" que o accept edits
	- Plan mode primeiro para entender o código
- Para usar o claude code (terminal) em alguma pasta especifica, ir nela e clicar com o botão direito do mouse e depois abrir terminal na pasta, e escrever claude
- ```/compact```: Analisa a conversa toda, mantém as informações mais importantes (para diminuir o tamanho do contexto)
- ```/clear```: Começar uma nova conversa/sessão
- ```/resume```: Ver históricos de conversa
- Documento ```claude.md```: Arquivo que contém informações sobre os meus objetivos, sobre a minha estrutura de pastas, sobre os meus documentos, informações relevantes para o claude quando ele abre aquela pasta. Existem dois níveis:
	- Primeiro nível: O que está na pasta do projeto que vai ser aberto
	- Segundo nível: Oculta na pasta .claude na pasta raíz do usuário (é carregado em todas as pastas)
	- Primeiro nível é como se fosse um prompt injetado naquela pasta e o segundo nível injetado em todas 
	- O comando ```/init``` inicializa o arquivo claude.md de maneira automática 
- Protocolo de MCPs: Permite conectar com outras ferramentas (ex; gmail, calendário, notion, figma...)
	- Excaldraw: Fazer desenhos, planejar melhor (mockup)
- ```@```: Marcar uma pasta
- Claude é muito bom para fazer dashboards
- Skills: Arquivo markdown que instrui o claude a fazer alguma coisa e diz quando o claude deve usar ele, só lê a skill quando acha que ela tem haver com o contexto. Pode ser criado a mão ou usar skills prontas na internet. Colar link e pedir para baixar a skill
- Sub Agents: Pede pra ele usar uma skill e em paralelo suba N sub Agents para trabalhar em paralelo
