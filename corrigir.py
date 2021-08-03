from variaveis import *
from src.funcoes import *
from src.conexao import consultar, executar


# Gera CPF aleatorio para pessoas com CPF nulo
def pessoas_sem_cpf():
    resultado = consultar(
        """ 
            SELECT 
                p.i_pessoas,
                p.nome
            FROM 
                bethadba.pessoas p, 
                bethadba.pessoas_fisicas pf  
            WHERE 
                cpf IS NULL AND 
                p.i_pessoas = pf.i_pessoas;
        """
    )

    for i in resultado:
        identificador = i[0]

        u = "UPDATE bethadba.pessoas_fisicas SET cpf = {} WHERE i_pessoas = {};".format(cpf_gerar(False), identificador)

        executar(u)


# Renomeia os campos adicionais com descrição repetida
def caracteristicas_nome_repetido():
    resultado = consultar(
        """
            SELECT 
                LIST(i_caracteristicas), 
                TRIM(nome), 
                COUNT(nome) AS quantidade 
            FROM 
                bethadba.caracteristicas 
            GROUP BY 
                TRIM(nome) 
            HAVING 
                quantidade > 1
        """
    )

    for i in resultado:
        lista = i[0].split(',')
        nome = i[1]

        for index, identificador in enumerate(lista):
            if index == 0:
                continue

            u = "UPDATE bethadba.caracteristicas SET nome = '{}'  WHERE i_caracteristicas = {};".format(
                (nome + " |" + str(index)), identificador)

            print(u)
            executar(u)


# Adiciona o valor 1 - Filho para os dependentes que estão cadastrados como 10 - OUTROS
def dependentes_grau_outros():
    executar(
        """
            UPDATE 
                bethadba.dependentes
            SET
                grau = 1
            WHERE 
                grau = 10;
        """
    )


# Coloca a data '1900-01-01' nas datas das pessoas com data de nascimento maior que data de admissão
def pessoa_data_nascimento_maior_data_admissao():
    executar(
        """
            UPDATE 
                bethadba.pessoas_fisicas pff
            SET 
                pff.dt_nascimento = '1900-01-01' 
            FROM 
                ( 
                    SELECT 
                        i_funcionarios,
                        i_entidades,
                        f.dt_admissao,
                        pf.dt_nascimento,
                        pf.i_pessoas,
                        p.nome
                    FROM 
                        bethadba.funcionarios f
                    INNER JOIN 
                        bethadba.pessoas_fisicas pf ON (f.i_pessoas = pf.i_pessoas)
                    INNER JOIN 
                        bethadba.pessoas p ON (f.i_pessoas = p.i_pessoas)
                    WHERE
                        pf.dt_nascimento > f.dt_admissao AND f.i_entidades IN ({})
                ) AS subPessoa
            WHERE 
                pff.i_pessoas = subPessoa.i_pessoas;
        """.format(lista_entidade)
    )


# Coloca a data '1900-01-01' nas datas nulas
def pessoas_sem_dt_nascimento():
    executar(
        """
            UPDATE 
                bethadba.pessoas_fisicas pff
            SET 
                pff.dt_nascimento = '1900-01-01' 
            FROM 
                ( 
                    SELECT 
                        p.i_pessoas,
                        p.nome,
                        pf.dt_nascimento 
                    FROM
                        bethadba.pessoas p, 
                        bethadba.pessoas_fisicas pf  
                    WHERE 
                        dt_nascimento IS NULL AND
                        p.i_pessoas = pf.i_pessoas
                ) AS subPessoa
            WHERE 
                pff.i_pessoas = subPessoa.i_pessoas;
        """
    )


# Busca a data de vencimento da CNH menor que a data de emissão da 1ª habilitação!
def pessoas_cnh_dt_vencimento_menor_dt_emissao():
    executar(
        """
            UPDATE
                bethadba.hist_pessoas_fis
            SET 
                dt_vencto_cnh = dt_primeira_cnh+1
            WHERE
                dt_primeira_cnh >= dt_vencto_cnh; 
        """
    )

    executar(
        """
            UPDATE
                bethadba.pessoas_fis_compl
            SET 
                dt_vencto_cnh = dt_primeira_cnh+1
            WHERE 
                dt_primeira_cnh >= dt_vencto_cnh; 
        """
    )


# Busca pessoas com data de nascimento maior que emissão da 1ª habilitação!
def pessoas_dt_primeira_cnh_maior_dt_nascimento():
    resultado = consultar(
        """ 
            SELECT 
                pf.i_pessoas,
                pf.dt_nascimento,
                pfc.dt_emissao_cnh,
                pfc.dt_primeira_cnh
            FROM   
                bethadba.pessoas_fisicas pf 
            INNER JOIN
                bethadba.pessoas_fis_compl pfc ON (pf.i_pessoas = pfc.i_pessoas)
            WHERE  
                pf.dt_nascimento > pfc.dt_primeira_cnh or pf.dt_nascimento > pfc.dt_emissao_cnh;
        """
    )

    for i in resultado:
        i_pessoas = i[0]
        dt_nascimento = i[1]
        dt_emissao_cnh = i[2]
        dt_primeira_cnh = i[3]

        if dt_nascimento > dt_emissao_cnh and dt_nascimento > dt_primeira_cnh:
            u = "UPDATE bethadba.pessoas_fis_compl SET dt_primeira_cnh = '{0}', dt_emissao_cnh = '{0}' WHERE i_pessoas = {1};".format(
                dt_nascimento, i_pessoas)

        elif dt_nascimento < dt_emissao_cnh:
            u = "UPDATE bethadba.pessoas_fis_compl SET dt_primeira_cnh = '{0}', dt_emissao_cnh = '{0}' WHERE i_pessoas = {1};".format(
                dt_emissao_cnh, i_pessoas)

        elif dt_nascimento < dt_primeira_cnh:
            u = "UPDATE bethadba.pessoas_fis_compl SET dt_primeira_cnh = '{0}', dt_emissao_cnh = '{0}' WHERE i_pessoas = {1};".format(
                dt_primeira_cnh, i_pessoas)

        print(u)
        executar(u)


# Atualiza a data de nascimento de acordo com a do responsavel
def pessoas_dt_nasc_maior_dt_nasc_responsavel():
    executar(
        """
            UPDATE 
                bethadba.pessoas_fisicas pff
            SET 
                pff.dt_nascimento = pessoa.data_nascimento_responsavel
            FROM 
                ( 
                    SELECT 
                        pf.i_pessoas as id_responsavel,
                        dt_nascimento as data_nascimento_responsavel, 
                        i_dependentes as id_dependente, 
                        (
                            SELECT 
                                a.dt_nascimento 
                            FROM 
                                bethadba.pessoas_fisicas a 
                            WHERE 
                                a.i_pessoas = d.i_dependentes
                        ) AS data_nascimento_dependente 
                    FROM 
                        bethadba.pessoas_fisicas pf 
                    INNER JOIN 
                        bethadba.dependentes d ON (pf.i_pessoas = d.i_pessoas)
                    WHERE 
                        (data_nascimento_dependente < data_nascimento_responsavel OR
                        data_nascimento_dependente IS NULL) AND
                        grau = 1
                ) AS pessoa
            WHERE 
                pff.i_pessoas = pessoa.id_dependente; 
        """
    )


# Coloca nulo para um dos CPF's repetidos
# As Pessoas (0,0) possuem o mesmo CPF!
def pessoas_cpf_repetido():
    resultado = consultar(
        """
            SELECT
                LIST(pf.i_pessoas),
                cpf,
                COUNT(cpf) AS quantidade
            FROM 
                bethadba.pessoas_fisicas pf 
            GROUP BY 
                cpf 
            HAVING 
                quantidade > 1
        """
    )

    for i in resultado:
        lista = i[0].split(',')

        for index, identificador in enumerate(lista):
            if index == 0:
                continue

            u = "UPDATE bethadba.pessoas_fisicas SET cpf = NULL WHERE i_pessoas = {};".format(identificador)

            print(u)
            executar(u)


# Coloca nulo para um dos PIS's repetidos
# As Pessoas (0,0) possuem o mesmo número do PIS!
def pessoas_pis_repetido():
    resultado = consultar(
        """
            SELECT
                LIST(pf.i_pessoas),
                num_pis,
                COUNT(num_pis) AS quantidade
            FROM 
                bethadba.pessoas_fisicas pf 
            GROUP BY 
                num_pis 
            HAVING 
                quantidade > 1
        """
    )

    for i in resultado:
        lista = i[0].split(',')

        for index, identificador in enumerate(lista):
            if index == 0:
                continue

            u = "UPDATE bethadba.pessoas_fisicas SET num_pis = NULL WHERE i_pessoas = {};".format(identificador)

            print(u)
            executar(u)


# Verifica se o PIS é valido
# PIS inválido
def pessoas_pis_invalido():
    resultado = consultar(
        """
           SELECT
                i_pessoas,
                num_pis
            FROM 
                bethadba.pessoas_fisicas
            WHERE 
                num_pis IS NOT NULL;
        """
    )

    for i in resultado:
        identificador = i[0]
        pis = i[1]

        if not pis_validar(pis):
            u = "UPDATE bethadba.pessoas_fisicas SET num_pis = NULL WHERE i_pessoas = {};".format(identificador)

            executar(u)

        # Gera CNPJ aleatorio para pessoas com CNPJ nulo


