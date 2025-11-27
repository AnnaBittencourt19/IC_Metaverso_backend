1. No terminal pipx e proetry: (Instalação pipx e poetry)
```shell
annabittencourt@MacBook-Air-de-Anna api % pip install --user pipx

Requirement already satisfied: pipx in /Users/annabittencourt/Library/Python/3.13/lib/python/site-packages (1.8.0)

Requirement already satisfied: argcomplete>=1.9.4 in /Users/annabittencourt/Library/Python/3.13/lib/python/site-packages (from pipx) (3.6.3)

Requirement already satisfied: packaging>=20 in /Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages (from pipx) (24.2)

Requirement already satisfied: platformdirs>=2.1 in /Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages (from pipx) (4.4.0)

Requirement already satisfied: userpath!=1.9,>=1.6 in /Users/annabittencourt/Library/Python/3.13/lib/python/site-packages (from pipx) (1.9.2)

Requirement already satisfied: click in /Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages (from userpath!=1.9,>=1.6->pipx) (8.2.1)

annabittencourt@MacBook-Air-de-Anna api % pipx ensurepath

/Users/annabittencourt/.local/bin is already in PATH.

/Users/annabittencourt/Library/Python/3.13/bin is already in PATH.

  

⚠️  All pipx binary directories have been appended to PATH. If you are sure

you want to proceed, try again with the '--force' flag.

  

Otherwise pipx is ready to go! ✨ 🌟 ✨

annabittencourt@MacBook-Air-de-Anna api % pipx list

venvs are in **/Users/annabittencourt/.local/pipx/venvs**

apps are exposed on your $PATH at **/Users/annabittencourt/.local/bin**

manual pages are exposed at **/Users/annabittencourt/.local/share/man**

   package **poetry** **2.2.1**, installed using Python 3.13.7

    - poetry

annabittencourt@MacBook-Air-de-Anna api % pipx inject poetry poetry-plugin-shell 

⚠️ poetry-plugin-shell already seems to be injected in 'poetry'. Not modifying

existing installation in '/Users/annabittencourt/.local/pipx/venvs/poetry'.

Pass '--force' to force installation.

```
	 - Por que? O pipx é um jeito seguro de fazer instalações globais no computador (o Poetry é uma instalação global que poderá ser usada em todos os projetos que eu desejar uma vez que ele seja instalado no computador), já o poetry ele é para dependências do projeto em si, é basicamente um ambiente virtual do proprio projeto (as instalações de ferramentas ficam isoladas pelo poetry), ele cria a padronização do projeto (o que vamos fazer em breve) e nessa padronização temos um arquivo que se chama poetry.lock nele dica as bibliotecas usadas e suas versões caso alguem baixe o projeto terá um ambiente igual ao que criei

2. Criando o projeto: (pasta padrão do poetry)
```shell
annabittencourt@MacBook-Air-de-Anna app % poetry new --flat app
```
	- Esse comando criou a seguinte estrutura:
	annabittencourt@MacBook-Air-de-Anna app % ls app 
	pyproject.toml README.md tests
	(criou a estrutura básica)
	
3. Instalação do FastAPI:
``` shell
poetry install 
poetry add 'fastapi[standard]'
```
	-poetry install adiciona pyproject.tom e poetry add vai adicionar o fastapi no nosso ambiente virtual do projeto atual

4. Definindo a versão do python que será usada no projeto:
```shell
annabittencourt@MacBook-Air-de-Anna app % poetry env use 3.14        

```

5. Mudar a versão do python no .toml:
```toml
requires-python = ">=3.14,<4.0"
```

6. Adicionar as ferramentas básicas: (de boas práticas/teste):
```shell
annabittencourt@MacBook-Air-de-Anna app % poetry add --group dev pytest pytest-cov taskipy ruff
```

7. Configurando essas ferramentas no toml: (Para mais informações: [[6. Configurando as ferramentas de desenvolvimento]])
```toml
[tool.ruff]
line-length = 79
extend-exclude = ['migrations']

[tool.ruff.lint]
preview = true
select = ['I', 'F', 'E', 'W', 'PL', 'PT']

[tool.ruff.format] 
preview = true 
quote-style = 'single'

[tool.pytest.ini_options]
pythonpath = "."
addopts = '-p no:warnings'

[tool.taskipy.tasks] 
lint = 'ruff check' 
pre_format = 'ruff check --fix' 
format = 'ruff format'
run = 'fastapi dev fast_zero/app.py'
pre_test = 'task lint' 
test = 'pytest -s -x --cov=fast_zero -vv' 
post_test = 'coverage html'