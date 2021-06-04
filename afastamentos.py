from src.functions import *
from src.database import *
from datetime import timedelta
from os import path

#Busca afastamentos concomitantes
def afastamentos():
    afastamentosConcomitantes = open(path.dirname(path.realpath(__file__)) + "\src\sql\\afastamentos_concomitantes.sql", "a")
    
    idFuncionarios = select(
        """
            SELECT 
                i_funcionarios
            FROM  
                bethadba.funcionarios;
        """
    )

    for i in idFuncionarios:
        idFuncionario = i[0]

        temRescisao = False

        resultado = select(
            """
                SELECT data_inicial, data_final, i_entidades, i_funcionarios, tabela FROM (
                    SELECT dt_afastamento AS data_inicial, dt_ultimo_dia AS data_final, i_entidades, i_funcionarios, 'afastamentos' AS tabela FROM bethadba.afastamentos WHERE i_funcionarios = {0} AND i_tipos_afast NOT IN (7, 8)
                    
                    UNION ALL
                    
                    SELECT dt_gozo_ini AS data_inicial, dt_gozo_fin AS data_final, i_entidades, i_funcionarios, 'ferias' AS tabela FROM bethadba.ferias WHERE i_funcionarios = {0}
                    
                    UNION ALL
                    
                    SELECT ISNULL(dt_aviso, dt_rescisao) AS  data_inicial, dt_rescisao AS data_final, i_entidades, i_funcionarios, 'rescisoes' AS tabela FROM bethadba.rescisoes WHERE i_funcionarios = {0}
                ) AS a ORDER BY data_inicial, data_final DESC;
            """.format(idFuncionario)
        )

        dataFinalAnterior = ""
        dataInicialAnterior = ""
        tabelaAnterior = ""
    
        for index, j in enumerate(resultado):
            dataInicial = j[0]
            dataFinal = j[1]
            idEntidade = j[2]
            tabela = j[4]

            if index == 0:
                tabelaAnterior = tabela
                dataInicialAnterior = dataInicial
                dataFinalAnterior = dataFinal
                continue

            if dataFinalAnterior >= dataInicial:

                if tabelaAnterior == "afastamentos":

                    u = "UPDATE bethadba.afastamentos SET dt_ultimo_dia = '{}' WHERE dt_afastamento = '{}' AND i_entidades = {} AND i_funcionarios = {};".format((dataInicial - timedelta(days = 1)), dataInicialAnterior, idEntidade, idFuncionario)

                    afastamentosConcomitantes.writelines(u)

                elif tabelaAnterior == "ferias" and tabela == "afastamentos":

                    u = "UPDATE bethadba.afastamentos SET dt_afastamento = '{}' WHERE dt_afastamento = '{}' AND i_entidades = {} AND i_funcionarios = {};".format((dataFinalAnterior + timedelta(days = 1)), dataInicial, idEntidade, idFuncionario)

                    afastamentosConcomitantes.writelines(u)
                          
                else:
                    print("Update manual: Verificar o incidente!")
                    print(idFuncionario)
                    print(dataInicialAnterior)
                    print(dataFinalAnterior)
                    print("===")

            if tabela == 'rescisoes':
                temRescisao = True

            tabelaAnterior = tabela
            dataInicialAnterior = dataInicial
            dataFinalAnterior = dataFinal   

        if temRescisao and resultado[len(resultado)-1][4] != 'rescisoes':
            
            print("Update manual: afastamentos ou ferias posteriores a rescisão!")
            print(idFuncionario)
            print(dataInicial)
            print(dataFinal)
            print("===")

#--------------------Executar-------------------------#
afastamentos()