def pessoas_sem_cnpj():
    resultado = consultar(
        """ 
            SELECT 
                pj.i_pessoas,
                p.nome
            FROM 
                bethadba.pessoas_juridicas pj 
            INNER JOIN 
                bethadba.pessoas p ON (pj.i_pessoas = p.i_pessoas)
            WHERE 
                cnpj IS NULL;
        """
    )

    for i in resultado:
        identificador = i[0]

        executar(
            """
                UPDATE bethadba.pessoas_juridicas SET cnpj = {} WHERE i_pessoas = {};
            """.format(cnpj_gerar(False), identificador)
        )


# Renomeia a descrição dos logradouros que tem caracter especial no inicio da descrição
def ruas_nome_caracter_especial():
    executar(
        """
            UPDATE 
                bethadba.ruas
            SET 
                nome = SUBSTRING(nome, 2)   
            WHERE 
                SUBSTRING(nome, 1, 1) in ('[', ']');
        """
    )


# Adiona um nome aleatorio para o nome da rua que está vazio
def ruas_sem_nome():
    executar(
        """
            UPDATE 
                bethadba.ruas
            SET 
                nome = 'Rua sem nome'
            WHERE
                nome = '' OR
                nome IS NULL;    
        """
    )


# Coloca a cidade da entidade
def ruas_sem_cidade():
    executar(
        """
            UPDATE 
                bethadba.ruas
            SET
                i_cidades = (SELECT TOP 1 i_cidades FROM bethadba.entidades)
            WHERE 
                i_cidades IS NULL;
        """
    )


# Renomeia os logradouros com descrição repetidos
def ruas_nome_repetido():
    resultado = consultar(
        """
            SELECT 
                LIST(i_ruas), 
                TRIM(nome),
                i_cidades, 
                COUNT(nome) AS quantidade
            FROM 
                bethadba.ruas 
            GROUP BY 
                TRIM(nome), 
                i_cidades
            HAVING 
                quantidade > 1;
        """
    )

    for i in resultado:
        lista = i[0].split(',')
        nome = i[1]

        for index, identificador in enumerate(lista):
            if index == 0:
                continue

            u = "UPDATE bethadba.ruas SET nome = '{}' WHERE i_ruas = {};".format((nome + " |" + str(index)),
                                                                                 identificador)

            print(u)
            executar(u)


# Renomeia os tipos bases repetidos
def tipos_bases_repetido():
    resultado = consultar(
        """
            SELECT 
                LIST(i_tipos_bases), 
                TRIM(nome), 
                COUNT(nome) AS quantidade
            FROM 
                bethadba.tipos_bases 
            GROUP BY 
                TRIM(nome) 
            HAVING 
                quantidade > 1;
        """
    )

    for i in resultado:
        lista = i[0].split(',')
        nome = i[1]

        for index, identificador in enumerate(lista):
            if index == 0:
                continue

            u = "UPDATE bethadba.tipos_bases SET nome = '{}'  WHERE i_tipos_bases = {};".format(
                (nome + " |" + str(index)), identificador)

            print(u)
            executar(u)


# Renomeia os atos com número nulo
def atos_sem_numero():
    resultado = consultar(
        """
            SELECT 
                i_atos
            FROM 
                bethadba.atos 
            WHERE
                num_ato IS NULL OR num_ato = '';   
        """
    )

    for index, i in enumerate(resultado, start=1):
        identificador = i[0]

        numero = "NAO INFOR. " + str(index)

        u = "UPDATE bethadba.atos SET num_ato = '{}'  WHERE i_atos = {};".format(numero, identificador)

        print(u)
        executar(u)


# Renomeia os atos repetidos
# Já existe um ato com o tipo e número oficial informado
def atos_repetido():
    resultado = consultar(
        """
            SELECT 
                LIST(i_atos),
                TRIM(num_ato),
                i_tipos_atos,
                COUNT(num_ato) AS quantidade
            FROM 
                bethadba.atos 
            GROUP BY 
                TRIM(num_ato),
                i_tipos_atos 
            HAVING 
                quantidade > 1;
        """
    )

    for i in resultado:
        lista = i[0].split(',')
        numero = i[1]

        for index, identificador in enumerate(lista):

            if index == 0:
                continue

            numero_novo = numero + " |" + str(index)

            if len(numero) > 13:
                numero_novo = numero[:13] + " |" + str(index)

            u = "UPDATE bethadba.atos SET num_ato = '{}'  WHERE i_atos = {};".format(numero_novo, identificador)

            print(u)
            executar(u)


# Adiciona o CBO mais utilizado no cargo
# O campo CBO é obrigatório
def cargos_sem_cbo():
    executar(
        """
            UPDATE 
                bethadba.cargos 
            SET 
                i_cbo = (SELECT TOP 1 i_cbo FROM bethadba.cargos GROUP BY i_cbo ORDER BY COUNT(i_cbo) DESC)
            WHERE
                i_cbo IS NULL AND i_entidades IN ({}); 
        """.format(lista_entidade)
    )

    executar(
        """
            UPDATE 
                bethadba.hist_cargos_cadastro 
            SET 
                i_cbo = (SELECT TOP 1 i_cbo FROM bethadba.cargos GROUP BY i_cbo ORDER BY COUNT(i_cbo) DESC)
            WHERE
                i_cbo IS NULL AND i_entidades IN ({}); 
        """.format(lista_entidade)
    )


# Adiciona uma categoria eSocial qualquer no vinculo empregaticio
def vinculos_sem_esocial():
    executar(
        """
            UPDATE 
                bethadba.vinculos
            SET 
                categoria_esocial =  (case tipo_func 
                                WHEN 'A' then 701
                                WHEN 'F' then 101
                                ELSE null
                                end)
            WHERE 
                categoria_esocial IS NULL 
                AND tipo_func <> 'B';                  
        """
    )


# Renomeia os vinculos empregaticios repetidos
def vinculos_descricao_repetido():
    resultado = consultar(
        """
            SELECT 
                LIST(i_vinculos), 
                TRIM(descricao),
                COUNT(descricao) AS quantidade 
            FROM 
                bethadba.vinculos 
            GROUP BY 
                TRIM(descricao) 
            HAVING
                quantidade > 1;
        """
    )

    for i in resultado:
        lista = i[0].split(',')
        descricao = i[1]

        for index, identificador in enumerate(lista):

            if index == 0:
                continue

            descricao_novo = descricao + " |" + str(index)

            if len(descricao) > 26:
                descricao_novo = descricao[:26] + " |" + str(index)

            u = "UPDATE bethadba.vinculos SET descricao = '{}'  WHERE i_vinculos = {};".format(descricao_novo,
                                                                                               identificador)

            print(u)
            executar(u)


# Adiciona uma categoria eSocial qualquer no motivo de rescisão
def motivos_resc_sem_esocial():
    executar(
        """
            UPDATE 
                bethadba.motivos_resc
            SET 
                categoria_esocial = '02'
            WHERE 
                categoria_esocial IS NULL;                
        """
    )


# Fecha as folha que não foram fechadas confome competencia passada por parametro
def folha_fechamento(competencia):
    executar(
        """
            UPDATE 
                bethadba.dados_calc SET dt_fechamento = date(year(i_competencias)||
                (if month(i_competencias) < 10 then '0'+cast(month(i_competencias) as varchar) else cast(month(i_competencias) as varchar) endif)||
                (if month(i_competencias) = 2 then '28' else '30' endif))
            WHERE 
                i_competencias < {0} AND dt_fechamento IS NULL; 

            COMMIT;

            UPDATE 
                bethadba.processamentos SET dt_fechamento = date(year(i_competencias)||
                (if month(i_competencias) < 10 then '0'+cast(month(i_competencias) as varchar) else cast(month(i_competencias) as varchar) endif)||
                (if month(i_competencias) = 2 then '28' else '30' endif))
            WHERE 
                i_competencias < {0} AND dt_fechamento IS NULL; 
            
            COMMIT;

            UPDATE 
                bethadba.processamentos SET pagto_realizado = 'S'
            WHERE 
                i_competencias < {0} AND pagto_realizado = 'N';                 
        """.format(competencia)
    )


# Adiciona uma categoria eSocial qualquer no motivo de aposentadoria
def motivos_apos_sem_esocial():
    executar(
        """
            UPDATE 
                bethadba.motivos_apos
            SET 
                categoria_esocial = '38'
            WHERE 
                categoria_esocial IS NULL;                
        """
    )


# Coloca R$0,01 nos historicos salariais com salario zerado ou nulo
def hist_salariais_sem_salario():
    executar(
        """
            UPDATE 
                bethadba.hist_salariais
            SET 
                salario = 0.01
            WHERE 
                salario IN (0, NULL) AND 
                i_entidades IN ({});          
        """.format(lista_entidade)
    )


# Faz a exclusão dessas variaveis
# Verifica variaveis com data inicial ou data final maior que data de rescisão
def variaveis_dt_inical_maior_dt_rescisao():
    resultado = consultar(
        """
            SELECT 
                v.i_entidades, 
                v.i_funcionarios,
                v.i_eventos,
                v.i_processamentos,
                v.i_tipos_proc, 
                v.dt_inicial, 
                v.dt_final
            FROM 
                bethadba.rescisoes r 
            INNER JOIN 
                bethadba.variaveis v ON (r.i_funcionarios = v.i_funcionarios AND r.i_entidades = v.i_entidades)
            INNER JOIN  
                bethadba.funcionarios f ON (r.i_funcionarios = f.i_funcionarios AND r.i_entidades = f.i_entidades)
            WHERE 
                v.dt_final > r.dt_rescisao OR v.dt_inicial > r.dt_rescisao AND f.i_entidades IN ({});
        """.format(lista_entidade)
    )

    if len(resultado) == 0:
        return

    delete = ""
    for i in resultado:
        delete += "DELETE FROM bethadba.variaveis_emprestimos_parc WHERE i_entidades = {} AND i_funcionarios = {} AND i_eventos = {} AND i_processamentos = {} AND i_tipos_proc = {} AND dt_inicial = '{}' AND dt_final = '{}';\n".format(
            i[0], i[1], i[2], i[3], i[4], i[5], i[6])
        delete += "DELETE FROM bethadba.variaveis WHERE i_entidades = {} AND i_funcionarios = {} AND i_eventos = {} AND i_processamentos = {} AND i_tipos_proc = {} AND dt_inicial = '{}' AND dt_final = '{}';\n".format(
            i[0], i[1], i[2], i[3], i[4], i[5], i[6])

    executar(delete)


