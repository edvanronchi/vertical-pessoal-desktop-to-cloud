from variaveis import *
from src.funcoes import *
from src.conexao import *

#Busca as pessoas com data de nascimento maior que data de admissão
def pessoa_data_nascimento_maior_data_admissao():

    resultado = consultar(
        """
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
                pf.dt_nascimento > f.dt_admissao
                AND f.i_entidades IN ({});
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Pessoas com data de nascimento maior que data de admissão: '+ str(quantidade))

#Busca as pessoas com data de vencimento da CNH menor que a data de emissão da 1ª habilitação!
def pessoa_data_vencimento_cnh_menor_data_emissao():

    resultado = consultar(
        """
            SELECT 
                pessoas_fis_compl.i_pessoas
            FROM   
                bethadba.pessoas_fis_compl
            WHERE  
                dt_primeira_cnh > dt_vencto_cnh;
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Pessoas com data de vencimento da CNH maior que emissão da 1ª habilitação: '+ str(quantidade))

    return quantidade

#Busca pessoas com data de nascimento maior que emissão da 1ª habilitação!
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
                pf.dt_nascimento >= pfc.dt_primeira_cnh or pf.dt_nascimento >= pfc.dt_emissao_cnh;
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Pessoas com data de nascimento maior que emissão da 1ª habilitação: '+ str(quantidade))

    return quantidade    

#Busca os campos adicionais com descrição repetido
def caracteristicas_nome_repetido():

    resultado = consultar(
        """
            SELECT 
                LIST(i_caracteristicas), 
                TRIM(nome), 
                COUNT(nome) 
            FROM 
                bethadba.caracteristicas 
            GROUP BY 
                TRIM(nome) 
            HAVING 
                COUNT(nome) > 1
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Campos adicionais com descrição repetida: '+ str(quantidade))

    return quantidade

#Verifica se o dependente está cadastrado como 10 - OUTROS
def dependentes_grau_outros():

    resultado = consultar(
        """
            SELECT 
                i_dependentes,
                i_pessoas
            FROM
                bethadba.dependentes,
            WHERE 
                grau = 10
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Dependentes cadastrados como OUTROS: '+ str(quantidade))

    return quantidade

#Pessoas com data de nascimento nulo
def pessoas_sem_dt_nascimento():

    resultado = consultar(
        """
            SELECT 
                p.i_pessoas,
                p.nome,
                pf.dt_nascimento 
            FROM
                bethadba.pessoas p, 
                bethadba.pessoas_fisicas pf  
            WHERE 
                dt_nascimento IS NULL 
                AND p.i_pessoas = pf.i_pessoas
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Pessoas com data de nascimento nulo: '+ str(quantidade))

    return quantidade

#Pessoas com data de nascimento maior que data de dependencia
def pessoas_cnh_dt_vencimento_menor_dt_emissao():

    resultado = consultar(
        """
            SELECT 
                d.i_dependentes,
                pf.dt_nascimento,
                d.dt_ini_depende 
            FROM 
                bethadba.dependentes d 
            JOIN 
                bethadba.pessoas_fisicas pf  ON (d.i_dependentes = pf.i_pessoas)
            WHERE 
                dt_nascimento > dt_ini_depende
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Pessoas com data de nascimento maior do que data de dependencia: '+ str(quantidade))

    return quantidade

#Pessoas com data de nascimento maior que data de nascimento do responsavel
def pessoas_dt_nasc_maior_dt_nasc_responsavel():

    resultado = consultar(
        """
            SELECT 
                pf.i_pessoas as idPai,
                dt_nascimento as dataNascimentoPai, 
                i_dependentes as idFilho, 
                (
                    SELECT 
                        a.dt_nascimento 
                    FROM 
                        bethadba.pessoas_fisicas a 
                    WHERE 
                        a.i_pessoas = d.i_dependentes
                ) AS dataNascimentoFilho 
            FROM 
                bethadba.pessoas_fisicas pf 
            INNER JOIN 
                bethadba.dependentes d ON (pf.i_pessoas = d.i_pessoas)
            WHERE 
                dataNascimentoFilho < dataNascimentoPai 
                OR dataNascimentoFilho IS NULL
                AND grau = 1
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Pessoas com data de nascimento maior do que data de nascimento do responsavel: '+ str(quantidade))

    return quantidade

#Verifica os CPF's nulos
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
                p.i_pessoas = pf.i_pessoas     
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('CPF nulo(s): '+ str(quantidade))

    return quantidade

#Verifica os CPF's repetidos
#As Pessoas (0,0) possuem o mesmo CPF!
def pessoas_cpf_repetido():

    resultado = consultar(
        """
            SELECT
                LIST(pf.i_pessoas),
                TRIM(cpf),
                COUNT(cpf) AS quantidade
            FROM 
                bethadba.pessoas_fisicas pf 
            GROUP BY 
                TRIM(cpf) 
            HAVING 
                quantidade > 1
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('CPF repetido(s): '+ str(quantidade))

    return quantidade

#Verifica os PIS's repetidos
#As Pessoas (0,0) possuem o mesmo número do PIS!
def pessoas_pis_repetido():

    resultado = consultar(
        """
            SELECT
                LIST(pf.i_pessoas),
                TRIM(num_pis),
                COUNT(num_pis) AS quantidade
            FROM 
                bethadba.pessoas_fisicas pf 
            GROUP BY 
                TRIM(num_pis) 
            HAVING 
                quantidade > 1
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('PIS repetido(s): '+ str(quantidade))

    return quantidade

#Verifica se o PIS é valido
#PIS inválido
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

    quantidade = 0

    for i in resultado:
        pis = i[1]

        if not pis_validar(pis):
            quantidade += 1

    if quantidade == 0:
        return

    print('PIS invalido(s): '+ str(quantidade))

    return quantidade

#Verifica os PIS's repetidos
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
                cnpj IS NULL
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('CNPJ nulo(s): '+ str(quantidade))

    return quantidade

#Verifica a descrição dos logradouros que tem caracter especial no inicio da descrição
def ruas_nome_caracter_especial():

    resultado = consultar(
        """
            SELECT 
                SUBSTRING(nome, 1, 1) as nome_com_caracter 
            FROM 
                bethadba.ruas 
            WHERE 
                nome_com_caracter in ('[', ']')
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Logradouros que tem caracter especial no inicio da descrição: '+ str(quantidade))

    return quantidade

#Verifica os logradouros com descrição repetidos
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

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Logradouros repetido(s): '+ str(quantidade))

    return quantidade

#Renomeia os tipos bases repetidos
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

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Tipos bases repetido(s): '+ str(quantidade))

    return quantidade

#Verifica os logradouros sem cidades

def ruas_sem_cidade():
    resultado = consultar(
        """
            SELECT 
                i_ruas,
                nome
            FROM 
                bethadba.ruas 
            WHERE 
                i_cidades IS NULL
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Logradouros sem cidade(s): '+ str(quantidade))

    return quantidade

#Verifica os atos com número nulos
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

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Atos com número nulo: '+ str(quantidade))

    return quantidade

#Verifica os atos repetidos
#Já existe um ato com o tipo e número oficial informado
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
                quantidade > 1
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Atos repetido(s): '+ str(quantidade))

    return quantidade

#Verifica os CBO's nulos nos cargos
def cargos_sem_cbo():

    resultado = consultar(
        """
            SELECT 
                * 
            FROM 
                bethadba.cargos 
            WHERE 
                i_cbo IS NULL
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('CBO do cargo nulo(s): '+ str(quantidade))

    return quantidade

#Verifica categoria eSocial nulo no vinculo empregaticio
def vinculos_sem_esocial():

    resultado = consultar(
        """
            SELECT 
                i_vinculos,
                descricao,
                categoria_esocial
            FROM 
                bethadba.vinculos
            WHERE 
                categoria_esocial IS NULL
                AND tipo_func <> 'B'  
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('eSocial nulo nos vinculos empregraticios: '+ str(quantidade))

    return quantidade

#Renomeia os vinculos empregaticios repetidos
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
                quantidade > 1 
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Vinculo(s) empregaticio(s) repetido(s): '+ str(quantidade))

    return quantidade

#Verifica categoria eSocial nulo no motivo de rescisão
def motivos_resc_sem_esocial():

    resultado = consultar(
        """
            SELECT 
                i_motivos_resc,
                descricao,
                categoria_esocial
            FROM 
                bethadba.motivos_resc
            WHERE 
                categoria_esocial IS NULL
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('eSocial nulo no motivo de rescisão: '+ str(quantidade))

    return quantidade

#Verifica as folha que não foram fechadas confome competencia passada por parametro
def folha_fechamento(competencia):

    resultado = consultar(
        """
            SELECT * FROM bethadba.processamentos WHERE i_competencias < {} AND pagto_realizado = 'N' AND i_entidades IN ({})
        """.format(competencia, lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Folhas que não foram fechadas até a competencia ' + str(competencia) + ': '+ str(quantidade))

    return quantidade

#Verifica as folhas de ferias sem data de pagamento
#A data de pagamento é obrigatória
def folhas_ferias_sem_dt_pagamento():

    resultado = consultar(
        """
            SELECT 
                bethadba.dbf_getdatapagamentoferias(ferias.i_entidades,ferias.i_funcionarios,ferias.i_periodos,ferias.i_ferias) AS dataPagamento,
                i_entidades,
                i_ferias,
                i_funcionarios
            FROM 
                bethadba.ferias 
            WHERE 
                dataPagamento IS NULL AND i_entidades IN ({}); 
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Folhas de ferias sem data de pagamento: '+ str(quantidade))

    return quantidade

#Verifica categoria eSocial nulo no motivo de aposentadoria
def motivos_apos_sem_esocial():

    resultado = consultar(
        """
            SELECT 
                i_motivos_apos,
                descricao,
                categoria_esocial
            FROM 
                bethadba.motivos_apos
            WHERE 
                categoria_esocial IS NULL
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('eSocial nulo no motivo de aposentadoria: '+ str(quantidade))

    return quantidade

#Verifica historicos salariais com salario zerado ou nulo

def hist_salariais_sem_salario():
    resultado = consultar(
        """
            SELECT * FROM bethadba.hist_salariais WHERE salario IN (0, NULL) AND i_entidades IN ({})
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Historico salarial com salario zerado: '+ str(quantidade))

    return quantidade

#Verifica variaveis com data inicial ou data final maior que data de rescisão
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
                (v.dt_final > r.dt_rescisao OR v.dt_inicial > r.dt_rescisao) AND f.i_entidades IN ({});
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Variaveis com data final maior que data de rescisão: '+ str(quantidade))

    return quantidade

#Busca as movimetação de pessoal repetidos
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
                quantidade > 1
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Movimetação de pessoal repetido(s): '+ str(quantidade))

    return quantidade

#Busca os tipos de afastamentos repetidos
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
                quantidade > 1
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Movimetação de pessoal repetido(s): '+ str(quantidade))

    return quantidade

#Busca as alterações de historicos dos funcionarios maior que a data de rescisão
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
                hf.dt_alteracoes > STRING(r.dt_rescisao, ' 23:59:59')
                AND hf.i_entidades IN ({})
            ORDER BY 
            	hf.i_funcionarios, hf.dt_alteracoes DESC
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Data alteração de historico do funcionario maior que data de rescisão: '+ str(quantidade))

    return quantidade

#Busca as alterações de salario dos funcionarios maior que a data de rescisão
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
                hs.dt_alteracoes > STRING(r.dt_rescisao, ' 23:59:59') AND hs.i_entidades IN ({})
            ORDER BY 
                hs.dt_alteracoes DESC
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Data alteração salarial do funcionario maior que data de rescisão: '+ str(quantidade))

    return quantidade

#Busca as alterações de cargo dos funcionarios maior que a data de rescisão
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
                hc.dt_alteracoes DESC
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Data alteração de cargo do funcionario maior que data de rescisão: '+ str(quantidade))

    return quantidade

#Busca as classificações que estão com código errado no tipo de afastamento
def tipos_afast_classif_invalida():

    resultado = consultar(
        """
            SELECT
                descricao
            FROM 
                bethadba.tipos_afast
            WHERE 
                classif IN (1, NULL)    
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Classificações que estão com código errado no tipo de afastamento: '+ str(quantidade))

    return quantidade

#Busca os tipos de atos repetidos
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
                quantidade > 1
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Tipo de ato repetido(s): '+ str(quantidade))

    return quantidade

#Busca as descrições repetidas no horario ponto
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
                quantidade > 1
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Descricao do horario ponto repetido(s): '+ str(quantidade))

    return quantidade

#Busca as descrições repetidas na turma
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
                quantidade > 1
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Descricao da turma repetido(s): '+ str(quantidade))

    return quantidade

#Buscar niveis de organogramas com separadores nulos
def niveis_organ_separador_invalido():

    resultado = consultar(
        """
            SELECT 
                * 
            FROM
                bethadba.niveis_organ 
            WHERE 
                separador_nivel IS NULL 
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Separadores nulos nos niveis de organogramas: '+ str(quantidade))

    return quantidade

#Verifica a natureza de texto juridico se é nulo nos atos
def atos_sem_natureza_texto_juridico():

    resultado = consultar(
        """
            SELECT 
                * 
            FROM 
                bethadba.atos 
            WHERE 
                i_natureza_texto_juridico IS NULL
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Natureza texto juridico do ato nulo: '+ str(quantidade))

    return quantidade

#Verifica se a data de fonte de divulgação é menor que a data de publicacao do ato
def atos_dt_publicacao_fonte_menor_dt_publicacao_divulgacao():

    resultado = consultar(
        """
            SELECT 
                a.i_atos,
                fa.dt_publicacao,
                a.dt_publicacao	 
            FROM 
                bethadba.atos a
            INNER JOIN 
                bethadba.fontes_atos fa ON (fa.i_atos = a.i_atos)
            WHERE 
                fa.dt_publicacao < a.dt_publicacao
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Data de fonte de divulgação é menor que a data de publicacao do ato: '+ str(quantidade))

    return quantidade

#Ter ao menos um tipo de afastamento na configuração do cancelamento de férias
def canc_ferias_sem_tipos_afast():

    resultado = consultar(
        """
            SELECT 
                *
            FROM 
                bethadba.canc_ferias cf
            WHERE 
                NOT EXISTS (SELECT i_tipos_afast FROM bethadba.canc_ferias_afast cfa WHERE cfa.i_canc_ferias = cf.i_canc_ferias)
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Tipo de afastamento na configuração do cancelamento de férias vazio: '+ str(quantidade))

    return quantidade

#Verifica descricao de cofiguração de organograma se é maior que 30 caracteres
def config_organograma_descricao_invalida():

    resultado = consultar(
        """
            SELECT 
                i_config_organ,
                descricao,
                LENGTH(descricao) AS tamanho 
            FROM 
                bethadba.config_organ
            WHERE 	
                tamanho > 30
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Descricao de cofiguração de organograma maior que 30 caracteres: '+ str(quantidade))

    return quantidade

#Verifica descricao de cofiguração de organograma repetido
def config_organ_descricao_repetido():

    resultado = consultar(
        """
           SELECT 
                LIST(i_config_organ), 
                TRIM(descricao), 
                COUNT(descricao) AS quantidade 
            FROM 
                bethadba.config_organ 
            GROUP BY 
                TRIM(descricao) 
            HAVING 
                quantidade > 1
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Descricao de cofiguração de organograma repetido(s): '+ str(quantidade))

    return quantidade

#Verifica se o CPF é invalido
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

    quantidade = 0

    for i in resultado:
        cpf = i[1]
        
        if not cpf_validar(cpf):
            quantidade += 1

    if quantidade == 0:
        return

    print('CPF invalido(s): '+ str(quantidade))

    return quantidade

#Verifica se o CNPJ é invalido
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

    quantidade = 0

    for i in resultado:
        cnpj = i[1]
       
        if not cnpj_validar(cnpj):
            quantidade += 1

    if quantidade == 0:
        return

    print('CNPJ invalido(s): '+ str(quantidade))

    return quantidade

#Verifica os RG's repetidos
def pessoas_rg_repetido():

    resultado = consultar(
        """
            SELECT
                LIST(i_pessoas),
                TRIM(rg),
                COUNT(rg) AS quantidade
            FROM 
                bethadba.pessoas_fisicas 
            GROUP BY 
                TRIM(rg) 
            HAVING 
                quantidade > 1
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('RG repetido(s): '+ str(quantidade))

    return quantidade

#Verifica os cargos com descricao repetidos
#Já existe um cargo com a descrição informada
def cargos_descricao_repetido():

    resultado = consultar(
        """
            SELECT
                LIST(i_cargos),
                LIST(i_entidades),
                TRIM(nome),
                COUNT(nome) AS quantidade
            FROM 
                bethadba.cargos 
            WHERE   
                i_entidades IN ({})
            GROUP BY 
                TRIM(nome) 
            HAVING 
                quantidade > 1
            ORDER BY
                quantidade
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Cargo(s) repetido(s): '+ str(quantidade))

    return quantidade

#Verifica o termino de vigencia maior que 2099
#Essa verificação é necessaria para não dar loop ao migrar a pessoa fisica
def bases_calc_outras_empresas_vigencia_invalida():

    resultado = consultar(
        """
            SELECT 
                dt_vigencia_fin
            FROM 
                bethadba.bases_calc_outras_empresas
            WHERE 
                dt_vigencia_fin > 20990101
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Vigencia maior que 2099 em bases de calculos de outras empresas: '+ str(quantidade))

    return quantidade

#Verifica os emails invalidos
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

    quantidade = 0

    for i in resultado:
        id_pessoa = i[0]
        email = i[1]

        if not email_validar(email):
            quantidade += 1

    if quantidade == 0:
        return

    print('Email invalido: '+ str(quantidade))

    return quantidade

#Verifica o número de endereço se está vazio
def pessoas_enderecos_sem_numero():

    resultado = consultar(
        """
            SELECT 
                i_pessoas 
            FROM 
                bethadba.pessoas_enderecos 
            WHERE
                numero = ''
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Número de endereço vazio: '+ str(quantidade))

    return quantidade

#Verifica o nome de rua se está vazio
def ruas_sem_nome():

    resultado = consultar(
        """
            SELECT 
                * 
            FROM 
                bethadba.ruas 
            WHERE
                nome = '' OR
                nome IS NULL
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Nome da rua vazio: '+ str(quantidade))

    return quantidade

#Verifica os funcionarios sem previdencia
def funcionarios_sem_previdencia():

    resultado = consultar(
        """
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
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Funcionario sem previdencia: '+ str(quantidade))

    return quantidade

#Verifica os eventos de média/vantagem que não tem eventos vinculados
#Os eventos de composição da média são obrigatórios
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

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Eventos de média/vantagem compondo outros eventos: '+ str(quantidade))

    return quantidade

#Verifica os eventos de média/vantagem se estão compondo outros eventos de média/vantagem
#Eventos de composição não pode ser eventos de média/vantagem
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

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Eventos de média/vantagem sem composição de eventos: '+ str(quantidade))

    return quantidade

#Verifica a data de admissão da matrícula se é posterior a data de início da matrícula nesta lotação física
def locais_mov_dt_inicial_menor_dt_admissao():

    resultado = consultar(
        """
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
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Data admissão matricula maior que data inicial de lotação fisica: '+ str(quantidade))

    return quantidade

#Verifica a descrição do motivo de alteração do ponto se contem mais que 30 caracteres
#A descrição não pode conter mais de 30 caracteres
def motivos_altponto_descricao_invalida():

    resultado = consultar(
        """
            SELECT
                i_motivos_altponto,
                LENGTH(descricao) AS tamanho_descricao
            FROM
                bethadba.motivos_altponto 
            WHERE 
                tamanho_descricao > 30 
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Descricao de motivos de alteração do ponto maior que 30 caracteres: '+ str(quantidade))

    return quantidade

#Verifica o motivo nos afastamentos se contem no máximo 150 caracteres
def afastamentos_observacao_invalida():

    resultado = consultar(
        """
            SELECT 
                LENGTH(observacao) AS tamanho_observacao, 
                i_entidades, 
                i_funcionarios, 
                dt_afastamento 
            FROM
                bethadba.afastamentos 
            WHERE 
                LENGTH(observacao) > 150 
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Motivos nos afastamentos maior que 150 caracteres: '+ str(quantidade))

    return quantidade

#Verifica a data inicial no afastamento de ferias se é maior que a data final 
#A quantidade de dias não pode ser menor que 0
def ferias_dt_gozo_ini_maior_dt_gozo_fin():

    resultado = consultar(
        """
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
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Data inicial no afastamento de férias é maior que a data final: '+ str(quantidade))

    return quantidade

#Busca as rescisões de aposentadoria com motivo nulo
#O motivo de rescisão é obrigatório
def rescisoes_sem_motivos_apos():

    resultado = consultar(
        """
            SELECT 
                i_entidades,
                i_funcionarios,
                i_rescisoes 
            FROM 
                bethadba.rescisoes 
            WHERE 
                i_motivos_resc = 7 AND 
                i_motivos_apos IS NULL AND 
                i_entidades IN ({})
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Rescisões de aposentadoria com motivo nulo: '+ str(quantidade))

    return quantidade

#Verifica os grupos funcionais repetidos
def grupos_nome_repetido():

    resultado = consultar(
        """
            SELECT
                LIST(i_entidades),
                LIST(i_grupos),
                TRIM(nome),
                COUNT(nome) AS quantidade
            FROM 
                bethadba.grupos
            WHERE
                i_entidades IN ({}) 
            GROUP BY 
                TRIM(nome) 
            HAVING 
                quantidade > 1
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Grupos funcionais repetido(s): '+ str(quantidade))

    return quantidade

#Verifica a data inicial de beneficio do dependente se é melhor que a do titular
#A data inicial do benefício não pode ser menor que a data de admissão
#Plano de saude
def func_planos_saude_vigencia_inicial_menor_vigencia_inicial_titular():

    resultado = consultar(
        """
            SELECT 
                fps.i_entidades,
                fps.i_funcionarios,
                fps.i_pessoas,
                fps.i_sequenciais,
                vigencia_inicial AS vigencia_inicial_dependente,
                vigencia_inicial_titular = (select vigencia_inicial FROM bethadba.func_planos_saude WHERE i_sequenciais = 1 AND i_funcionarios = fps.i_funcionarios)
            FROM 
                bethadba.func_planos_saude fps 
            WHERE 
                fps.i_sequenciais != 1 AND 
                fps.vigencia_inicial < vigencia_inicial_titular   
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('A data inicial do dependente maior do que do titular (Plano de Saude): '+ str(quantidade))

    return quantidade

#Verifica se o número de telefone na lotação fisica é maior que 11 caracteres
#O telefone pode conter no máximo 11 caracteres
def locais_trab_fone_invalido():

    resultado = consultar(
        """
            SELECT 
                i_entidades,
                i_locais_trab,
                fone,
                LENGTH(fone) AS quantidade
            FROM 
                bethadba.locais_trab
            WHERE 
                quantidade > 11 AND
                i_entidades IN ({});      
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Número de telefone na lotação fisica é maior que 11 caracteres: '+ str(quantidade))

    return quantidade

#Busca os atos com data inicial nulo
#A data de criação é obrigatória
def atos_sem_dt_inicial():

    resultado = consultar(
        """
            SELECT 
                i_atos, 
                dt_vigorar 
            FROM
                bethadba.atos 
            WHERE
                dt_inicial IS NULL     
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Data de criação do ato é obrigatorio: '+ str(quantidade))

    return quantidade

#Busca as descrições repetidas dos niveis salariais
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

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Descricao de niveis salariais repetido(s): '+ str(quantidade))

    return quantidade

#Busca os cartões pontos que estão diferente de sua matricula ou repetidos
#Esta função só ira funcionar se os números das matriculas estiverem recodificados (que não se repetem)
def funcionarios_cartao_ponto_repetido():

    matriculas = consultar(
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

    if len(matriculas) > 0:
        return

    resultado = consultar(
        """
            SELECT 
                num_cp, 
                LIST(DISTINCT(i_funcionarios)), 
                COUNT(DISTINCT(i_funcionarios)) AS quantidade
            FROM 
                bethadba.hist_funcionarios 
            WHERE
                bate_cartao = 'S' AND num_cp IS NOT NULL
                AND i_entidades IN ({}) 
            GROUP BY 
                num_cp
            HAVING
                quantidade > 1
            ORDER BY 
                quantidade DESC
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Cartão ponto repetido(s): '+ str(quantidade))

    return quantidade

#Busca os funcionarios com data de nomeação maior que a data de posse
#O funcionário x da entidade x deve ter a data de posse (0000-00-00) posterior à data de nomeação (0000-00-00)!
def cargos_dt_nomeacao_maior_dt_posse():

    resultado = consultar(
        """
            SELECT 
                i_funcionarios 
            FROM 
                bethadba.hist_cargos
            WHERE
                dt_nomeacao > dt_posse AND i_entidades IN ({})
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Data de nomeação maior que data de posse: '+ str(quantidade))

    return quantidade

#Busca as contas bancarias dos funcionarios que estão invalidas
#Quando a forma de pagamento for "Crédito em conta" é necessário informar a conta bancária
def funcionarios_conta_bancaria_invalida():

    resultado = consultar(
        """
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
                (pc.i_bancos != hf.i_bancos OR pc.i_agencias != hf.i_agencias) AND hf.forma_pagto = 'R' AND f.i_entidades IN ({})
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Historicos de funcionarios que estão com conta bancaria errada: '+ str(quantidade))

    return quantidade

#Busca os historicos de funcionarios com mais do que uma previdencia informada
#Apenas uma previdência pode ser informada
def funcionarios_com_mais_de_uma_previdencia():

    resultado = consultar(
        """
            SELECT 
                i_funcionarios,
                i_entidades,
                dt_alteracoes,
                LENGTH(REPLACE(prev_federal || prev_estadual || fundo_ass || fundo_prev, 'N', '')) AS quantidade
            FROM 
                bethadba.hist_funcionarios
            WHERE
                quantidade > 1 AND i_entidades IN ({});
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Historicos de funcionarios com mais do que uma previdencia informada: '+ str(quantidade))

    return quantidade

#Busca os afastamentos com data inicial menor que data de admissão
#A data inicial não poderá ser menor que a data de admissão
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
                a.dt_afastamento < data_admissao AND a.i_entidades IN ({});
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Afastamentos com data inicial menor que data de admissão: '+ str(quantidade))

    return quantidade

#Busca as areas de atuação com descrição repetido
#Já existe uma área de atuação com a descrição informada
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

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Áreas de atuação com descrição repetido: '+ str(quantidade))

    return quantidade

#Busca os dependentes sem motivo de termino
#O motivo de término é obrigatório
def dependentes_sem_dt_fim():

    resultado = consultar(
        """
            SELECT 
                i_pessoas ,
                i_dependentes,
                dt_ini_depende
            FROM 
                bethadba.dependentes d  
            WHERE 
                mot_fin_depende IS NULL AND 
                dt_fin_depende IS NOT NULL;
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Dependente sem motivo de termino: '+ str(quantidade))

    return quantidade

#Busca os cargos sem configuração de ferias
#A configuração de férias é obrigatória
def cargos_sem_configuracao_ferias():

    resultado = consultar(
        """
            SELECT 
                i_cargos, i_entidades 
            FROM 
                bethadba.cargos_compl
            WHERE
                i_config_ferias IS NULL OR 
                i_config_ferias_subst IS NULL
                AND i_entidades IN ({})
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Cargos sem configuração de ferias: '+ str(quantidade))

    return quantidade

#Busca a data da opção do FGTS diferente que a data de admissão
#Quando a data de admissão for posterior a 04/10/1988, a data da opção do FGTS deve ser igual a data de admissão
def opcao_fgts_diferente_dt_admissao():

    resultado = consultar(
        """
            SELECT 
                i_funcionarios, 
                i_entidades, 
                dt_admissao, 
                dt_opcao_fgts 
            FROM 
                bethadba.funcionarios 
            WHERE
                dt_admissao > '1988-10-04' AND 
                dt_admissao != dt_opcao_fgts
                AND i_entidades IN ({})
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Data da opção do FGTS diferente que a data de admissão: '+ str(quantidade))

    return quantidade

#Busca os funcionarios com recebimento credito em conta sem dados da conta bancaria
#Quando a forma de pagamento for "Crédito em conta" é necessário informar a conta bancária
def funcionarios_conta_bancaria_sem_dados():

    resultado = consultar(
        """
            SELECT 
                i_funcionarios,
                i_entidades
            FROM 
                bethadba.hist_funcionarios hf 
            WHERE 
                forma_pagto = 'R' AND 
                i_pessoas_contas IS NULL
                AND i_entidades IN ({})
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Funcionarios com recebimento credito em conta sem dados da conta bancaria: '+ str(quantidade))

    return quantidade

#Busca os funcionarios com marcacoes com origem invalida
def funcionarios_maracoes_invalida():

    resultado = consultar(
        """
            SELECT 
                i_funcionarios
            FROM 
                bethadba.apuracoes_marc am 
            WHERE 
                origem_marc NOT IN ('O','I','A') 
                AND i_entidades IN ({})
        """.format(lista_entidade)
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Funcionarios com marcacoes com origem invalida: '+ str(quantidade))

    return quantidade

#Busca as ocorrencias do ponto com nome repetido
#Já existe uma ocorrência de ponto com a descrição informada
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

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Ocorrencias do ponto com nome repetido: '+ str(quantidade))

    return quantidade

#Busca as as configurações de dirf com eventos repetidos
def configuracao_dirf_com_eventos_repetidos():

    resultado = consultar("SELECT chave_dsk1 = campoDirf, nomeCampoDsk = CASE campo WHEN '0A-01' THEN '050101' WHEN '0A-03' THEN '050102' WHEN 'AA-01' THEN '05010201' WHEN 'AA-02-01' THEN '0501020201' WHEN 'AA-02-02' THEN '0501020202' WHEN 'AA-02-03' THEN '0501020203' WHEN 'AA-02-04' THEN '0501020204' WHEN '03-04' THEN '030401' WHEN '04-01' then '040101'           when '04-01-01' then '040102'             when '04-03' then '040301'         when '04-03-01' then '040302'         when '04-06' then '040601'            else         bethadba.dbf_retira_alfa_de_inteiros(campo)     end ,     campoDirf = case bethadba.dbf_retira_alfa_de_inteiros(nomeCampoDsk)         when '0301' then 'TOTAL_REND_INC_FERIAS'         when '0302' then 'CONTRIB_PREV_OFICIAL'         when '030301' then 'CONTRIB_PREV_PRIVADA'         when '030302' then 'CONTRIB_FAPI'         when '030303' then 'CONTRIB_FUND_PREV_SERVIDOR_PUBLICO'         when '030304' then 'CONTRIB_ENTE_PUBLICO_PATROCINADOR'         when '030401' then 'PENSAO_ALIMENTICIA'         when '030402' then 'PENSAO_ALIMENTICIA_13_SALARIO'         when '0305' then 'IRRF'         when '040101' then 'PARC_ISENTA_APOSENT'         when '040102' then 'PARC_ISENTA_APOSENT_13_SALARIO'         when '0402' then 'DIARIAS_AJUDAS_CUSTO'         when '040301' then 'PROV_APOSENT_MOLESTIA_GRAVE'         when '040302' then 'PROV_APOSENT_MOLESTIA_GRAVE_13_SALARIO'         when '0404' then 'LUCROS_DIVIDENDOS'         when '0405' then 'VALORES_PAGOS_TITULAR_SOCIO_EMPRESA'         when '040601' then 'INDENIZ_RESC_CONTRATO_TRABALHO'         when '040602' then 'INDENIZ_RESC_CONTRATO_TRABALHO_13_SALARIO'         when '040701' then 'REND_ISENTOS_OUTROS'         when '040702' then 'REND_ISENTOS_OUTROS_MEDICO_RESIDENTE'         when '050101' then 'TOTAL_REND_13_SALARIO'         when '050102' then 'IRRF_13_SALARIO'         when '05010201' then 'CONTRIB_PREV_OFICIAL_13_SALARIO'         when '0501020202' then 'CONTRIB_FAPI_13_SALARIO'         when '0501020203' then 'CONTRIB_FUND_PREV_SERVIDOR_PUBLICO_13_SALARIO'         when '0501020204' then 'CONTRIB_ENTE_PUBLICO_PATROCINADOR_13_SALARIO'         when '050301' then 'REND_SUJ_TRIB_EXCLUSIVA_OUTROS_13_SALARIO'         when '050302' then 'REND_SUJ_TRIB_EXCLUSIVA_OUTROS_13_SALARIO_MEDICO_RESIDENTE'         when '0601' then 'RRA_TOTAL_RENDIMENTOS_TRIBUTAVEIS'         when '0602' then 'RRA_EXCLUSAO_DESP_ACAO_JUDICIAL'         when '0603' then 'RRA_DEDUCAO_CONTRIB_PREV_OFICIAL'         when '0604' then 'RRA_DEDUCAO_PENSAO_ALIMENTICIA'         when '0605' then 'RRA_IRRF'         when '0606' then 'RRA_RENDIMENTOS_ISENTOS'         when '0700' then 'INFORMACOES_COMPLEMENTARES'         when 'ABOPEC' then 'ABONO_PECUNIARIO' end,         eventos =  LIST(i_eventos)     from bethadba.comprends            where campo not in ('05-01','0A-02')       and campoDirf is not null     group by campoDirf, nomeCampoDsk, chave_dsk1         union all         select chave_dsk1 = campoDirf,         nomeCampoDsk =         case campo             when '03-01' then '0601'             when '03-02' then '0603'             when '03-05' then '0605'             when '03-04' then '0604'         else             bethadba.dbf_retira_alfa_de_inteiros(campo)         end ,         campoDirf = case bethadba.dbf_retira_alfa_de_inteiros(nomeCampoDsk)                    when '0601' then 'RRA_TOTAL_RENDIMENTOS_TRIBUTAVEIS'             when '0602' then 'RRA_EXCLUSAO_DESP_ACAO_JUDICIAL'             when '0603' then 'RRA_DEDUCAO_CONTRIB_PREV_OFICIAL'             when '0604' then 'RRA_DEDUCAO_PENSAO_ALIMENTICIA'             when '0605' then 'RRA_IRRF'             when '0606' then 'RRA_RENDIMENTOS_ISENTOS' end,         eventos =  LIST(i_eventos)     from bethadba.comprends     where campo in ('03-01','03-02','03-03-01','03-03-02','03-03-03','03-03-04', '03-04','03-05')       and campoDirf is not null     group by campoDirf, nomeCampoDsk, chave_dsk1")

    quantidade = 0

    for i in resultado:
        lista_eventos = i[3].split(',')

        if len(buscar_duplicatas(lista_eventos)) > 0:
            quantidade += 1

    if quantidade == 0:
        return

    print('Configurações de dirf com eventos repetidos: '+ str(quantidade))

    return quantidade

#Verifica a descricao de motivo de alteração salarial repetindo
#Já existe um motivo de alteração salarial com a descrição informada
def motivo_alt_salarial_descricao_repetido():

    resultado = consultar(
        """
           SELECT 
                LIST(i_motivos_altsal), 
                TRIM(descricao), 
                COUNT(descricao) AS quantidade 
            FROM 
                bethadba.motivos_altsal 
            GROUP BY 
                TRIM(descricao) 
            HAVING 
                quantidade > 1
        """
    )

    quantidade = len(resultado)

    if quantidade == 0:
        return

    print('Descrição de motivo de alteração salarial repetindo: '+ str(quantidade))

    return quantidade
#-----------------------Executar---------------------#
#pessoas_sem_cpf() - Em analise
hist_funcionarios_dt_alteracoes_maior_dt_rescisao()
#cargos_sem_configuracao_ferias() - Em analise
pessoa_data_vencimento_cnh_menor_data_emissao()
caracteristicas_nome_repetido()
dependentes_grau_outros()
pessoa_data_nascimento_maior_data_admissao()
pessoas_sem_dt_nascimento()
pessoas_cnh_dt_vencimento_menor_dt_emissao()
pessoas_dt_primeira_cnh_maior_dt_nascimento()
pessoas_dt_nasc_maior_dt_nasc_responsavel()
pessoas_cpf_repetido()
pessoas_pis_repetido()
pessoas_pis_invalido()
pessoas_sem_cnpj()
ruas_nome_caracter_especial()
ruas_sem_nome()
ruas_sem_cidade()
ruas_nome_repetido()
tipos_bases_repetido()
atos_sem_numero()
atos_repetido()
cargos_sem_cbo()
vinculos_sem_esocial()
vinculos_descricao_repetido()
motivos_resc_sem_esocial()
folha_fechamento(folha_fechamento_competencia)
folhas_ferias_sem_dt_pagamento()
motivos_apos_sem_esocial()
hist_salariais_sem_salario()
variaveis_dt_inical_maior_dt_rescisao()
tipos_movpes_descricao_repetido()
tipos_afast_descricao_repetido()
hist_salariais_dt_alteracoes_maior_dt_rescisao()
hist_cargos_dt_alteracoes_maior_dt_rescisao()
tipos_afast_classif_invalida()
tipos_atos_nome_repetido()
horarios_ponto_descricao_repetido()
turmas_descricao_repetido()
niveis_organ_separador_invalido()
atos_sem_natureza_texto_juridico()
atos_dt_publicacao_fonte_menor_dt_publicacao_divulgacao()
canc_ferias_sem_tipos_afast()
config_organograma_descricao_invalida()
config_organ_descricao_repetido()
pessoas_cpf_invalido()
pessoas_cnpj_invalido()
pessoas_rg_repetido()
cargos_descricao_repetido()
bases_calc_outras_empresas_vigencia_invalida()
pessoas_email_invalido()
pessoas_enderecos_sem_numero()
funcionarios_sem_previdencia()
mediasvant_sem_composicao()
mediasvant_eve_composicao_invalida()
locais_mov_dt_inicial_menor_dt_admissao()
motivos_altponto_descricao_invalida()
afastamentos_observacao_invalida()
ferias_dt_gozo_ini_maior_dt_gozo_fin()
rescisoes_sem_motivos_apos()
grupos_nome_repetido()
func_planos_saude_vigencia_inicial_menor_vigencia_inicial_titular()
locais_trab_fone_invalido()
atos_sem_dt_inicial()
niveis_descricao_repetido()
funcionarios_cartao_ponto_repetido()
cargos_dt_nomeacao_maior_dt_posse()
funcionarios_conta_bancaria_invalida()
funcionarios_com_mais_de_uma_previdencia()
afastamentos_dt_afastamento_menor_dt_admissao()
areas_atuacao_nome_repetido()
dependentes_sem_dt_fim()
opcao_fgts_diferente_dt_admissao()
funcionarios_conta_bancaria_sem_dados()
funcionarios_maracoes_invalida()
ocorrencia_ponto_nome_repetido()
configuracao_dirf_com_eventos_repetidos()
motivo_alt_salarial_descricao_repetido()