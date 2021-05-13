from variavel_global import *
from src.functions import *
from src.database import *
from os import path

unificarGeral1 = open(path.dirname(path.realpath(__file__)) + "\src\sql\\unificar_geral_1.sql", "a")
unificarGeral2 = open(path.dirname(path.realpath(__file__)) + "\src\sql\\unificar_geral_2.sql", "a")

desabilitarTriggers = "CALL bethadba.dbp_conn_gera(1, 2021, 300);\nCALL bethadba.pg_setoption('wait_for_commit','on');\nCALL bethadba.pg_habilitartriggers('off');\n\n"

unificarGeral1.writelines(desabilitarTriggers)
unificarGeral2.writelines(desabilitarTriggers)

def unificarFuncionarios(idEntidadesAgrupadas):
    unificar1 = open(path.dirname(path.realpath(__file__)) + "\src\sql\\unificar_funcionarios_1.sql", "a")
    unificar2 = open(path.dirname(path.realpath(__file__)) + "\src\sql\\unificar_funcionarios_2.sql", "a")
    
    unificar1.writelines(desabilitarTriggers)
    unificar2.writelines(desabilitarTriggers)

    resultado = select(
        """
            SELECT 
                list(i_entidades), 
                i_funcionarios, 
                count(*) AS quantidade 
            FROM 
                bethadba.funcionarios 
            WHERE
                i_entidades IN {}    
            GROUP BY 
                i_funcionarios 
            HAVING 
                quantidade > 1 
            ORDER BY 
                i_funcionarios   
        """.format(idEntidadesAgrupadas)
    )

    tabelas = tabelaColuna(['i_entidades', 'i_funcionarios'])

    idMax = select("SELECT (MAX(i_funcionarios)+1) AS id FROM bethadba.funcionarios")[0][0]

    for i in resultado:
        idsEntidade = i[0].split(',')

        identificador = i[1]

        for index, idEntidade in enumerate(idsEntidade):

            if index == 0:
                continue

            querys = ""

            for tabela in tabelas:
                
                u = "UPDATE bethadba.{} SET i_funcionarios = {} WHERE i_funcionarios = {} AND i_entidades = {};\n".format(tabela, idMax, identificador, idEntidade)

                if tabela in tabelasSemPermissoes:
                    unificar2.writelines(u)
                    unificarGeral2.writelines(u)                   
                    continue

                querys += u
            
            querys += "\n"

            unificar1.writelines(querys)
            unificarGeral1.writelines(querys)

            idMax += 1

    print("Código SQL gerado para tabela: funcionarios!")

def unificarCargos(idEntidadesAgrupadas):
    unificar1 = open(path.dirname(path.realpath(__file__)) + "\src\sql\\unificar_cargos_1.sql", "a")

    unificar1.writelines(desabilitarTriggers)

    resultado = select(
        """
           SELECT 
                list(i_entidades), 
                i_cargos, 
                count(*) AS quantidade 
            FROM 
                bethadba.cargos 
            WHERE
                i_entidades IN {}
            GROUP BY 
                i_cargos 
            HAVING 
                quantidade > 1 
            ORDER BY 
                i_cargos   
        """.format(idEntidadesAgrupadas)
    )

    tabelas = tabelaColuna(['i_entidades', 'i_cargos'])

    idMax = select("SELECT (MAX(i_cargos)+1) AS id FROM bethadba.cargos")[0][0]

    for i in resultado:
        idsEntidade = i[0].split(',')

        identificador = i[1]

        for index, idEntidade in enumerate(idsEntidade):

            if index == 0:
                continue      
            
            querys = ""

            for tabela in tabelas:
          
                u = "UPDATE bethadba.{} SET i_cargos = {} WHERE i_cargos = {} AND i_entidades = {};\n".format(tabela, idMax, identificador, idEntidade)

                querys += u
            
            querys += "\n"

            unificar1.writelines(querys)
            unificarGeral1.writelines(querys)

            idMax += 1

    print("Código SQL gerado para tabela: cargos")