# Renomeia as movimetação de pessoal repetidos
def tipos_movpes_descricao_repetido():
    resultado = consultar(
        """
            SELECT 
                LIST(i_tipos_movpes), 
                TRIM(descricao),
                COUNT(descricao) AS quantidade 
            FROM 
                bethadba.tipos_movpes 
            GROUP BY 
                TRIM(descricao) 
            HAVING
                quantidade > 1;
        """
    )

    for i in resultado:
        lista = i[0].split(',')
        descricao = i[1]

        for index, identificador in enumerate(lista):

            if index == 0:
                continue

            descricao_novo = descricao + " |" + str(index)

            if len(descricao) > 47:
                descricao_novo = descricao[:47] + " |" + str(index)

            u = "UPDATE bethadba.tipos_movpes SET descricao = '{}'  WHERE i_tipos_movpes = {};".format(descricao_novo,
                                                                                                       identificador)

            print(u)
            executar(u)


# Renomeia os tipos de afastamentos repetidos
def tipos_afast_descricao_repetido():
    resultado = consultar(
        """
            SELECT 
                LIST(i_tipos_afast), 
                TRIM(descricao),
                COUNT(descricao) AS quantidade 
            FROM 
                bethadba.tipos_afast 
            GROUP BY 
                TRIM(descricao)
            HAVING
                quantidade > 1;
        """
    )

    for i in resultado:
        lista = i[0].split(',')
        descricao = i[1]

        for index, identificador in enumerate(lista):

            if index == 0:
                continue

            descricao_novo = descricao + " |" + str(index)

            if len(descricao) > 47:
                descricao_novo = descricao[:47] + " |" + str(index)

            u = "UPDATE bethadba.tipos_afast SET descricao = '{}'  WHERE i_tipos_afast = {};".format(descricao_novo,
                                                                                                     identificador)

            print(u)
            executar(u)


# Coloca a data de rescisão na data de alteração
def hist_funcionarios_dt_alteracoes_maior_dt_rescisao():
    resultado = consultar(
        """
            SELECT
                hf.i_funcionarios,
                hf.i_entidades,
                hf.dt_alteracoes,
                r.dt_rescisao,
                STRING(r.dt_rescisao, ' ', SUBSTRING(hf.dt_alteracoes, 12, 8)) AS dt_alteracoes_novo
            FROM
                bethadba.hist_funcionarios hf
            INNER JOIN 
                bethadba.rescisoes r ON (hf.i_funcionarios = r.i_funcionarios AND hf.i_entidades = r.i_entidades)
            WHERE
                hf.dt_alteracoes > STRING(r.dt_rescisao, ' 23:59:59') AND hf.i_entidades IN ({})
            ORDER BY 
            	hf.i_funcionarios, hf.dt_alteracoes DESC;
        """.format(lista_entidade)
    )

    for i in resultado:
        query = ""
        quantidade = "SELECT * FROM bethadba.hist_funcionarios WHERE i_funcionarios = {} AND i_entidades = {} AND dt_alteracoes = '{}';".format(
            i[0], i[1], i[4])

        if len(consultar(quantidade)) > 0:
            query += "DELETE FROM bethadba.hist_funcionarios WHERE i_funcionarios = {} AND i_entidades = {} AND dt_alteracoes = '{}';\n".format(
                i[0], i[1], i[2])
            query += "DELETE FROM bethadba.hist_funcionarios_prop_adic WHERE i_funcionarios = {} AND i_entidades = {} AND dt_alteracoes = '{}';\n".format(
                i[0], i[1], i[2])

            print(query)
            executar(query)
        else:
            query += "UPDATE bethadba.hist_funcionarios SET dt_alteracoes = '{}' WHERE i_funcionarios = {} AND i_entidades = {} AND dt_alteracoes = '{}';\n".format(
                i[4], i[0], i[1], i[2])
            query += "UPDATE bethadba.hist_funcionarios_prop_adic SET dt_alteracoes = '{}' WHERE i_funcionarios = {} AND i_entidades = {} AND dt_alteracoes = '{}';\n".format(
                i[4], i[0], i[1], i[2])

            print(query)
            executar(query)


# Coloca a data de rescisão na data de alteração
def hist_salariais_dt_alteracoes_maior_dt_rescisao():
    resultado = consultar(
        """
            SELECT
                hs.i_funcionarios,
                hs.i_entidades,
                hs.dt_alteracoes,
                r.dt_rescisao,
                STRING(r.dt_rescisao, ' ', SUBSTRING(hs.dt_alteracoes, 12, 8)) AS dt_alteracoes_novo
            FROM
                bethadba.hist_salariais hs
            INNER JOIN 
                bethadba.rescisoes r ON (hs.i_funcionarios = r.i_funcionarios AND hs.i_entidades = r.i_entidades)
            WHERE
                hs.dt_alteracoes > STRING(r.dt_rescisao, ' 23:59:59') AND
                hs.i_entidades IN ({})
            ORDER BY 
                hs.dt_alteracoes DESC;
        """.format(lista_entidade)
    )

    for i in resultado:

        u = """
            UPDATE
                bethadba.hist_salariais
            SET
                dt_alteracoes = '{}'
            WHERE
                i_funcionarios = {} AND 
                i_entidades = {} AND
                dt_alteracoes = '{}';

        """.format(i[4], i[0], i[1], i[2])

        s = """
            SELECT 
                *
            FROM
                bethadba.hist_salariais
            WHERE 
                i_funcionarios = {} AND 
                i_entidades = {} AND
                dt_alteracoes = '{}';

        """.format(i[0], i[1], i[4])

        if len(consultar(s)) > 0:
            executar(
                """
                    DELETE FROM bethadba.hist_salariais WHERE i_funcionarios = {} AND i_entidades = {} AND dt_alteracoes = '{}';
                """.format(i[0], i[1], i[2])
            )

        else:
            executar(u)


# Coloca a data de rescisão na data de alteração
def hist_cargos_dt_alteracoes_maior_dt_rescisao():
    resultado = consultar(
        """
            SELECT
                hc.i_funcionarios,
                hc.i_entidades,
                hc.dt_alteracoes,
                r.dt_rescisao,
                STRING(r.dt_rescisao, ' ', SUBSTRING(hc.dt_alteracoes, 12, 8)) AS dt_alteracoes_novo
            FROM
                bethadba.hist_cargos hc
            INNER JOIN 
                bethadba.rescisoes r ON (hc.i_funcionarios = r.i_funcionarios AND hc.i_entidades = r.i_entidades)
            WHERE
                hc.dt_alteracoes > STRING(r.dt_rescisao, ' 23:59:59') AND
                hc.i_entidades IN ({})
            ORDER BY 
                hc.dt_alteracoes DESC;
        """.format(lista_entidade)
    )

    for i in resultado:

        u = """
            UPDATE
                bethadba.hist_cargos
            SET
                dt_alteracoes = '{}'
            WHERE
                i_funcionarios = {} AND 
                i_entidades = {} AND
                dt_alteracoes = '{}';
        """.format(i[4], i[0], i[1], i[2])

        s = """
            SELECT 
                *
            FROM
                bethadba.hist_cargos
            WHERE 
                i_funcionarios = {} AND 
                i_entidades = {} AND
                dt_alteracoes = '{}';

        """.format(i[0], i[1], i[4])

        if len(consultar(s)) > 0:
            executar(
                """
                    DELETE FROM bethadba.hist_cargos WHERE i_funcionarios = {} AND i_entidades = {} AND dt_alteracoes = '{}';
                """.format(i[0], i[1], i[2])
            )

        else:
            executar(u)


# Coloca 7 - (Licença SEM vencimentos) para as classificações que estão com código errado no tipo de afastamento
def tipos_afast_classif_invalida():
    executar(
        """
            UPDATE
                bethadba.tipos_afast
            SET
                classif = 7
            WHERE
                classif IN (1, NULL);   
        """
    )


# Renomeia os tipos de atos repetidos
def tipos_atos_nome_repetido():
    resultado = consultar(
        """
            SELECT 
                LIST(i_tipos_atos), 
                TRIM(nome),
                COUNT(nome) AS quantidade 
            FROM 
                bethadba.tipos_atos 
            GROUP BY 
                TRIM(nome) 
            HAVING
                quantidade > 1;
        """
    )

    for i in resultado:
        lista = i[0].split(',')
        descricao = i[1]

        for index, identificador in enumerate(lista):

            if index == 0:
                continue

            descricao_novo = descricao + " |" + str(index)

            if len(descricao) > 37:
                descricao_novo = descricao[:37] + " |" + str(index)

            u = "UPDATE bethadba.tipos_atos SET nome = '{}' WHERE i_tipos_atos = {};".format(descricao_novo,
                                                                                             identificador)

            print(u)
            executar(u)


