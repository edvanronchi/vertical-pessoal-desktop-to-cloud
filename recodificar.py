from variaveis import *
from src.functions import *
from src.database import *
from os import path

desabilitarTriggers = "CALL bethadba.dbp_conn_gera(1, 2021, 300);\nCALL bethadba.pg_setoption('wait_for_commit','on');\nCALL bethadba.pg_habilitartriggers('off');\nset option fire_triggers = 'off';\n\n"

#recodificarGeral = open(path.dirname(path.realpath(__file__)) + "\src\sql\\recodificar_geral.sql", "a")
#recodificarGeral.writelines(desabilitarTriggers)

def recodificarFuncionarios(idEntidadesAgrupadas):
    recodificar = open(path.dirname(path.realpath(__file__)) + "\src\sql\\recodificar_funcionarios.sql", "a")
    
    recodificar.writelines(desabilitarTriggers)

    resultado = select(
        """
            SELECT 
                list(i_entidades), 
                i_funcionarios, 
                count(*) AS quantidade 
            FROM 
                bethadba.funcionarios 
            WHERE
                i_entidades IN ({})    
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

    idCampoAdicional = select("SELECT i_caracteristicas FROM bethadba.caracteristicas WHERE nome = 'Matrícula do funcionário'")[0][0]

    for i in resultado:
        idsEntidade = i[0].split(',')

        identificador = i[1]

        for idEntidade in idsEntidade:

            if idEntidade == idEntidadePrincipal:
                continue

            valorCaracter = "{}-{}".format(idEntidade, identificador)

            queryDadosAdicionais = ""

            buscaDadosAdicionais = select(
                """
                    SELECT 
                        * 
                    FROM 
                        bethadba.funcionarios_prop_adic 
                    WHERE 
                        i_caracteristicas = {} AND 
                        i_funcionarios = {} AND 
                        i_entidades = {};
                """.format(idCampoAdicional, identificador, idEntidade)
            )

            if len(buscaDadosAdicionais) > 0:
                queryDadosAdicionais = "UPDATE bethadba.funcionarios_prop_adic SET valor_caracter = {} WHERE i_caracteristicas = {} AND i_entidades = {} AND i_funcionarios = {};".format(valorCaracter, idCampoAdicional, idEntidade, identificador)
            else:
                queryDadosAdicionais = "INSERT INTO bethadba.funcionarios_prop_adic (i_caracteristicas, i_entidades, i_funcionarios, valor_caracter) VALUES ({}, {}, {}, {});".format(idCampoAdicional, idEntidade, identificador, valorCaracter)
                   
            recodificar.writelines(queryDadosAdicionais)

            querys = ""

            for tabela in tabelas:
                
                u = "UPDATE bethadba.{} SET i_funcionarios = {} WHERE i_funcionarios = {} AND i_entidades = {};\n".format(tabela, idMax, identificador, idEntidade)

                querys += u
            
            querys += "\n"

            recodificar.writelines(querys)
            recodificar.writelines("COMMIT;\n")

            idMax += 1

    print("Código SQL gerado para tabela: funcionarios!")

def recodificarCargos(idEntidadesAgrupadas):
    recodificar = open(path.dirname(path.realpath(__file__)) + "\src\sql\\recodificar_cargos.sql", "a")

    recodificar.writelines(desabilitarTriggers)

    resultado = select(
        """
           SELECT 
                list(i_entidades), 
                i_cargos, 
                count(*) AS quantidade 
            FROM 
                bethadba.cargos 
            WHERE
                i_entidades IN ({})
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

        for idEntidade in idsEntidade:

            if idEntidade == idEntidadePrincipal:
                continue      
            
            querys = ""

            for tabela in tabelas:
          
                u = "UPDATE bethadba.{} SET i_cargos = {} WHERE i_cargos = {} AND i_entidades = {};\n".format(tabela, idMax, identificador, idEntidade)

                querys += u
            
            querys += "\n"

            recodificar.writelines(querys)
            #recodificarGeral.writelines(querys)

            idMax += 1

    print("Código SQL gerado para tabela: cargos")

def recodificarPeriodosTrab(idEntidadesAgrupadas):
    recodificar = open(path.dirname(path.realpath(__file__)) + "\src\sql\\recodificar_periodos_trab.sql", "a")

    recodificar.writelines(desabilitarTriggers)

    resultado = select(
        """
            SELECT 
                list(i_entidades), 
                i_periodos_trab, 
                count(*) AS quantidade 
            FROM
                bethadba.periodos_trab 
            WHERE
                i_entidades IN ({})
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

        for idEntidade in idsEntidade:

            if idEntidade == idEntidadePrincipal:
                continue      
            
            querys = ""

            for tabela in tabelas:
          
                u = "UPDATE bethadba.{} SET i_periodos_trab = {} WHERE i_periodos_trab = {} AND i_entidades = {};\n".format(tabela, idMax, identificador, idEntidade)

                querys += u
            
            querys += "\n"

            recodificar.writelines(querys)
            #recodificarGeral.writelines(querys)

            idMax += 1

    print("Código SQL gerado para tabela: periodos_trab")

def recodificarTurmas(idEntidadesAgrupadas):
    recodificar = open(path.dirname(path.realpath(__file__)) + "\src\sql\\recodificar_turmas.sql", "a")

    recodificar.writelines(desabilitarTriggers)

    resultado = select(
        """
            SELECT 
                list(i_entidades), 
                i_turmas, 
                count(*) AS quantidade 
            FROM 
                bethadba.turmas 
            WHERE
                i_entidades IN ({})
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

        for idEntidade in idsEntidade:

            if idEntidade == idEntidadePrincipal:
                continue      
            
            querys = ""

            for tabela in tabelas:
          
                u = "UPDATE bethadba.{} SET i_turmas = {} WHERE i_turmas = {} AND i_entidades = {};\n".format(tabela, idMax, identificador, idEntidade)

                querys += u
            
            querys += "\n"

            recodificar.writelines(querys)
            #recodificarGeral.writelines(querys)

            idMax += 1

    print("Código SQL gerado para tabela: turmas")

def recodificarDespesas(idEntidadesAgrupadas):
    recodificar = open(path.dirname(path.realpath(__file__)) + "\src\sql\\recodificar_despesas.sql", "a")

    recodificar.writelines(desabilitarTriggers)

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
                i_entidades IN ({})
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

        for idEntidade in idsEntidade:

            if idEntidade == idEntidadePrincipal:
                continue      
            
            querys = ""

            for tabela in tabelas:
          
                u = "UPDATE bethadba.{} SET i_despesas = {} WHERE i_despesas = {} AND i_entidades = {} AND ano_exerc = {};\n".format(tabela, idMax, identificador, idEntidade, anoExercicio)

                querys += u
            
            querys += "\n"

            recodificar.writelines(querys)
            #recodificarGeral.writelines(querys)

            idMax += 1

    print("Código SQL gerado para tabela: despesas")

def recodificarNiveis(idEntidadesAgrupadas):
    recodificar = open(path.dirname(path.realpath(__file__)) + "\src\sql\\recodificar_niveis.sql", "a")

    recodificar.writelines(desabilitarTriggers)

    resultado = select(
        """
            SELECT 
                list(i_entidades), 
                i_niveis, 
                count(*) AS quantidade 
            FROM 
                bethadba.níveis 
            WHERE
                i_entidades IN ({})
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

        for idEntidade in idsEntidade:

            if idEntidade == idEntidadePrincipal:
                continue      
            
            querys = ""

            for tabela in tabelas:
          
                u = "UPDATE bethadba.{} SET i_niveis = {} WHERE i_niveis = {} AND i_entidades = {};\n".format(tabela, idMax, identificador, idEntidade)

                querys += u
            
            querys += "\n"

            recodificar.writelines(querys)
            #recodificarGeral.writelines(querys)

            idMax += 1

    print("Código SQL gerado para tabela: niveis")


def recodificarHorariosPonto(idEntidadesAgrupadas):
    recodificar = open(path.dirname(path.realpath(__file__)) + "\src\sql\\recodificar_horarios_ponto.sql", "a")
 
    recodificar.writelines(desabilitarTriggers)

    resultado = select(
        """
            SELECT 
                list(i_entidades), 
                i_horarios_ponto, 
                count(*) AS quantidade 
            FROM 
                bethadba.horarios_ponto 
            WHERE
                i_entidades IN ({})
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

        for idEntidade in idsEntidade:

            if idEntidade == idEntidadePrincipal:
                continue  
           
            querys = ""

            for tabela in tabelas:
          
                u = "UPDATE bethadba.{} SET i_horarios_ponto = {} WHERE i_horarios_ponto = {} AND i_entidades = {};\n".format(tabela, idMax, identificador, idEntidade)

                querys += u
            
            querys += "\n"

            recodificar.writelines(querys)
            #recodificarGeral.writelines(querys)

            idMax += 1

    print("Código SQL gerado para tabela: horarios_ponto")

def recodificarGrupos(idEntidadesAgrupadas):
    recodificar = open(path.dirname(path.realpath(__file__)) + "\src\sql\\recodificar_grupos.sql", "a")

    recodificar.writelines(desabilitarTriggers)

    resultado = select(
        """
            SELECT 
                list(i_entidades), 
                i_grupos, 
                count(*) AS quantidade 
            FROM 
                bethadba.grupos 
            WHERE
                i_entidades IN ({})
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

        for idEntidade in idsEntidade:

            if idEntidade == idEntidadePrincipal:
                continue    
            
            querys = ""

            for tabela in tabelas:
          
                u = "UPDATE bethadba.{} SET i_grupos = {} WHERE i_grupos = {} AND i_entidades = {};\n".format(tabela, idMax, identificador, idEntidade)

                querys += u
            
            querys += "\n"

            recodificar.writelines(querys)
            #recodificarGeral.writelines(querys)

            idMax += 1

    print("Código SQL gerado para tabela: grupos")

def recodificarLocaisTrab(idEntidadesAgrupadas):
    recodificar = open(path.dirname(path.realpath(__file__)) + "\src\sql\\recodificar_locais_trab.sql", "a")

    recodificar.writelines(desabilitarTriggers)

    resultado = select(
        """
            SELECT 
                list(i_entidades), 
                i_locais_trab, 
                count(*) AS quantidade 
            FROM 
                bethadba.locais_trab 
            WHERE
                i_entidades IN ({})
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

        for idEntidade in idsEntidade:

            if idEntidade == idEntidadePrincipal:
                continue    
            
            querys = ""

            for tabela in tabelas:
          
                u = "UPDATE bethadba.{} SET i_locais_trab = {} WHERE i_locais_trab = {} AND i_entidades = {};\n".format(tabela, idMax, identificador, idEntidade)

                querys += u
            
            querys += "\n"

            recodificar.writelines(querys)
            #recodificarGeral.writelines(querys)

            idMax += 1

    print("Código SQL gerado para tabela: locais_trab")

#--------------------Executar-------------------------#
recodificarFuncionarios(idEntidadesAgrupadas)
#recodificarCargos(idEntidadesAgrupadas)
#recodificarPeriodosTrab(idEntidadesAgrupadas)
#recodificarTurmas(idEntidadesAgrupadas)
#recodificarDespesas(idEntidadesAgrupadas)
#recodificarNiveis(idEntidadesAgrupadas)
#recodificarHorariosPonto(idEntidadesAgrupadas)
#recodificarGrupos(idEntidadesAgrupadas)
#recodificarLocaisTrab(idEntidadesAgrupadas)