def unificarPeriodosTrab(idEntidadesAgrupadas):
    unificar1 = open(path.dirname(path.realpath(__file__)) + "\src\sql\\unificar_periodos_trab_1.sql", "a")

    unificar1.writelines(desabilitarTriggers)

    resultado = select(
        """
            SELECT 
                list(i_entidades), 
                i_periodos_trab, 
                count(*) AS quantidade 
            FROM
                bethadba.periodos_trab 
            WHERE
                i_entidades IN {}
            GROUP BY 
                i_periodos_trab 
            HAVING 
                quantidade > 1 
            ORDER BY 
                i_periodos_trab    
        """.format(idEntidadesAgrupadas)
    )

    tabelas = tabelaColuna(['i_entidades', 'i_periodos_trab'])

    idMax = select("SELECT (MAX(i_periodos_trab)+1) AS id FROM bethadba.periodos_trab")[0][0]

    for i in resultado:
        idsEntidade = i[0].split(',')

        identificador = i[1]

        for index, idEntidade in enumerate(idsEntidade):

            if index == 0:
                continue      
            
            querys = ""

            for tabela in tabelas:
          
                u = "UPDATE bethadba.{} SET i_periodos_trab = {} WHERE i_periodos_trab = {} AND i_entidades = {};\n".format(tabela, idMax, identificador, idEntidade)

                querys += u
            
            querys += "\n"

            unificar1.writelines(querys)
            unificarGeral1.writelines(querys)

            idMax += 1

    print("Código SQL gerado para tabela: periodos_trab")

def unificarTurmas(idEntidadesAgrupadas):
    unificar1 = open(path.dirname(path.realpath(__file__)) + "\src\sql\\unificar_turmas_1.sql", "a")

    unificar1.writelines(desabilitarTriggers)

    resultado = select(
        """
            SELECT 
                list(i_entidades), 
                i_turmas, 
                count(*) AS quantidade 
            FROM 
                bethadba.turmas 
            WHERE
                i_entidades IN {}
            GROUP BY 
                i_turmas 
            HAVING 
                quantidade > 1 
            ORDER BY 
                i_turmas      
        """.format(idEntidadesAgrupadas)
    )

    tabelas = tabelaColuna(['i_entidades', 'i_turmas'])

    idMax = select("SELECT (MAX(i_turmas)+1) AS id FROM bethadba.turmas")[0][0]

    for i in resultado:
        idsEntidade = i[0].split(',')

        identificador = i[1]

        for index, idEntidade in enumerate(idsEntidade):

            if index == 0:
                continue      
            
            querys = ""

            for tabela in tabelas:
          
                u = "UPDATE bethadba.{} SET i_turmas = {} WHERE i_turmas = {} AND i_entidades = {};\n".format(tabela, idMax, identificador, idEntidade)

                querys += u
            
            querys += "\n"

            unificar1.writelines(querys)
            unificarGeral1.writelines(querys)

            idMax += 1

    print("Código SQL gerado para tabela: turmas")

def unificarDespesas(idEntidadesAgrupadas):
    unificar1 = open(path.dirname(path.realpath(__file__)) + "\src\sql\\unificar_despesas_1.sql", "a")

    unificar1.writelines(desabilitarTriggers)

    resultado = select(
        """
            SELECT 
                list(i_entidades), 
                i_despesas, 
                ano_exerc, 
                count(*) AS quantidade 
            FROM 
                bethadba.despesas 
            WHERE
                i_entidades IN {}
            GROUP BY 
                i_despesas,
                ano_exerc
            HAVING 
                quantidade > 1 
            ORDER BY 
                i_despesas  
        """.format(idEntidadesAgrupadas)
    )

    tabelas = tabelaColuna(['i_entidades', 'i_despesas', 'ano_exerc'])

    idMax = select("SELECT (MAX(i_despesas)+1) AS id FROM bethadba.despesas")[0][0]

    for i in resultado:
        idsEntidade = i[0].split(',')

        identificador = i[1]
        anoExercicio = i[2]

        for index, idEntidade in enumerate(idsEntidade):

            if index == 0:
                continue      
            
            querys = ""

            for tabela in tabelas:
          
                u = "UPDATE bethadba.{} SET i_despesas = {} WHERE i_despesas = {} AND i_entidades = {} AND ano_exerc = {};\n".format(tabela, idMax, identificador, idEntidade, anoExercicio)

                querys += u
            
            querys += "\n"

            unificar1.writelines(querys)
            unificarGeral1.writelines(querys)

            idMax += 1

    print("Código SQL gerado para tabela: despesas")