# Renomeia as descrições repetidas no horario ponto
def horarios_ponto_descricao_repetido():
    resultado = consultar(
        """
            SELECT 
                LIST(i_entidades), 
                LIST(i_horarios_ponto), 
                TRIM(descricao),
                COUNT(descricao) AS quantidade 
            FROM 
                bethadba.horarios_ponto 
            GROUP BY 
                TRIM(descricao) 
            HAVING
                quantidade > 1;
        """
    )

    for i in resultado:
        entidade = i[0].split(',')
        horario = i[1].split(',')
        descricao = i[2]

        for index in range(len(entidade)):

            if index == 0:
                continue

            descricao_novo = descricao + " |" + str(index)

            if len(descricao) > 47:
                descricao_novo = descricao[:47] + " |" + str(index)

            u = """
                UPDATE 
                    bethadba.horarios_ponto 
                SET 
                    descricao = '{}' 
                WHERE 
                    i_entidades = {} AND i_horarios_ponto = {};
            """.format(descricao_novo, entidade[index], horario[index])

            executar(u)


# Renomeia as descrições repetidas na turma
def turmas_descricao_repetido():
    resultado = consultar(
        """
            SELECT 
                LIST(i_entidades), 
                LIST(i_turmas), 
                TRIM(descricao),
                COUNT(descricao) AS quantidade 
            FROM 
                bethadba.turmas 
            GROUP BY 
                TRIM(descricao) 
            HAVING
                quantidade > 1;
        """
    )

    for i in resultado:
        entidade = i[0].split(',')
        turma = i[1].split(',')
        descricao = i[2]

        for index in range(len(entidade)):

            if index == 0:
                continue

            descricao_novo = descricao + " |" + str(index)

            if len(descricao) > 57:
                descricao_novo = descricao[:57] + " |" + str(index)

            u = "UPDATE bethadba.turmas SET descricao = '{}' WHERE i_entidades = {} AND i_turmas = {};".format(
                descricao_novo, entidade[index], turma[index])

            print(u)
            executar(u)


# Coloca um ponto (.) nos separadores nulos
def niveis_organ_separador_invalido():
    executar(
        """
            UPDATE 
                bethadba.niveis_organ 
            SET 
                separador_nivel = '.'
            WHERE
                separador_nivel IS NULL;
        """
    )


# Adiciona a natureza de texto juridico mais utilizada no ato
def atos_sem_natureza_texto_juridico():
    executar(
        """
            UPDATE 
                bethadba.atos 
            SET 
                i_natureza_texto_juridico = (SELECT TOP 1 i_natureza_texto_juridico FROM bethadba.atos GROUP BY i_natureza_texto_juridico ORDER BY COUNT(i_natureza_texto_juridico) DESC)
            WHERE
                i_natureza_texto_juridico IS NULL; 
        """
    )


# Coloca a data de publicação do ato na data de fonte de divulgação
def atos_dt_publicacao_fonte_menor_dt_publicacao_divulgacao():
    executar(
        """
            UPDATE 
                bethadba.fontes_atos fa
            SET 
                fa.dt_publicacao = ato.dt_publicacao_ffa
            FROM 
                ( 
                     SELECT 
                        a.i_atos,
                        ffa.dt_publicacao,
                        a.dt_publicacao AS dt_publicacao_ffa
                    FROM 
                        bethadba.atos a
                    INNER JOIN 
                        bethadba.fontes_atos ffa ON (ffa.i_atos = a.i_atos)
                    WHERE 
                        ffa.dt_publicacao < a.dt_publicacao
                ) AS ato
            WHERE 
                fa.i_atos = ato.i_atos;
        """
    )


# Inseri um tipo de afastamento na configuração do cancelamento de férias
def canc_ferias_sem_tipos_afast():
    executar(
        """
            INSERT INTO bethadba.canc_ferias_afast
            SELECT 
                cf.i_canc_ferias AS i_canc_ferias, 
                1 AS i_tipos_afast 
            FROM 
                bethadba.canc_ferias cf
            WHERE 
                NOT EXISTS (SELECT i_tipos_afast FROM bethadba.canc_ferias_afast cfa WHERE cfa.i_canc_ferias = cf.i_canc_ferias);
        """
    )


# Renomeia descricao de cofiguração de organograma maior que 30 caracteres
def config_organograma_descricao_invalida():
    executar(
        """
            UPDATE 
                bethadba.config_organ co
            SET 
                co.descricao = SUBSTRING(co.descricao, 1, 30)
            FROM 
                ( 
                    SELECT 
                        i_config_organ,
                        descricao,
                        LENGTH(descricao) AS tamanho 
                    FROM 
                        bethadba.config_organ
                    WHERE 	
                        tamanho > 30 
                ) AS config_organograma
            WHERE 
                co.i_config_organ = config_organograma.i_config_organ;
        """
    )


# Renomeia descricao de cofiguração de organograma repetido
def config_organ_descricao_repetido():
    resultado = consultar(
        """
            SELECT 
                LIST(i_config_organ), 
                descricao, 
                COUNT(descricao) AS quantidade 
            FROM 
                bethadba.config_organ 
            GROUP BY 
                descricao 
            HAVING 
                quantidade > 1
        """
    )

    for i in resultado:
        lista = i[0].split(',')
        nome = i[1]

        for index, identificador in enumerate(lista):

            if index == 0:
                continue

            nome_novo = nome + " |" + str(index)

            if len(nome) > 27:
                nome_novo = nome[:27] + " |" + str(index)

            u = "UPDATE bethadba.config_organ SET descricao = '{}'  WHERE i_config_organ = {};".format(nome_novo,
                                                                                                       identificador)

            print(u)
            executar(u)


# Adiciona um CPF valido
def pessoas_cpf_invalido():
    resultado = consultar(
        """
           SELECT
                i_pessoas,
                cpf
            FROM 
                bethadba.pessoas_fisicas
            WHERE
                cpf IS NOT NULL;
        """
    )

    for i in resultado:
        identificador = i[0]
        cpf = i[1]

        if not cpf_validar(cpf):
            u = "UPDATE bethadba.pessoas_fisicas SET cpf = NULL WHERE i_pessoas = {};".format(identificador)

            executar(u)


# Adiciona um CNPJ valido
def pessoas_cnpj_invalido():
    resultado = consultar(
        """
           SELECT
                i_pessoas,
                cnpj
            FROM 
                bethadba.pessoas_juridicas
        """
    )

    for i in resultado:
        identificador = i[0]
        cnpj = i[1]

        if not cnpj_validar(cnpj):
            u = "UPDATE bethadba.pessoas_juridicas SET cnpj = '{}'  WHERE i_pessoas = {};".format(cnpj_gerar(),
                                                                                                  identificador)

            executar(u)


# Adiciona um RG aleatorio
def pessoas_rg_repetido():
    resultado = consultar(
        """
            SELECT
                LIST(i_pessoas),
                rg,
                COUNT(rg) AS quantidade
            FROM 
                bethadba.pessoas_fisicas 
            GROUP BY 
                rg 
            HAVING 
                quantidade > 1
        """
    )

    for i in resultado:
        lista = i[0].split(',')

        for index, identificador in enumerate(lista):
            if index == 0:
                continue

            u = "UPDATE bethadba.pessoas_fisicas SET rg = NULL  WHERE i_pessoas = {};".format(identificador)

            print(u)
            executar(u)


# Renomeia os cargos com descricão repetidos
# Já existe um cargo com a descrição informada
def cargos_descricao_repetido():
    resultado = consultar(
        """
            SELECT
                LIST(i_cargos),
                LIST(i_entidades),
                nome,
                COUNT(nome) AS quantidade
            FROM 
                bethadba.cargos 
            WHERE   
                i_entidades IN ({})
            GROUP BY 
                nome 
            HAVING 
                quantidade > 1
            ORDER BY
                quantidade
        """.format(lista_entidade)
    )

    for i in resultado:
        cargo = i[0].split(',')
        entidade = i[1].split(',')
        nome = i[2]

        for index in range(len(entidade)):

            if index == 0:
                continue

            nome_novo = nome + " |" + str(index)

            if len(nome) > 97:
                nome_novo = nome[:97] + " |" + str(index)

            u1 = "UPDATE bethadba.cargos SET nome = '{}' WHERE i_entidades = {} AND i_cargos = {};".format(nome_novo,
                                                                                                           entidade[
                                                                                                               index],
                                                                                                           cargo[index])
            u2 = "UPDATE bethadba.hist_cargos_cadastro SET nome = '{}' WHERE i_entidades = {} AND i_cargos = {};".format(
                nome_novo, entidade[index], cargo[index])

            print(u1)
            print(u2)

            executar(u1)
            executar(u2)


# Adiciona um valor fixo para o termino de vigencia maior que 2099
# Essa verificação é necessaria para não dar loop ao migrar a pessoa fisica
def bases_calc_outras_empresas_vigencia_invalida():
    executar(
        """
            UPDATE 
                bethadba.bases_calc_outras_empresas
            SET 
                dt_vigencia_fin = '2099-01-01'   
            WHERE
                dt_vigencia_fin > 20990101;        
        """
    )


# Remove os emails invalidos
def pessoas_email_invalido():
    resultado = consultar(
        """
            SELECT 
                i_pessoas,
                email
            FROM 
                bethadba.pessoas
            WHERE 
                email IS NOT NULL
        """
    )

    for i in resultado:
        i_pessoa = i[0]
        email = i[1]

        if not email_validar(email):
            u = "UPDATE bethadba.pessoas SET email = NULL WHERE i_pessoas = {};".format(i_pessoa)

            print(u)
            executar(u)


