### [Um guia para iniciantes sobre como construir um aplicativo de Geração Aumentada por Recuperação (RAG) do zero.](https://learnbybuilding.ai/tutorial/rag-from-scratch/)
- Rag de um jeito bem simples:
![[Captura de Tela 2025-12-10 às 13.10.03.png]]
Um guia para iniciantes sobre como construir um aplicativo de Geração Aumentada por Recuperação (RAG) do zero.
- Tudo que é preciso para o RAG:
	- Coleção de documentos(Corpus)
	- O input do usuario
	- Uma medida de similaridade entre os documentos e o input
- Passos de um sistema RAG:
	1. Receber um input
	2. Realizar a busca por similaridade
	3. Processar os documentos obtidos e a entrada obtida

Um RAG funciona basicamente assim:
É um modelo que recebe uma pergunta, procura sobre ela em documentos relevantes (recupera k documentos relevantes isso, geralmente definimos k como 3) e usa esses documentos para gerar uma resposta. Possui a combinação de dois componentes:
	- Retriever (não paramétrico): Encontra documentos relevantes
	- Generator (paramétrico): Usa os documentos para gerar a resposta final
O sistema primeiro recebe uma consulta (query) e precisa processar essa consulta, depois de receber essa consulta o sistema pega essa consulta e o vetoriza (pode ter outros processos antes disso como o chunking), logo após a vetorização vai para o retriever (nesse processo o sistema procura os documentos onde o vetor é mais parecido com a entrada do usuario), os documentos encontrados no retriever são enviados para o generator que cria uma resposta para a consulta com base em cada documento relevante e depois essas respostas geradas passam pelo processo de marginalização (combinar as respostas)
