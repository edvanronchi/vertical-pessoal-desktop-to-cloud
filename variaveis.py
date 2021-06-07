import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

#Variaveis globais
idEntidadePrincipal = os.environ.get("ID_ENTIDADE_PRINCIPAL")    
idEntidadesAgrupadas = os.environ.get("ID_ENTIDADE_AGRUPADAS")

#Nome da conexão via ODBC
database = os.environ.get("DATABASE")

#Utilização do bethaD BA
bethaDBA = os.environ.get("BETHADBA")

#Fechar as folhas de pagamentos com data anterior a data especificada
competenciaFechamentoFolha = os.environ.get("COMPETENCIA_FECHAMENTO_FOLHA")