# Remove o número do endereço que está vazio
def pessoas_enderecos_sem_numero():
    executar(
        """
            UPDATE 
                bethadba.pessoas_enderecos
            SET 
                numero = NULL
            WHERE
                numero = '';    
        """
    )


# Adiciona previdencia federal para os funcionarios sem previdencia
def funcionarios_sem_previdencia():
    executar(
        """
            UPDATE 
                bethadba.hist_funcionarios hfu
            SET 
                hfu.prev_federal = 'S'
            FROM
                (
                   SELECT 
                        hf.i_funcionarios,
                        hf.i_entidades 
                    FROM 
                        bethadba.hist_funcionarios hf
                    INNER JOIN 
                        bethadba.funcionarios f ON (f.i_funcionarios = hf.i_funcionarios AND f.i_entidades = hf.i_entidades)
                    WHERE
                        hf.prev_federal = 'N' AND
                        hf.prev_estadual = 'N' AND
                        hf.fundo_ass = 'N' AND
                        hf.fundo_prev = 'N' AND
                        f.i_entidades IN ({}) AND
                        f.tipo_func = 'F'
                    GROUP BY
                        hf.i_funcionarios,
                        hf.i_entidades
                    ORDER BY	
                        hf.i_funcionarios 
                ) AS sem_previdencia
            WHERE
                hfu.i_funcionarios = sem_previdencia.i_funcionarios  AND
                hfu.i_entidades = sem_previdencia.i_entidades;    
        """.format(lista_entidade)
    )


# Exclui os eventos de média/vantagem que não tem eventos vinculados
# Os eventos de composição da média são obrigatórios
def mediasvant_sem_composicao():
    resultado = consultar(
        """
            SELECT 
                DISTINCT(m.i_eventos),
                me.i_eventos_medias
            FROM 
                bethadba.mediasvant m
            LEFT JOIN
                mediasvant_eve me ON (m.i_eventos = me.i_eventos_medias)
            WHERE 
                me.i_eventos_medias IS NULL
        """
    )

    for i in resultado:
        idEventos = i[0]

        d = "DELETE FROM bethadba.mediasvant WHERE i_eventos = {};".format(idEventos)

        print(d)
        executar(d)


# Exclui os eventos de média/vantagem pai que estão vinculados a outros
def mediasvant_eve_composicao_invalida():
    resultado = consultar(
        """
            SELECT 
                i_eventos_medias,
                i_eventos
            FROM
                bethadba.mediasvant_eve 
            WHERE 
                i_eventos IN (SELECT i_eventos FROM bethadba.mediasvant)
        """
    )

    for i in resultado:
        evento_media = i[0]
        evento = i[1]

        d = "DELETE FROM bethadba.mediasvant_eve WHERE i_eventos_medias = {} AND i_eventos = {};".format(evento_media,
                                                                                                         evento)

        executar(d)


# Verifica a data de admissão da matrícula se é posterior a data de início da matrícula nesta lotação física
def locais_mov_dt_inicial_menor_dt_admissao():
    executar(
        """
            UPDATE 
                bethadba.locais_mov lmv
            SET 
                lmv.dt_inicial = lotacaoFisica.dt_admissao
            FROM 
                ( 
                     SELECT 
                        f.dt_admissao,
                        lm.i_funcionarios,
                        lm.dt_inicial,
                        lm.i_entidades,
                        lm.i_locais_trab,
                        lm.dt_final 
                    FROM
                        bethadba.funcionarios f
                    INNER JOIN
                        bethadba.locais_mov lm ON (f.i_funcionarios = lm.i_funcionarios AND f.i_entidades = lm.i_entidades)
                    WHERE 
                        f.dt_admissao > lm.dt_inicial AND f.i_entidades IN ({})
                ) AS lotacaoFisica
            WHERE 
                lmv.i_entidades = lotacaoFisica.i_entidades AND
                lmv.i_funcionarios = lotacaoFisica.i_funcionarios AND
                lmv.dt_inicial = lotacaoFisica.dt_inicial AND
                lmv.i_locais_trab = lotacaoFisica.i_locais_trab;
        """.format(lista_entidade)
    )


# Limita a descrição do motivo de alteração do ponto em 30 caracteres
# A descrição não pode conter mais de 30 caracteres
def motivos_altponto_descricao_invalida():
    executar(
        """
            UPDATE 
                bethadba.motivos_altponto ma
            SET 
                ma.descricao = SUBSTRING(ma.descricao, 1, 30)
            FROM 
                ( 
                    SELECT
                        i_motivos_altponto,
                        LENGTH(descricao) AS tamanho_descricao
                    FROM
                        bethadba.motivos_altponto 
                    WHERE 
                        tamanho_descricao > 30  
                ) AS alteracao_ponto
            WHERE 
                ma.i_motivos_altponto = alteracao_ponto.i_motivos_altponto;  
        """
    )


# Limita o numero de caracteres em 150 no motivo dos afastamentos
def afastamentos_observacao_invalida():
    executar(
        """
            UPDATE 
                bethadba.afastamentos a
            SET 
                a.observacao = SUBSTRING(afastamento.observacao, 1, 150)
            FROM 
                ( 
                     SELECT 
                        LENGTH(observacao) AS tamanho_observacao, 
                        observacao,
                        i_entidades, 
                        i_funcionarios, 
                        dt_afastamento 
                    FROM
                        bethadba.afastamentos 
                    WHERE 
                        LENGTH(observacao) > 150 
                ) AS afastamento
            WHERE 
                a.i_entidades = afastamento.i_entidades AND
                a.i_funcionarios = afastamento.i_funcionarios AND
                a.dt_afastamento = afastamento.dt_afastamento;    
        """
    )


# Verifica a data inicial no afastamento se é maior que a data final
# A quantidade de dias não pode ser menor que 0
def ferias_dt_gozo_ini_maior_dt_gozo_fin():
    executar(
        """
            UPDATE 
                bethadba.ferias f
            SET 
                f.dt_gozo_ini = afastamento.dt_gozo_fin,
                f.dt_gozo_fin = afastamento.dt_gozo_ini
            FROM 
                ( 
                     SELECT 
                        i_entidades, 
                        i_funcionarios, 
                        i_ferias,
                        dt_gozo_ini,
                        dt_gozo_fin 
                    FROM 
                        bethadba.ferias 
                    WHERE 
                        dt_gozo_ini > dt_gozo_fin AND
                        i_entidades IN ({})
                ) AS afastamento
            WHERE 
                f.i_entidades = afastamento.i_entidades AND
                f.i_funcionarios = afastamento.i_funcionarios AND
                f.i_ferias = afastamento.i_ferias;    
        """.format(lista_entidade)
    )


# Adiciona o motivo de aposentadoria 1 - Aposentadoria por tempo de serviço, com rescisão contratual
# O motivo de rescisão é obrigatório
def rescisoes_sem_motivos_apos():
    executar(
        """
            UPDATE
                bethadba.rescisoes
            SET
                i_motivos_apos = 1
            WHERE
                i_motivos_resc = 7 AND 
                i_motivos_apos IS NULL AND
                i_entidades IN ({});                                    
        """.format(lista_entidade)
    )


# Renomeia os grupos funcionais repetidos
def grupos_nome_repetido():
    resultado = consultar(
        """
            SELECT
                LIST(i_entidades),
                LIST(i_grupos),
                nome,
                COUNT(nome) AS quantidade
            FROM 
                bethadba.grupos
            WHERE
                i_entidades IN ({}) 
            GROUP BY 
                nome 
            HAVING 
                quantidade > 1
        """.format(lista_entidade)
    )

    for i in resultado:
        entidade = i[0].split(',')
        grupo = i[1].split(',')
        nome = i[2]

        for index in range(len(entidade)):

            if index == 0:
                continue

            nome_novo = nome + " |" + str(index)

            if len(nome) > 57:
                nome_novo = nome[:57] + " |" + str(index)

            u = """
                UPDATE 
                    bethadba.grupos 
                SET 
                    nome = '{}' 
                WHERE 
                    i_entidades = {} AND i_grupos = {};
            """.format(nome_novo, entidade[index], grupo[index])

            print(u)
            executar(u)


# A data inicial do benefício não pode ser menor que a data de admissão
# Plano de saude
def func_planos_saude_vigencia_inicial_menor_vigencia_inicial_titular():
    executar(
        """
            UPDATE 
                bethadba.func_planos_saude fp
            SET 
                fp.vigencia_inicial = plano_saude.vigencia_inicial_titular
            FROM 
                ( 
                     SELECT 
                        fps.i_entidades,
                        fps.i_funcionarios,
                        fps.i_pessoas,
                        fps.i_sequenciais,
                        vigencia_inicial AS vigencia_inicial_dependente,
                        vigencia_inicial_titular = (SELECT vigencia_inicial FROM bethadba.func_planos_saude WHERE i_sequenciais = 1 AND i_funcionarios = fps.i_funcionarios)
                    FROM 
                        bethadba.func_planos_saude fps 
                    WHERE 
                        fps.i_sequenciais != 1 AND 
                        fps.vigencia_inicial < vigencia_inicial_titular AND 
                        fps.i_entidades IN ({})
                ) AS plano_saude
            WHERE 
                fp.i_entidades = plano_saude.i_entidades AND
                fp.i_funcionarios = plano_saude.i_funcionarios AND
                fp.i_pessoas = plano_saude.i_pessoas AND
                fp.i_sequenciais = plano_saude.i_sequenciais;    
        """.format(lista_entidade)
    )


