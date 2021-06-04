import pyodbc
from variaveis import *

cnxn = pyodbc.connect(f'DSN={database}', ConnectionIdleTimeout=0)
cursor = cnxn.cursor()

#Pesquisar dados
def select(query: str) -> list:
    cursor.execute(query)
    row  = cursor.fetchall()

    return row

#Atualizar, deletar, inserir dados
def updateInsertDelete(query: str):

    if bethaDBA:
        cursor.execute(
            """
                CALL bethadba.dbp_conn_gera(1, 2021, 300);
                set option wait_for_commit = 'on';
                set option fire_triggers = 'off';
                {}
                COMMIT; 
                set option fire_triggers = 'on';
            """.format(query)
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
        """.format(query)
    )