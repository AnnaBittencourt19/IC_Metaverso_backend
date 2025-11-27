from evento import Evento
from evento_online import EventoOnline

ev_online = EventoOnline("Live de Python")
ev2_online = EventoOnline("Live de JavaScript")

print(ev_online.imprime_informacoes())
print(ev2_online.imprime_informacoes())
print(type(ev_online.imprime_informacoes()))

ev = Evento("Aula de Python", "Rio de Janeiro")

# Evento e EventoOnline podem ser usados aqui normalmente
# Porém não podemos importar EventoOnline em evento.py para evitar importação circular