# Remove caracteres especiais e espaços para que o número do telefone seja menor ou igual a 11
# O telefone pode conter no máximo 11 caracteres
def locais_trab_fone_invalido():
    executar(
        """
            UPDATE
                bethadba.locais_trab
            SET
                fone = NULL
            WHERE 
                LENGTH(fone) > 9 AND
                i_entidades IN ({});    
        """.format(lista_entidade)
    )


# Coloca a data de vigor na data de criação
# A data de criação é obrigatória
def atos_sem_dt_inicial():
    executar(
        """
            UPDATE 
                bethadba.atos a
            SET 
                a.dt_inicial = a.dt_vigorar
            WHERE 
                a.dt_inicial IS NULL;                                  
        """
    )


# Renomeia as descrições repetidas dos niveis salariais
def niveis_descricao_repetido():
    resultado = consultar(
        """
            SELECT 
                LIST(i_entidades), 
                LIST(i_niveis), 
                TRIM(nome),
                COUNT(nome) AS quantidade
            FROM 
                bethadba.niveis 
            WHERE
                i_entidades IN ({}) 
            GROUP BY 
                TRIM(nome)   
            HAVING
                quantidade > 1
        """.format(lista_entidade)
    )

    for i in resultado:
        entidade = i[0].split(',')
        nivel = i[1].split(',')
        nome = i[2]

        for index in range(len(entidade)):

            if index == 0:
                continue

            descricao_novo = nome + " |" + str(index)

            if len(nome) > 46:
                descricao_novo = nome[:46] + " |" + str(index)

            u = "UPDATE bethadba.niveis SET nome = '{}' WHERE i_entidades = {} AND i_niveis = {};".format(
                descricao_novo, entidade[index], nivel[index])

            print(u)
            executar(u)


# Recodifica os cartões pontos que estão diferentes de sua matricula ou repetidos
# Esta função só ira funcionar se os números das matriculas estiverem recodificados (que não se repetem)
def funcionarios_cartao_ponto_repetido():
    funcionario = consultar(
        """
            SELECT 
                LIST(i_entidades), 
                i_funcionarios, 
                COUNT(*) AS quantidade 
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
        """.format(lista_entidade)
    )

    if len(funcionario) > 0:
        return

    executar(
        """
            UPDATE 
                bethadba.hist_funcionarios
            SET 
                num_cp = i_funcionarios
            WHERE 
                bate_cartao = 'S' AND i_entidades IN ({});                                  
        """.format(lista_entidade)
    )

    executar(
        """
            UPDATE 
                bethadba.hist_funcionarios
            SET 
                num_cp = NULL
            WHERE 
                bate_cartao = 'N' AND i_entidades IN ({});                                  
        """.format(lista_entidade)
    )


# Coloca a data de nomeação na data de posse
# O funcionário x da entidade x deve ter a data de posse (0000-00-00) posterior à data de nomeação (0000-00-00)!
def cargos_dt_nomeacao_maior_dt_posse():
    executar(
        """
            UPDATE 
                bethadba.hist_cargos
            SET 
                dt_nomeacao = dt_posse
            WHERE 
                dt_nomeacao > dt_posse AND i_entidades IN ({});                                  
        """.format(lista_entidade)
    )


# Colaca os dados da conta bancaria de acordo com o cadastro de conta bancaria da pessoa
# Quando a forma de pagamento for "Crédito em conta" é necessário informar a conta bancária
def funcionarios_conta_bancaria_invalida():
    executar(
        """
            UPDATE 
                bethadba.hist_funcionarios hff
            SET 
                hff.i_bancos = conta_bancaria.banco_novo,
                hff.i_agencias = conta_bancaria.agencia_nova
            FROM 
                ( 
                    SELECT 
                        f.i_funcionarios,
                        f.i_entidades,
                        hf.dt_alteracoes,
                        hf.i_bancos AS banco_atual,
                        hf.i_agencias AS agencia_atual,
                        hf.i_pessoas_contas,
                        pc.i_bancos AS banco_novo,
                        pc.i_agencias AS agencia_nova
                    FROM 
                        bethadba.hist_funcionarios hf
                    INNER JOIN 
                        bethadba.funcionarios f ON (hf.i_funcionarios = f.i_funcionarios AND hf.i_entidades = f.i_entidades)
                    INNER JOIN 
                        bethadba.pessoas_contas pc ON (f.i_pessoas = pc.i_pessoas AND pc.i_pessoas_contas = hf.i_pessoas_contas)	
                    WHERE 
                        (pc.i_bancos != hf.i_bancos OR pc.i_agencias != hf.i_agencias) 
                        AND hf.forma_pagto = 'R' AND hf.i_entidades IN ({})
                ) AS conta_bancaria
            WHERE 
                hff.i_entidades = conta_bancaria.i_entidades AND
                hff.i_funcionarios = conta_bancaria.i_funcionarios AND
                hff.dt_alteracoes = conta_bancaria.dt_alteracoes;
        """.format(lista_entidade)
    )


# Coloca previdencia federal para os historicos de funcionarios com mais do que uma previdencia informada
# Apenas uma previdência pode ser informada
def funcionarios_com_mais_de_uma_previdencia():
    executar(
        """
            UPDATE 
                bethadba.hist_funcionarios hff
            SET 
                hff.prev_federal = 'S',
                hff.prev_estadual = 'N',
                hff.fundo_ass = 'N',
                hff.fundo_prev = 'N'
            FROM 
                ( 
                    SELECT 
                        i_funcionarios,
                        i_entidades,
                        dt_alteracoes,
                        LENGTH(REPLACE(prev_federal || prev_estadual || fundo_ass || fundo_prev, 'N', '')) AS quantidade
                    FROM 
                        bethadba.hist_funcionarios
                    WHERE
                        quantidade > 1 AND i_entidades IN ({})
                ) AS historico_funcionario
            WHERE 
                hff.i_entidades = historico_funcionario.i_entidades AND
                hff.i_funcionarios = historico_funcionario.i_funcionarios AND
                hff.dt_alteracoes = historico_funcionario.dt_alteracoes;
        """.format(lista_entidade)
    )


# Ajusta os afastamentos com data inicial menor que data de admissão
# A data inicial não poderá ser menor que a data de admissão
def afastamentos_dt_afastamento_menor_dt_admissao():
    resultado = consultar(
        """
            SELECT 
                dt_afastamento, 
                dt_ultimo_dia, 
                i_entidades, 
                i_funcionarios, 
                (SELECT dt_admissao FROM bethadba.funcionarios WHERE i_funcionarios = a.i_funcionarios AND i_entidades = a.i_entidades) AS data_admissao 
            FROM 
                bethadba.afastamentos a
            WHERE 
                a.dt_afastamento < data_admissao
                AND i_entidades IN ({});
        """.format(lista_entidade)
    )

    for i in resultado:
        dt_inicial = i[0]
        dt_final = i[1]
        entidade = i[2]
        funcionario = i[3]
        dt_admissao = i[4]

        u = "UPDATE bethadba.afastamentos SET dt_afastamento = '{}' WHERE i_funcionarios = {} AND i_entidades = {} AND dt_afastamento = '{}';".format(
            dt_admissao, funcionario, entidade, dt_inicial)

        print(u)
        executar(u)


# Renomeia as areas de atuação com descrição repetido
# Já existe uma área de atuação com a descrição informada
def areas_atuacao_nome_repetido():
    resultado = consultar(
        """
           SELECT 
                LIST(i_areas_atuacao), 
                TRIM(nome), 
                COUNT(nome) 
            FROM 
                bethadba.areas_atuacao 
            GROUP BY 
                TRIM(nome) 
            HAVING 
                COUNT(nome) > 1
        """
    )

    for i in resultado:
        lista = i[0].split(',')
        nome = i[1]

        for index, identificador in enumerate(lista):
            if index == 0:
                continue

            u = "UPDATE bethadba.areas_atuacao SET nome = '{}'  WHERE i_areas_atuacao = {};".format(
                (nome + " |" + str(index)), identificador)

            print(u)
            executar(u)


# Coloca 0 - Outros para os dependentes sem motivo de termino
# O motivo de término é obrigatório
def dependentes_sem_dt_fim():
    executar(
        """
            UPDATE
                bethadba.dependentes
            SET 
                mot_fin_depende = 0
            WHERE
                mot_fin_depende IS NULL AND 
                dt_fin_depende IS NOT NULL;                               
        """
    )


# Coloca a configuração de feroas mais utilizada para os cargos sem configuração de ferias
# A configuração de férias é obrigatória
def cargos_sem_configuracao_ferias():
    executar(
        """
            UPDATE
                bethadba.cargos_compl
            SET 
                i_config_ferias = (SELECT TOP 1 i_config_ferias FROM bethadba.cargos_compl GROUP BY i_config_ferias ORDER BY COUNT(*) DESC),
                i_config_ferias_subst = (SELECT TOP 1 i_config_ferias_subst FROM bethadba.cargos_compl GROUP BY i_config_ferias_subst ORDER BY COUNT(*) DESC)
            WHERE
                i_config_ferias IS NULL OR 
                i_config_ferias_subst IS NULL;                               
        """
    )


# Coloca a data de admissão na data de opção do FGTS
# Quando a data de admissão for posterior a 04/10/1988, a data da opção do FGTS deve ser igual a data de admissão
def opcao_fgts_diferente_dt_admissao():
    executar(
        """
            UPDATE
                bethadba.funcionarios
            SET 
                dt_opcao_fgts = dt_admissao
            WHERE
                dt_admissao > '1988-10-04' AND 
                dt_admissao != dt_opcao_fgts AND 
                i_entidades IN ({});                               
        """.format(lista_entidade)
    )