def unificarNiveis(idEntidadesAgrupadas):
    unificar1 = open(path.dirname(path.realpath(__file__)) + "\src\sql\\unificar_niveis_1.sql", "a")

    unificar1.writelines(desabilitarTriggers)

    resultado = select(
        """
            SELECT 
                list(i_entidades), 
                i_niveis, 
                count(*) AS quantidade 
            FROM 
                bethadba.níveis 
            WHERE
                i_entidades IN {}
            GROUP BY 
                i_niveis 
            HAVING 
                quantidade > 1 
            ORDER BY 
                i_niveis      
        """.format(idEntidadesAgrupadas)
    )

    tabelas = tabelaColuna(['i_entidades', 'i_niveis'])

    idMax = select("SELECT (MAX(i_niveis)+1) AS id FROM bethadba.niveis")[0][0]

    for i in resultado:
        idsEntidade = i[0].split(',')

        identificador = i[1]

        for index, idEntidade in enumerate(idsEntidade):

            if index == 0:
                continue      
            
            querys = ""

            for tabela in tabelas:
          
                u = "UPDATE bethadba.{} SET i_niveis = {} WHERE i_niveis = {} AND i_entidades = {};\n".format(tabela, idMax, identificador, idEntidade)

                querys += u
            
            querys += "\n"

            unificar1.writelines(querys)
            unificarGeral1.writelines(querys)

            idMax += 1

    print("Código SQL gerado para tabela: niveis")


def unificarHorariosPonto(idEntidadesAgrupadas):
    unificar1 = open(path.dirname(path.realpath(__file__)) + "\src\sql\\unificar_horarios_ponto_1.sql", "a")
 
    unificar1.writelines(desabilitarTriggers)

    resultado = select(
        """
            SELECT 
                list(i_entidades), 
                i_horarios_ponto, 
                count(*) AS quantidade 
            FROM 
                bethadba.horarios_ponto 
            WHERE
                i_entidades IN {}
            GROUP BY
                i_horarios_ponto
            HAVING
                quantidade > 1 
            ORDER BY 
                i_horarios_ponto      
        """.format(idEntidadesAgrupadas)
    )

    tabelas = tabelaColuna(['i_entidades', 'i_horarios_ponto'])

    idMax = select("SELECT (MAX(i_horarios_ponto)+1) AS id FROM bethadba.horarios_ponto")[0][0]

    for i in resultado:
        idsEntidade = i[0].split(',')

        identificador = i[1]

        for index, idEntidade in enumerate(idsEntidade):

            if index == 0:
                continue  

            #Gambiarra
            if ((int(identificador) == 1 and int(idEntidade) == 2) or (int(identificador) == 2 and int(idEntidade) in [2, 4]) or (int(identificador) == 3 and int(idEntidade) == 4)):
                continue    
            
            querys = ""

            for tabela in tabelas:
          
                u = "UPDATE bethadba.{} SET i_horarios_ponto = {} WHERE i_horarios_ponto = {} AND i_entidades = {};\n".format(tabela, idMax, identificador, idEntidade)

                querys += u
            
            querys += "\n"

            unificar1.writelines(querys)
            unificarGeral1.writelines(querys)

            idMax += 1

    print("Código SQL gerado para tabela: horarios_ponto")

