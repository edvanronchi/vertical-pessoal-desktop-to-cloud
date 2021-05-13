import pyodbc

#Nome da conexão via ODBC
database = 'folha_sao_ludgero_pm_oficial'

cnxn = pyodbc.connect(f'DSN={database}', ConnectionIdleTimeout=0)
cursor = cnxn.cursor()

#Pesquisar dados
def select(query: str) -> list:
    cursor.execute(query)
    row  = cursor.fetchall()

    return row

#Atualizar, deletar, inserir dados
def updateInsertDelete(query: str, fire: bool = False):

    if fire:
        cursor.execute(
            """
                CALL bethadba.pg_setoption('fire_triggers','off');
                {}
                COMMIT; 
                CALL bethadba.pg_setoption('fire_triggers','on');
            """.format(query)
        )

        return
    
    cursor.execute(
        """
            CALL bethadba.dbp_conn_gera(1, 2021, 300);
            CALL bethadba.pg_setoption('wait_for_commit','on');
            CALL bethadba.pg_habilitartriggers('off'); 
            {}
            COMMIT; 
            CALL bethadba.pg_habilitartriggers('on');   
        """.format(query)
    )