# Coloca forma de pagamento em dinheiro
# Quando a forma de pagamento for "Crédito em conta" é necessário informar a conta bancária
def funcionarios_conta_bancaria_sem_dados():
    executar(
        """
            UPDATE
                bethadba.hist_funcionarios
            SET 
                forma_pagto = 'D'
            WHERE
                forma_pagto = 'R' AND 
                i_pessoas_contas IS NULL AND
                i_entidades IN ({});                            
        """.format(lista_entidade)
    )


# Coloca 'A' - Automatico como origem de marcações para as marcacoes com origem invalida
def funcionarios_maracoes_invalida():
    executar(
        """
            UPDATE
                bethadba.apuracoes_marc
            SET 
                origem_marc = 'I'
            WHERE 
                origem_marc NOT IN ('O','I','A') AND
                i_entidades IN ({});                          
        """.format(lista_entidade)
    )


# Renomeia as ocorrencias do ponto com nome repetido
# Já existe uma ocorrência de ponto com a descrição informada
def ocorrencia_ponto_nome_repetido():
    resultado = consultar(
        """
            SELECT 
                LIST(i_ocorrencias_ponto), 
                TRIM(nome), 
                COUNT(nome) 
            FROM 
                bethadba.ocorrencias_ponto
            GROUP BY 
                TRIM(nome) 
            HAVING 
                COUNT(nome) > 1
        """
    )

    for i in resultado:
        lista = i[0].split(',')
        nome = i[1]

        for index, identificador in enumerate(lista):
            if index == 0:
                continue

            u = "UPDATE bethadba.ocorrencias_ponto SET nome = '{}'  WHERE i_ocorrencias_ponto = {};".format(
                (nome + " |" + str(index)), identificador)

            print(u)
            executar(u)


# Busca as as configurações de dirf com eventos repetidos
def configuracao_dirf_com_eventos_repetidos():
    resultado = consultar(
        "SELECT chave_dsk1 = campoDirf, nomeCampoDsk = CASE campo WHEN '0A-01' THEN '050101' WHEN '0A-03' THEN '050102' WHEN 'AA-01' THEN '05010201' WHEN 'AA-02-01' THEN '0501020201' WHEN 'AA-02-02' THEN '0501020202' WHEN 'AA-02-03' THEN '0501020203' WHEN 'AA-02-04' THEN '0501020204' WHEN '03-04' THEN '030401' WHEN '04-01' then '040101'           when '04-01-01' then '040102'             when '04-03' then '040301'         when '04-03-01' then '040302'         when '04-06' then '040601'            else         bethadba.dbf_retira_alfa_de_inteiros(campo)     end ,     campoDirf = case bethadba.dbf_retira_alfa_de_inteiros(nomeCampoDsk)         when '0301' then 'TOTAL_REND_INC_FERIAS'         when '0302' then 'CONTRIB_PREV_OFICIAL'         when '030301' then 'CONTRIB_PREV_PRIVADA'         when '030302' then 'CONTRIB_FAPI'         when '030303' then 'CONTRIB_FUND_PREV_SERVIDOR_PUBLICO'         when '030304' then 'CONTRIB_ENTE_PUBLICO_PATROCINADOR'         when '030401' then 'PENSAO_ALIMENTICIA'         when '030402' then 'PENSAO_ALIMENTICIA_13_SALARIO'         when '0305' then 'IRRF'         when '040101' then 'PARC_ISENTA_APOSENT'         when '040102' then 'PARC_ISENTA_APOSENT_13_SALARIO'         when '0402' then 'DIARIAS_AJUDAS_CUSTO'         when '040301' then 'PROV_APOSENT_MOLESTIA_GRAVE'         when '040302' then 'PROV_APOSENT_MOLESTIA_GRAVE_13_SALARIO'         when '0404' then 'LUCROS_DIVIDENDOS'         when '0405' then 'VALORES_PAGOS_TITULAR_SOCIO_EMPRESA'         when '040601' then 'INDENIZ_RESC_CONTRATO_TRABALHO'         when '040602' then 'INDENIZ_RESC_CONTRATO_TRABALHO_13_SALARIO'         when '040701' then 'REND_ISENTOS_OUTROS'         when '040702' then 'REND_ISENTOS_OUTROS_MEDICO_RESIDENTE'         when '050101' then 'TOTAL_REND_13_SALARIO'         when '050102' then 'IRRF_13_SALARIO'         when '05010201' then 'CONTRIB_PREV_OFICIAL_13_SALARIO'         when '0501020202' then 'CONTRIB_FAPI_13_SALARIO'         when '0501020203' then 'CONTRIB_FUND_PREV_SERVIDOR_PUBLICO_13_SALARIO'         when '0501020204' then 'CONTRIB_ENTE_PUBLICO_PATROCINADOR_13_SALARIO'         when '050301' then 'REND_SUJ_TRIB_EXCLUSIVA_OUTROS_13_SALARIO'         when '050302' then 'REND_SUJ_TRIB_EXCLUSIVA_OUTROS_13_SALARIO_MEDICO_RESIDENTE'         when '0601' then 'RRA_TOTAL_RENDIMENTOS_TRIBUTAVEIS'         when '0602' then 'RRA_EXCLUSAO_DESP_ACAO_JUDICIAL'         when '0603' then 'RRA_DEDUCAO_CONTRIB_PREV_OFICIAL'         when '0604' then 'RRA_DEDUCAO_PENSAO_ALIMENTICIA'         when '0605' then 'RRA_IRRF'         when '0606' then 'RRA_RENDIMENTOS_ISENTOS'         when '0700' then 'INFORMACOES_COMPLEMENTARES'         when 'ABOPEC' then 'ABONO_PECUNIARIO' end,         eventos =  LIST(i_eventos)     from bethadba.comprends where campo not in ('05-01','0A-02')       and campoDirf IS not NULL     group by campoDirf, nomeCampoDsk, chave_dsk1         union all         select chave_dsk1 = campoDirf,         nomeCampoDsk =         case campo             when '03-01' then '0601'             when '03-02' then '0603'             when '03-05' then '0605'             when '03-04' then '0604'         else             bethadba.dbf_retira_alfa_de_inteiros(campo)         end ,         campoDirf = case bethadba.dbf_retira_alfa_de_inteiros(nomeCampoDsk)                    when '0601' then 'RRA_TOTAL_RENDIMENTOS_TRIBUTAVEIS'             when '0602' then 'RRA_EXCLUSAO_DESP_ACAO_JUDICIAL'             when '0603' then 'RRA_DEDUCAO_CONTRIB_PREV_OFICIAL'             when '0604' then 'RRA_DEDUCAO_PENSAO_ALIMENTICIA'             when '0605' then 'RRA_IRRF'             when '0606' then 'RRA_RENDIMENTOS_ISENTOS' end,         eventos =  LIST(i_eventos)     from bethadba.comprends     where campo in ('03-01','03-02','03-03-01','03-03-02','03-03-03','03-03-04', '03-04','03-05') and campoDirf iISnot NULL group by campoDirf, nomeCampoDsk, chave_dsk1")

    for i in resultado:
        lista_eventos = i[3].split(',')

        for j in buscar_duplicatas(lista_eventos):

            evento = consultar(
                "SELECT campo, chave_dsk1 = campoDirf, nomeCampoDsk = CASE campo WHEN '0A-01' THEN '050101' WHEN '0A-03' THEN '050102' WHEN 'AA-01' THEN '05010201' WHEN 'AA-02-01' THEN '0501020201' WHEN 'AA-02-02' THEN '0501020202' WHEN 'AA-02-03' THEN '0501020203' WHEN 'AA-02-04' THEN '0501020204' WHEN '03-04' THEN '030401' WHEN '04-01' then '040101'           when '04-01-01' then '040102'             when '04-03' then '040301'         when '04-03-01' then '040302'         when '04-06' then '040601'            else         bethadba.dbf_retira_alfa_de_inteiros(campo)     end ,     campoDirf = case bethadba.dbf_retira_alfa_de_inteiros(nomeCampoDsk)         when '0301' then 'TOTAL_REND_INC_FERIAS'         when '0302' then 'CONTRIB_PREV_OFICIAL'         when '030301' then 'CONTRIB_PREV_PRIVADA'         when '030302' then 'CONTRIB_FAPI'         when '030303' then 'CONTRIB_FUND_PREV_SERVIDOR_PUBLICO'         when '030304' then 'CONTRIB_ENTE_PUBLICO_PATROCINADOR'         when '030401' then 'PENSAO_ALIMENTICIA'         when '030402' then 'PENSAO_ALIMENTICIA_13_SALARIO'         when '0305' then 'IRRF'         when '040101' then 'PARC_ISENTA_APOSENT'         when '040102' then 'PARC_ISENTA_APOSENT_13_SALARIO'         when '0402' then 'DIARIAS_AJUDAS_CUSTO'         when '040301' then 'PROV_APOSENT_MOLESTIA_GRAVE'         when '040302' then 'PROV_APOSENT_MOLESTIA_GRAVE_13_SALARIO'         when '0404' then 'LUCROS_DIVIDENDOS'         when '0405' then 'VALORES_PAGOS_TITULAR_SOCIO_EMPRESA'         when '040601' then 'INDENIZ_RESC_CONTRATO_TRABALHO'         when '040602' then 'INDENIZ_RESC_CONTRATO_TRABALHO_13_SALARIO'         when '040701' then 'REND_ISENTOS_OUTROS'         when '040702' then 'REND_ISENTOS_OUTROS_MEDICO_RESIDENTE'         when '050101' then 'TOTAL_REND_13_SALARIO'         when '050102' then 'IRRF_13_SALARIO'         when '05010201' then 'CONTRIB_PREV_OFICIAL_13_SALARIO'         when '0501020202' then 'CONTRIB_FAPI_13_SALARIO'         when '0501020203' then 'CONTRIB_FUND_PREV_SERVIDOR_PUBLICO_13_SALARIO'         when '0501020204' then 'CONTRIB_ENTE_PUBLICO_PATROCINADOR_13_SALARIO'         when '050301' then 'REND_SUJ_TRIB_EXCLUSIVA_OUTROS_13_SALARIO'         when '050302' then 'REND_SUJ_TRIB_EXCLUSIVA_OUTROS_13_SALARIO_MEDICO_RESIDENTE'         when '0601' then 'RRA_TOTAL_RENDIMENTOS_TRIBUTAVEIS'         when '0602' then 'RRA_EXCLUSAO_DESP_ACAO_JUDICIAL'         when '0603' then 'RRA_DEDUCAO_CONTRIB_PREV_OFICIAL'         when '0604' then 'RRA_DEDUCAO_PENSAO_ALIMENTICIA'         when '0605' then 'RRA_IRRF'         when '0606' then 'RRA_RENDIMENTOS_ISENTOS'         when '0700' then 'INFORMACOES_COMPLEMENTARES'         when 'ABOPEC' then 'ABONO_PECUNIARIO' end,         eventos = i_eventos     from bethadba.comprends            where campo not in ('05-01','0A-02')       and campoDirf iISnot NULL and i_eventos = {}  union all         select campo, chave_dsk1 = campoDirf,         nomeCampoDsk =         case campo             when '03-01' then '0601'             when '03-02' then '0603'             when '03-05' then '0605'             when '03-04' then '0604'         else             bethadba.dbf_retira_alfa_de_inteiros(campo)         end ,         campoDirf = case bethadba.dbf_retira_alfa_de_inteiros(nomeCampoDsk)                    when '0601' then 'RRA_TOTAL_RENDIMENTOS_TRIBUTAVEIS'             when '0602' then 'RRA_EXCLUSAO_DESP_ACAO_JUDICIAL'             when '0603' then 'RRA_DEDUCAO_CONTRIB_PREV_OFICIAL'             when '0604' then 'RRA_DEDUCAO_PENSAO_ALIMENTICIA'             when '0605' then 'RRA_IRRF'             when '0606' then 'RRA_RENDIMENTOS_ISENTOS' end,         eventos =  i_eventos     from bethadba.comprends     where campo in ('03-01','03-02','03-03-01','03-03-02','03-03-03','03-03-04', '03-04','03-05') and campoDirf iISnot NULL and i_eventos = {}".format(
                    j))

            for k in evento:

                if i[1] != k[2]:
                    continue

                print("campo: " + i[0])
                print("i_ventos: " + j[4])
                print("========")


