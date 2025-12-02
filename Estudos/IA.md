### [Building and evaluating multilingual RAG systems](https://medium.com/data-science-at-microsoft/building-and-evaluating-multilingual-rag-systems-943c290ab711)

**Sugestões de LLMs multilingues:** paraphrase-multilingual-MiniLM-L12-v2 (mais leve e carrega rápido, melhor opção), LaBSE (mais pesado e é a qualidade é maior que do paraphrase) e mE5-base (é mais moderno, intermediario e a qualidade de inglês é melhor que o miniLM)
- Primeira parte para um sistema RAG multilingue: indexação e recuperação (retrieval), segundo: geração 
- No projeto não poderá ser usado um modelo monolingue, um modelo monolingue tem os documentos de base em um único idioma (os artigos são em inglês) e as entradas e saídas são nesse mesmo idioma dos documentos. A maioria dos LLMs disponíveis mesmo que sejam multilingue são treinados predominantemente em inglês
- Multilíngue: Consultar em idiomas diferentes e esperar uma resposta com o idioma de entrada e os documentos podem estar em diferentes idiomas também, porém em alguns casos pode ser necessário adicionar uma etapa de tradução e deve-se ter muito cuidado com erros de tradução
#### Introdução
- Busca semântica: Na busca semântica os documentos da base de conhecimento são divididos em blocos, que se tornam pesquisáveis por palavra-chave ou por representação vetorial semântica(podendo ser similaridade de cosseno), recupera k documentos mais relevantes (k é definido por nós)

query → embedding → FAISS → docs → prompt → LLM → resposta

![[Captura de Tela 2025-12-01 às 11.02.46.png]] ```A imagem representa um sistema que possui uma entrada, uma base de dados e a resposta em alemão e em inglês, no projeto de IA do XGMobile será em português/inglês```

- Query: Input do usuário é multilingue, é a entrada do usuário (vai ser convertida em uma lista de vetores (os embeddings))
#### Etapa de indexação e retrieval


