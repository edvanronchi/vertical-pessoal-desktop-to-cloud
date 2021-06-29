import pyodbc
from variaveis import *

conexao = pyodbc.connect(f'DSN={odbc}', ConnectionIdleTimeout=0)
cursor = conexao.cursor()

#Pesquisar dados.
def consultar(comando: str) -> list:
    cursor.execute(comando)
    linha  = cursor.fetchall()

    return linha

#Executa ações de atualizar, deletar, inserir dados desabilitando os gatilhos.
def executar(comando: str):

    if bethadba:
        cursor.execute(
            """
                CALL bethadba.dbp_conn_gera(1, 2021, 300);
                set option wait_for_commit = 'on';
                set option fire_triggers = 'off';
                {}
                COMMIT; 
                set option fire_triggers = 'on';
            """.format(comando)
        )

        return
    
    cursor.execute(
        """
            CALL bethadba.dbp_conn_gera(1, 2021, 300);
            set option wait_for_commit = 'on';
            CALL bethadba.pg_habilitartriggers('off'); 
            {}
            COMMIT; 
            CALL bethadba.pg_habilitartriggers('on');   
        """.format(comando)
    )