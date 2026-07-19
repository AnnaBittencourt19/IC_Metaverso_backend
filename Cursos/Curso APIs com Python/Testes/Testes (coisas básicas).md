- Testes automatizados são códigos que escrevemos para verificar que o código original está correto 
- O pytest procura automaticamente por arquivos que começam com ``test_`` ou terminam com  ``_test``
### Por que testar?
- Os testes são feitos para evitar a regressão (consertar uma coisa e estragar outra)
### A hierarquia dos testes
- Teste Unitário: Testam uma única função ou classe (de forma isolada)
- Teste de integração: Testam se duas partes conversam bem. (ex. API com o BD)
### A estrutura AAA
- AAA: Arrange, Act e Assert

1. Arrange(Preparar): Criar os dados necessários
2. Act(Agir): Chamar a função que quer testar 
3. Assert(Verificar): Validar a resposta esperada