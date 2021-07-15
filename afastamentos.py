from src.funcoes import *
from src.conexao import *
from datetime import timedelta
from os import path

#Busca afastamentos concomitantes
def afastamentos():
    concomitantes = open(path.dirname(path.realpath(__file__)) + "\src\sql\\afastamentos_concomitantes.sql", "a")
    
    lista_funcionario = consultar(
        """
            SELECT 
                i_funcionarios,
                i_entidades
            FROM  
                bethadba.funcionarios;
        """
    )

    for i in lista_funcionario:
        funcionario = i[0]
        entidade  = i[1]

        tem_rescisao = False

        resultado = consultar(
            """
                SELECT data_inicial, data_final, i_entidades, i_funcionarios, tabela FROM (
                    SELECT dt_afastamento AS data_inicial, dt_ultimo_dia AS data_final, i_entidades, i_funcionarios, 'afastamentos' AS tabela FROM bethadba.afastamentos WHERE i_funcionarios = {0} AND i_entidades = {1} AND i_tipos_afast NOT IN (7, 8)
                    
                    UNION ALL
                    
                    SELECT dt_gozo_ini AS data_inicial, dt_gozo_fin AS data_final, i_entidades, i_funcionarios, 'ferias' AS tabela FROM bethadba.ferias WHERE i_funcionarios = {0} AND i_entidades = {1}
                    
                    UNION ALL
                    
                    SELECT ISNULL(dt_aviso, dt_rescisao) AS  data_inicial, dt_rescisao AS data_final, i_entidades, i_funcionarios, 'rescisoes' AS tabela FROM bethadba.rescisoes WHERE i_funcionarios = {0} AND i_entidades = {1}
                ) AS a ORDER BY data_inicial, data_final DESC;
            """.format(funcionario, entidade)
        )

        dt_final_anterior = ""
        dt_inicial_anterior = ""
        tabela_anterior = ""
    
        for index, j in enumerate(resultado):
            dt_inicial = j[0]
            dt_final = j[1]
            tabela = j[4]

            if index == 0:
                tabela_anterior = tabela
                dt_inicial_anterior = dt_inicial
                dt_final_anterior = dt_final
                continue
        
            if dt_inicial_anterior >= dt_inicial:

                if tabela_anterior == "afastamentos":

                    u = "UPDATE bethadba.afastamentos SET dt_ultimo_dia = '{}' WHERE dt_afastamento = '{}' AND i_entidades = {} AND i_funcionarios = {};".format((dt_inicial - timedelta(days = 1)), dt_inicial_anterior, entidade, funcionario)
                    
                    concomitantes.writelines(u + "\n")

                elif tabela_anterior == "ferias" and tabela == "afastamentos":

                    u = "UPDATE bethadba.afastamentos SET dt_afastamento = '{}' WHERE dt_afastamento = '{}' AND i_entidades = {} AND i_funcionarios = {};".format((dt_final_anterior + timedelta(days = 1)), dt_inicial, entidade, funcionario)
                    
                    concomitantes.writelines(u + "\n")
                          
                else:

                    if tabela_anterior == 'rescisoes' and tabela == 'rescisoes':
                        continue

                    print("Update manual: Verificar o incidente!")
                    print(funcionario)
                    print(entidade)
                    print(dt_inicial_anterior)
                    print(dt_final_anterior)
                    print("===")

            if tabela == 'rescisoes':
                tem_rescisao = True

            tabela_anterior = tabela
            dt_inicial_anterior = dt_inicial
            dt_final_anterior = dt_final   

        if tem_rescisao and resultado[len(resultado)-1][4] != 'rescisoes':
            
            print("Update manual: afastamentos ou ferias posteriores a rescisão!")
            print(funcionario)
            print(entidade)
            print(dt_inicial)
            print(dt_final)
            print("===")

afastamentos()