#### Address already in use
- Endereço em uso
- No terminal da pasta (onde está o código):
```shell
lsof -i :8000 # vai dar informações do processo que está aberto
```
- Na segunda coluna vamos ter o valor do PID e vamos usar esse valor para "matar" o processo atual:
```shell
kill -9 <PID>
# exemplo: kill -9 12345
```
- Rodar novamente o servidor utilizando o uvicorn:
```shell
uvicorn fast_zero.app:app --reload
```