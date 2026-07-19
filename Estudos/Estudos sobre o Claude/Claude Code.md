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
- Documento ```claude.md```: 