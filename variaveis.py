import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(join(dirname(__file__), '.env'))

#Variaveis globais
entidade = os.environ.get("ENTIDADE")    
lista_entidade = os.environ.get("LISTA_ENTIDADE")

#Nome da conexão ODBC
odbc = os.environ.get("ODBC")

#Utilização do BETHADBA
bethadba = os.environ.get("BETHADBA")

#Id do vinculo empregaticio
vinculo_empregaticio_autonomo = os.environ.get("VINCULO_EMPREGATICIO_AUTONOMO")
vinculo_empregaticio_autonomo_conselheiro = os.environ.get("VINCULO_EMPREGATICIO_AUTONOMO_CONSELHEIRO")

#Fechar as folhas de pagamentos com data anterior a data especificada
folha_fechamento_competencia = os.environ.get("FOLHA_FECHAMENTO_COMPETENCIA")