# Renomeia descricao de motivo de alteração salarial repetido
# Já existe um motivo de alteração salarial com a descrição informada
def motivo_alt_salarial_descricao_repetido():
    resultado = consultar(
        """
            SELECT 
                LIST(i_motivos_altsal), 
                descricao, 
                COUNT(descricao) AS quantidade 
            FROM 
                bethadba.motivos_altsal 
            GROUP BY 
                descricao 
            HAVING 
                quantidade > 1
        """
    )

    for i in resultado:
        lista = i[0].split(',')
        descricao = i[1]

        for index, identificador in enumerate(lista):
            if index == 0:
                continue

            u = "UPDATE bethadba.motivos_altsal SET descricao = '{}'  WHERE i_motivos_altsal = {};".format(
                (descricao + " |" + str(index)), identificador)

            print(u)
            executar(u)

        # Remove a taxa do evento que está invalido


# A taxa deve ser composta de no máximo 3 números inteiros e 4 decimais
def evento_taxa_invalida():
    executar(
        """
            UPDATE 
                bethadba.eventos 
            SET
                taxa = 0
            WHERE 
                taxa > 999.9999;
        """
    )


# Altera a faixa da licença premio
# A licença não pode conter mais de 2 dígitos
def licenca_premio_faixa_invalida():
    executar(
        """
            UPDATE 
                bethadba.licpremio_faixas 
            SET
                taxa = 99
            WHERE 
                taxa > 99;
        """
    )


# Cria cadastro de formação para migração
# O profissional XXXXXX deve possuir formações cadastradas!
def formacao_vazio():
    resultado = consultar(
        """
            SELECT * FROM bethadba.formacoes WHERE nome = 'Formação para conversão'
        """
    )

    if len(resultado) > 0:
        return

    id_max = len(consultar("SELECT * FROM bethadba.formacoes")) + 1

    u = "INSERT INTO formacoes (i_formacoes, nome, sigla_conselho, nivel_formacao, seguranca_trab, uf_conselho) VALUES({}, 'Formação para conversão', NULL, 1,'N', NULL);".format(
        id_max)

    print(u)
    executar(u)


def contratacao_aprendiz_vazio():
    executar(
        """ 
            update 
                bethadba.hist_entidades_compl
            set 
                contratacao_aprendiz = 0,
                contr_aprendiz_ent_educ = 'N' 
            where 
                contratacao_aprendiz is null 
            and (contr_aprendiz_ent_educ is null or contr_aprendiz_ent_educ = 'N');
        """
    )


def contratacao_pcd_vazio():
    executar(
        """
            update 
                bethadba.hist_entidades_compl
            set 
                contratacao_pcds = 0
            where 
                contratacao_pcds is null;
        """
    )


# -----------------------Executar---------------------#
# pessoas_sem_cpf() - Em analise
# hist_funcionarios_dt_alteracoes_maior_dt_rescisao()
# cargos_sem_configuracao_ferias() - Em analise
# pessoas_data_vencimento_cnh_menor_data_emissao() - Em analise
# caracteristicas_nome_repetido()
# dependentes_grau_outros()
# pessoa_data_nascimento_maior_data_admissao()
pessoas_sem_dt_nascimento()
# pessoas_cnh_dt_vencimento_menor_dt_emissao()
# pessoas_dt_primeira_cnh_maior_dt_nascimento()
pessoas_dt_nasc_maior_dt_nasc_responsavel()
pessoas_cpf_repetido()
pessoas_pis_repetido()
# pessoas_pis_invalido()
pessoas_sem_cnpj()
# ruas_nome_caracter_especial()
# ruas_sem_nome()
# ruas_sem_cidade()
# ruas_nome_repetido()
# tipos_bases_repetido()
atos_sem_numero()
atos_repetido()
# cargos_sem_cbo()
vinculos_sem_esocial()
vinculos_descricao_repetido()
motivos_resc_sem_esocial()
# folha_fechamento(folha_fechamento_competencia)
# folhas_ferias_sem_dt_pagamento() Em analise
motivos_apos_sem_esocial()
# hist_salariais_sem_salario()
# variaveis_dt_inical_maior_dt_rescisao()
# tipos_movpes_descricao_repetido()
# tipos_afast_descricao_repetido()
# hist_salariais_dt_alteracoes_maior_dt_rescisao()
# hist_cargos_dt_alteracoes_maior_dt_rescisao()
# tipos_afast_classif_invalida()
# tipos_atos_nome_repetido()
# horarios_ponto_descricao_repetido()
turmas_descricao_repetido()
# niveis_organ_separador_invalido()
# atos_sem_natureza_texto_juridico()
# atos_dt_publicacao_fonte_menor_dt_publicacao_divulgacao()
# canc_ferias_sem_tipos_afast()
config_organograma_descricao_invalida()
# config_organ_descricao_repetido()
# pessoas_cpf_invalido()
# pessoas_cnpj_invalido()
pessoas_rg_repetido()
cargos_descricao_repetido()
# bases_calc_outras_empresas_vigencia_invalida()
# pessoas_email_invalido()
# pessoas_enderecos_sem_numero()
# funcionarios_sem_previdencia()
# mediasvant_sem_composicao()
# mediasvant_eve_composicao_invalida()
# locais_mov_dt_inicial_menor_dt_admissao()
# motivos_altponto_descricao_invalida()
# afastamentos_observacao_invalida()
# ferias_dt_gozo_ini_maior_dt_gozo_fin()
# rescisoes_sem_motivos_apos()
# grupos_nome_repetido()
# func_planos_saude_vigencia_inicial_menor_vigencia_inicial_titular()
# locais_trab_fone_invalido()
# atos_sem_dt_inicial()
niveis_descricao_repetido()
funcionarios_cartao_ponto_repetido()
cargos_dt_nomeacao_maior_dt_posse()
# funcionarios_conta_bancaria_invalida()
# funcionarios_com_mais_de_uma_previdencia()
# afastamentos_dt_afastamento_menor_dt_admissao()
# areas_atuacao_nome_repetido()
# dependentes_sem_dt_fim()
# opcao_fgts_diferente_dt_admissao()
# funcionarios_conta_bancaria_sem_dados()
# funcionarios_maracoes_invalida()
# ocorrencia_ponto_nome_repetido()
# configuracao_dirf_com_eventos_repetidos()
# motivo_alt_salarial_descricao_repetido()
# evento_taxa_invalida()
# licenca_premio_faixa_invalida()
formacao_vazio()
contratacao_aprendiz_vazio()
contratacao_pcd_vazio()