def unificarGrupos(idEntidadesAgrupadas):
    unificar1 = open(path.dirname(path.realpath(__file__)) + "\src\sql\\unificar_grupos_1.sql", "a")

    unificar1.writelines(desabilitarTriggers)

    resultado = select(
        """
            SELECT 
                list(i_entidades), 
                i_grupos, 
                count(*) AS quantidade 
            FROM 
                bethadba.grupos 
            WHERE
                i_entidades IN {}
            GROUP BY
                i_grupos
            HAVING
                quantidade > 1 
            ORDER BY 
                i_grupos      
        """.format(idEntidadesAgrupadas)
    )

    tabelas = tabelaColuna(['i_entidades', 'i_grupos'])

    idMax = select("SELECT (MAX(i_grupos)+1) AS id FROM bethadba.grupos")[0][0]

    for i in resultado:
        idsEntidade = i[0].split(',')

        identificador = i[1]

        for index, idEntidade in enumerate(idsEntidade):

            if index == 0:
                continue    
            
            querys = ""

            for tabela in tabelas:
          
                u = "UPDATE bethadba.{} SET i_grupos = {} WHERE i_grupos = {} AND i_entidades = {};\n".format(tabela, idMax, identificador, idEntidade)

                querys += u
            
            querys += "\n"

            unificar1.writelines(querys)
            unificarGeral1.writelines(querys)

            idMax += 1

    print("Código SQL gerado para tabela: grupos")

def unificarLocaisTrab(idEntidadesAgrupadas):
    unificar1 = open(path.dirname(path.realpath(__file__)) + "\src\sql\\unificar_locais_trab_1.sql", "a")
    unificar2 = open(path.dirname(path.realpath(__file__)) + "\src\sql\\unificar_locais_trab_2.sql", "a")

    unificar1.writelines(desabilitarTriggers)
    unificar2.writelines(desabilitarTriggers)

    resultado = select(
        """
            SELECT 
                list(i_entidades), 
                i_locais_trab, 
                count(*) AS quantidade 
            FROM 
                bethadba.locais_trab 
            WHERE
                i_entidades IN {}
            GROUP BY
                i_locais_trab
            HAVING
                quantidade > 1 
            ORDER BY 
                i_locais_trab      
        """.format(idEntidadesAgrupadas)
    )

    tabelas = tabelaColuna(['i_entidades', 'i_locais_trab'])

    idMax = select("SELECT (MAX(i_locais_trab)+1) AS id FROM bethadba.locais_trab")[0][0]

    for i in resultado:
        idsEntidade = i[0].split(',')

        identificador = i[1]

        for index, idEntidade in enumerate(idsEntidade):

            if index == 0:
                continue    
            
            querys = ""

            for tabela in tabelas:
          
                u = "UPDATE bethadba.{} SET i_locais_trab = {} WHERE i_locais_trab = {} AND i_entidades = {};\n".format(tabela, idMax, identificador, idEntidade)

                if tabela in tabelasSemPermissoes:
                    unificar2.writelines(u)
                    unificarGeral2.writelines(u)
                    continue

                querys += u
            
            querys += "\n"

            unificar1.writelines(querys)
            unificarGeral1.writelines(querys)

            idMax += 1

    print("Código SQL gerado para tabela: locais_trab")

#--------------------Executar-------------------------#
unificarFuncionarios(idEntidadesAgrupadas)
unificarCargos(idEntidadesAgrupadas)
unificarPeriodosTrab(idEntidadesAgrupadas)
unificarTurmas(idEntidadesAgrupadas)
unificarDespesas(idEntidadesAgrupadas)
unificarNiveis(idEntidadesAgrupadas)
unificarHorariosPonto(idEntidadesAgrupadas)
unificarGrupos(idEntidadesAgrupadas)
unificarLocaisTrab(idEntidadesAgrupadas)