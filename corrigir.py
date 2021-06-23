from validate_email import validate_email 
from variaveis import *
from src.functions import *
from src.database import *
import re

#Renomeia os campos adicionais com descrição repetido
def campoAdicionalDescricaoRepetido():

    resultado = select(
        """
            SELECT 
                list(i_caracteristicas), 
                TRIM(nome), 
                count(nome) AS quantidade 
            FROM 
                bethadba.caracteristicas 
            GROUP BY 
                TRIM(nome) 
            HAVING 
                quantidade > 1
        """
    )

    for i in resultado:
        ids = i[0].split(',')
        nome = i[1]

        for index, identificador in enumerate(ids):
            if index == 0:
                continue
            
            u = "UPDATE bethadba.caracteristicas SET nome = '{}'  WHERE i_caracteristicas = {};".format((nome + " |" + str(index)), identificador)

            print(u)
            updateInsertDelete(u)

#Adiciona o valor 1 - Filho para os dependentes que estão cadastrados como 10 - OUTROS
def dependentesOutros():

    updateInsertDelete(
        """
            UPDATE 
                bethadba.dependentes
            SET
                grau = 1
            WHERE 
                grau = 10;
        """
    )
    
#Adiciona a data '1900-01-01' e se tiver responsavel adiciona a data de nascimento do mesmo
def pessoaDataNascimentoNulo():

    #Coloca a data '1900-01-01' nas datas das pessoas com data de nascimento maior que data de admissão
    #pessoaDataNascimentoMaiorDataAdmissao
    updateInsertDelete(
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
                        pf.dt_nascimento > f.dt_admissao
                ) AS subPessoa
            WHERE 
                pff.i_pessoas = subPessoa.i_pessoas;
        """
    )

    #Coloca a data '1900-01-01' nas datas nulas
    #pessoaDataNascimentoNulo
    updateInsertDelete(
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

    #Atualiza a data de nascimento de acordo com a do responsavel
    #pessoaDataNascimentoMaiorDataNascimentoResponsavel
    updateInsertDelete(
        """
            UPDATE 
                bethadba.pessoas_fisicas pff
            SET 
                pff.dt_nascimento = subPessoa.dataNascimentoPai
            FROM 
                ( 
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
                ) AS subPessoa
            WHERE 
                pff.i_pessoas = subPessoa.idFilho; 
        """
    )

    #Atualiza a data de dependencia acordo com a pessoa
    #pessoaDataNascimentoMaiorDataDependecia
    updateInsertDelete(
        """
            UPDATE 
                bethadba.dependentes dpe
            SET 
                dpe.dt_ini_depende = subPessoa.dt_nascimento
            FROM 
                ( 
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
                ) AS subPessoa
            WHERE 
                dpe.i_dependentes = subPessoa.i_dependentes;
        """
    )

#Busca a data de vencimento da CNH menor que a data de emissão da 1ª habilitação!
def pessoaDataVencimentoCNHMenorDataEmissao():

    updateInsertDelete(
        """
            UPDATE
                bethadba.hist_pessoas_fis
            SET 
                dt_vencto_cnh = dt_primeira_cnh+1
            WHERE
                dt_primeira_cnh >= dt_vencto_cnh; 
        """
    )

    updateInsertDelete(
        """
            UPDATE
                bethadba.pessoas_fis_compl
            SET 
                dt_vencto_cnh = dt_primeira_cnh+1
            WHERE 
                dt_primeira_cnh >= dt_vencto_cnh; 
        """
    )
    print("Data de emissao da CNH atualizada!")

#Busca pessoas com data de nascimento maior que emissão da 1ª habilitação!
def pessoaDataPrimeiraCNHMaiorNascimento():

    updateInsertDelete(
        """
            UPDATE 
                bethadba.hist_pessoas_fis
            SET    
                hist_pessoas_fis.dt_primeira_cnh = NULL
            FROM   
                (SELECT i_pessoas,
                        (SELECT a.dt_nascimento
                            FROM   bethadba.pessoas_fisicas AS a
                            WHERE  a.i_pessoas = hpf.i_pessoas) nascimento,
                        dt_emissao_cnh,
                        NULL AS novaDataCNH
                    FROM   bethadba.hist_pessoas_fis hpf
                    WHERE  nascimento >= dt_primeira_cnh) AS d
            WHERE  
                hist_pessoas_fis.i_pessoas = d.i_pessoas;
        """
    )

    updateInsertDelete(
        """
            UPDATE 
                bethadba.pessoas_fis_compl
            SET    
                pessoas_fis_compl.dt_primeira_cnh = NULL
            FROM   
                (SELECT i_pessoas,
                        (SELECT a.dt_nascimento
                            FROM   bethadba.pessoas_fisicas AS a
                            WHERE  a.i_pessoas = hpf.i_pessoas) nascimento,
                        dt_emissao_cnh,
                        NULL AS novaDataCNH
                    FROM   bethadba.pessoas_fis_compl hpf
                    WHERE  nascimento >= dt_primeira_cnh) AS d
            WHERE  
                pessoas_fis_compl.i_pessoas = d.i_pessoas;
        """
    )
    print("Data da primeira CNH atualizada!")

#Gera CPF aleatorio para pessoas com CPF nulo
def cpfNulo():

    resultado = select(
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
        idPessoa = i[0]

        u = "UPDATE bethadba.pessoas_fisicas SET cpf = {} WHERE i_pessoas = {};".format(gerarCpf(False), idPessoa)
        
        print(u)
        updateInsertDelete(u)

#Coloca nulo para um dos CPF's repetidos
#As Pessoas (0,0) possuem o mesmo CPF!
def cpfRepetido():

    resultado = select(
        """
            SELECT
                list(pf.i_pessoas),
                cpf,
                count(cpf) AS quantidade
            FROM 
                bethadba.pessoas_fisicas pf 
            GROUP BY 
                cpf 
            HAVING 
                quantidade > 1
        """
    )

    for i in resultado:
        idsPessoa = i[0].split(',')

        for index, idPessoa in enumerate(idsPessoa):
            if index == 0:
                continue
            
            u = "UPDATE bethadba.pessoas_fisicas SET cpf = NULL WHERE i_pessoas = {};".format(idPessoa)

            print(u)
            updateInsertDelete(u)

#Coloca nulo para um dos PIS's repetidos
#As Pessoas (0,0) possuem o mesmo número do PIS!
def pisRepetido():

    resultado = select(
        """
            SELECT
                list(pf.i_pessoas),
                num_pis,
                count(num_pis) AS quantidade
            FROM 
                bethadba.pessoas_fisicas pf 
            GROUP BY 
                num_pis 
            HAVING 
                quantidade > 1
        """
    )

    for i in resultado:
        idsPessoa = i[0].split(',')

        for index, idPessoa in enumerate(idsPessoa):
            if index == 0:
                continue
            
            u = "UPDATE bethadba.pessoas_fisicas SET num_pis = NULL WHERE i_pessoas = {};".format(idPessoa)

            print(u)
            updateInsertDelete(u)

#Verifica se o PIS é valido
#PIS inválido
def pisInvalido():

    resultado = select(
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
        idPessoa = i[0]
        pis = i[1]

        if not validarPis(pis):
            u = "UPDATE bethadba.pessoas_fisicas SET num_pis = NULL WHERE i_pessoas = {};".format(idPessoa)

            print(u)
            updateInsertDelete(u)          

#Gera CNPJ aleatorio para pessoas com CNPJ nulo
def cnpjNulo():

    resultado = select(
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
        idPessoa = i[0]

        updateInsertDelete(
            """
                UPDATE bethadba.pessoas_juridicas SET cnpj = {} WHERE i_pessoas = {};
            """.format(gerarCnpj(False), idPessoa)
        )

#Renomeia a descrição dos logradouros que tem caracter especial no inicio da descrição
def logradourosDescricaoCaracterEspecial():

    updateInsertDelete(
        """
            UPDATE 
                bethadba.ruas
            SET 
                nome = SUBSTRING(nome, 2)   
            WHERE 
                SUBSTRING(nome, 1, 1) in ('[', ']');
        """
    )

#Renomeia os logradouros com descrição repetidos
def logradourosDescricaoRepetido():

    resultado = select(
        """
            SELECT 
                list(i_ruas), 
                TRIM(nome),
                i_cidades, 
                count(nome) AS quantidade
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
        ids = i[0].split(',')
        nome = i[1]

        for index, identificador in enumerate(ids):
            if index == 0:
                continue
            
            u = "UPDATE bethadba.ruas SET nome = '{}'  WHERE i_ruas = {};".format((nome + " |" + str(index)), identificador)

            print(u)
            updateInsertDelete(u)

#Renomeia os tipos bases repetidos
def tiposBasesRepetido():

    resultado = select(
        """
            SELECT 
                list(i_tipos_bases), 
                nome, 
                count(nome) AS quantidade
            FROM 
                bethadba.tipos_bases 
            GROUP BY 
                nome 
            HAVING 
                quantidade > 1;
        """
    )

    for i in resultado:
        ids = i[0].split(',')
        nome = i[1]

        for index, identificador in enumerate(ids):
            if index == 0:
                continue
            
            u = "UPDATE bethadba.tipos_bases SET nome = '{}'  WHERE i_tipos_bases = {};".format((nome + " |" + str(index)), identificador)

            print(u)
            updateInsertDelete(u)

#Coloca a cidade da entidade
def logradourosSemCidade():

    updateInsertDelete(
        """
            UPDATE 
                bethadba.ruas
            SET
                i_cidades = (SELECT TOP 1 i_cidades FROM bethadba.entidades)
            WHERE 
                i_cidades IS NULL;
        """
    )

#Renomeia os atos com número nulo
def atosNumeroNulo():

    resultado = select(
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
        idAto = i[0]

        numeroAto = "NAO INFOR. " + str(index)
        
        u = "UPDATE bethadba.atos SET num_ato = '{}'  WHERE i_atos = {};".format(numeroAto, idAto)

        print(u)
        updateInsertDelete(u)

#Renomeia os atos repetidos
def atosRepetido():

    resultado = select(
        """
            SELECT 
                list(i_atos),
                num_ato,
                i_tipos_atos,
                count(num_ato) AS quantidade
            FROM 
                bethadba.atos 
            GROUP BY 
                num_ato,
                i_tipos_atos 
            HAVING 
                quantidade > 1;
        """
    )

    for i in resultado:
        ids = i[0].split(',')
        numeroAto = i[1]
        
        for index, identificador in enumerate(ids):

            if index == 0:
                continue
            
            numeroAtoNovo = numeroAto + " |" + str(index) 

            if len(numeroAto) > 13:
                numeroAtoNovo = numeroAto[:13] + " |" + str(index) 

            u = "UPDATE bethadba.atos SET num_ato = '{}'  WHERE i_atos = {};".format(numeroAtoNovo, identificador)

            print(u)
            updateInsertDelete(u)

#Adiciona o CBO mais utilizado no cargo
def cargoCboNulo():

    updateInsertDelete(
        """
            UPDATE 
                bethadba.cargos 
            SET 
                i_cbo = (SELECT TOP 1 i_cbo FROM bethadba.cargos GROUP BY i_cbo ORDER BY count(i_cbo) DESC)
            WHERE
                i_cbo IS NULL; 
        """
    )

#Adiciona uma categoria eSocial qualquer no vinculo empregaticio
def eSocialNuloVinculoEmpregaticio():

    updateInsertDelete(
        """
            UPDATE 
                bethadba.vinculos
            SET 
                categoria_esocial = '101'
            WHERE 
                categoria_esocial IS NULL 
                AND tipo_func <> 'B';                  
        """
    )

#Renomeia os vinculos empregaticios repetidos
def vinculoEmpregaticioRepetido():

    resultado = select(
        """
            SELECT 
                list(i_vinculos), 
                descricao,
                count(descricao) AS quantidade 
            FROM 
                bethadba.vinculos 
            GROUP BY 
                descricao 
            HAVING
                quantidade > 1;
        """
    )

    for i in resultado:
        ids = i[0].split(',')
        descricao = i[1]
        
        for index, identificador in enumerate(ids):
            
            if index == 0:
                continue
            
            descricaoNovo = descricao + " |" + str(index) 

            if len(descricao) > 26:
                descricaoNovo = descricao[:26] + " |" + str(index) 

            u = "UPDATE bethadba.vinculos SET descricao = '{}'  WHERE i_vinculos = {};".format(descricaoNovo, identificador)
            
            print(u)
            updateInsertDelete(u)

#Adiciona uma categoria eSocial qualquer no motivo de rescisão
def eSocialNuloMotivoRescisao():

    updateInsertDelete(
        """
            UPDATE 
                bethadba.motivos_resc
            SET 
                categoria_esocial = '02'
            WHERE 
                categoria_esocial IS NULL;                
        """
    )

#Fecha as folha que não foram fechadas confome competencia passada por parametro
def fechamentoFolha(competencia):
    print('Pode demorar um pouco!')

    updateInsertDelete(
        """
            UPDATE 
                bethadba.dados_calc SET dt_fechamento = date(year(i_competencias)||
                (if month(i_competencias) < 10 then '0'+cast(month(i_competencias) as varchar) else cast(month(i_competencias) as varchar) endif)||
                (if month(i_competencias) = 2 then '28' else '30' endif))
            WHERE 
                i_competencias < {0} AND dt_fechamento is null; 

            COMMIT;

            UPDATE 
                bethadba.processamentos SET dt_fechamento = date(year(i_competencias)||
                (if month(i_competencias) < 10 then '0'+cast(month(i_competencias) as varchar) else cast(month(i_competencias) as varchar) endif)||
                (if month(i_competencias) = 2 then '28' else '30' endif))
            WHERE 
                i_competencias < {0} AND dt_fechamento is null; 
            
            COMMIT;

            UPDATE 
                bethadba.processamentos SET pagto_realizado = 'S'
            WHERE 
                i_competencias < {0} AND pagto_realizado = 'N';                 
        """.format(competencia)
    )

#Verifica as folhas de ferias sem data de pagamento
#A data de pagamento é obrigatória
def folhaFeriasDataPagamentoNulo():
    print("Não foi feito ainda: folhaFeriasDataPagamentoNulo()")

#Adiciona uma categoria eSocial qualquer no motivo de aposentadoria
def eSocialNuloMotivoAposentadoria():

    updateInsertDelete(
        """
            UPDATE 
                bethadba.motivos_apos
            SET 
                categoria_esocial = '38'
            WHERE 
                categoria_esocial IS NULL;                
        """
    )

#Coloca R$0,01 nos historicos salariais com salario zerado ou nulo
def historicoSalarialZerado():

    updateInsertDelete(
        """
            UPDATE 
                bethadba.hist_salariais
            SET 
                salario = 0.01
            WHERE 
                salario IN (0, NULL);            
        """
    )

#Coloca data de rescisão na data inicial se a mesma for maior;
#Coloca a data de rescisão na data final
def dataFinalLancamentoMaiorDataRescisao():

    resultado = select(
        """
            SELECT 
                v.i_funcionarios,
                v.i_entidades, 
                v.i_eventos,
                v.i_processamentos,
                v.i_tipos_proc, 
                f.dt_admissao,
                DATEFORMAT(f.dt_admissao,'01/MM/yyyy') AS dt_admissao_formatada,
                r.dt_rescisao,
                DATEFORMAT(r.dt_rescisao,'01/MM/yyyy') AS dt_resc_formatada,
                v.dt_inicial,
                DATEFORMAT(v.dt_inicial,'dd/MM/yyyy') AS dt_inicial_formatada,
                v.dt_final,
                DATEFORMAT(v.dt_final,'dd/MM/yyyy') AS dt_final_formatada
            FROM 
                bethadba.rescisoes r 
            INNER JOIN  
                bethadba.variaveis v ON (r.i_funcionarios = v.i_funcionarios AND r.i_entidades = v.i_entidades)
            INNER JOIN  
                bethadba.funcionarios f ON (r.i_funcionarios = f.i_funcionarios AND r.i_entidades = f.i_entidades)
            WHERE
                v.dt_final > DATEFORMAT(r.dt_rescisao, 'yyyy-MM-01') OR v.dt_inicial > DATEFORMAT(r.dt_rescisao, 'yyyy-MM-01');
        """
    )

    for i in resultado:
        idFuncionario = i[0]  
        idEntidade = i[1]
        idEvento = i[2]
        idProcessamento = i[3]
        idTipoProcessamento = i[4]
        dataAdmissao = str(i[5])[:8] + "01" 
        dataAdmissaoFormatada = int(dataAdmissao.replace('-', ''))
        dataRescisao = str(i[7])[:8] + "01"
        dataRescisaoFormatada = int(dataRescisao.replace('-', ''))
        dataInicial = str(i[9])
        dataInicialFormatada = int(dataInicial.replace('-', ''))
        dataFinal = i[11]
        dataInicialNovo = dataInicial

        if dataInicialFormatada > dataRescisaoFormatada:
            dataInicialNovo = dataRescisao
        
        if dataInicialFormatada < dataAdmissaoFormatada:
            dataInicialNovo = dataAdmissao

        u = """
            UPDATE 
                bethadba.variaveis 
            SET 
                dt_inicial = '{}', dt_final = '{}', i_variaveis_import = null 
            WHERE
                i_funcionarios = {} AND 
                i_entidades = {} AND 
                i_eventos = {} AND
                i_processamentos = {} AND 
                i_tipos_proc = {} AND 
                dt_inicial = '{}' AND
                dt_final = '{}';
        """.format(dataInicialNovo, dataRescisao, idFuncionario, idEntidade, idEvento, idProcessamento, idTipoProcessamento, dataInicial, dataFinal)

        s = """
            SELECT 
                * 
            FROM 
                bethadba.variaveis 
            WHERE
                i_funcionarios = {} AND 
                i_entidades = {} AND 
                i_eventos = {} AND
                i_processamentos = {} AND 
                i_tipos_proc = {} AND 
                dt_inicial = '{}' AND
                dt_final = '{}';           
        """.format(idFuncionario, idEntidade, idEvento, idProcessamento, idTipoProcessamento, dataInicialNovo, dataRescisao)

        if len(select(s)) > 0:
            updateInsertDelete(
                """
                    DELETE FROM bethadba.variaveis WHERE i_funcionarios = {} AND i_entidades = {} AND i_eventos = {} AND i_processamentos = {} AND i_tipos_proc = {} AND dt_inicial = '{}' AND dt_final = '{}'; 
                """.format(idFuncionario, idEntidade, idEvento, idProcessamento, idTipoProcessamento, dataInicial, dataFinal)
            )

        else:
            updateInsertDelete(u)

#Renomeia as movimetação de pessoal repetidos
def movimentacaoPessoalRepetido():

    resultado = select(
        """
            SELECT 
                list(i_tipos_movpes), 
                descricao,
                count(descricao) AS quantidade 
            FROM 
                bethadba.tipos_movpes 
            GROUP BY 
                descricao 
            HAVING
                quantidade > 1;
        """
    )

    for i in resultado:
        ids = i[0].split(',')
        descricao = i[1]
        
        for index, identificador in enumerate(ids):

            if index == 0:
                continue
            
            descricaoNovo = descricao + " |" + str(index) 

            if len(descricao) > 47:
                descricaoNovo = descricao[:47] + " |" + str(index) 

            u = "UPDATE bethadba.tipos_movpes SET descricao = '{}'  WHERE i_tipos_movpes = {};".format(descricaoNovo, identificador)
            
            print(u)
            updateInsertDelete(u)
        
#Renomeia os tipos de afastamentos repetidos
def tipoAfastamentoRepetido():

    resultado = select(
        """
            SELECT 
                list(i_tipos_afast), 
                TRIM(descricao),
                count(descricao) AS quantidade 
            FROM 
                bethadba.tipos_afast 
            GROUP BY 
                TRIM(descricao)
            HAVING
                quantidade > 1;
        """
    )

    for i in resultado:
        ids = i[0].split(',')
        descricao = i[1]
        
        for index, identificador in enumerate(ids):
            
            if index == 0:
                continue
            
            descricaoNovo = descricao + " |" + str(index) 

            if len(descricao) > 47:
                descricaoNovo = descricao[:47] + " |" + str(index) 

            u = "UPDATE bethadba.tipos_afast SET descricao = '{}'  WHERE i_tipos_afast = {};".format(descricaoNovo, identificador)
            
            print(u)
            updateInsertDelete(u)

#Coloca a data de rescisão na data de alteração
def alteracaoFuncionarioMaiorDataRescisaoA():

    updateInsertDelete(
        """
            UPDATE 
                bethadba.hist_funcionarios hff
            SET 
                hff.dt_alteracoes = historico.dt_alteracoes_novo
            FROM 
                ( 
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
                    ORDER BY 
                        hf.dt_alteracoes DESC
                ) AS historico
            WHERE
                hff.i_funcionarios = historico.i_funcionarios AND
                hff.i_entidades = historico.i_entidades AND
                hff.dt_alteracoes = historico.dt_alteracoes;
        """
    )

#Coloca a data de rescisão na data de alteração
def alteracaoFuncionarioMaiorDataRescisao():

    resultado = select(
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
            ORDER BY 
            	hf.i_funcionarios, hf.dt_alteracoes DESC;
        """
    )

    for i in resultado:
        idFuncionario = i[0]    
        idEntidade = i[1]               
        dtAlteracoes = i[2]
        dtRescisao = i[3] 
        dtAlteracoesNovo = i[4]

        u = """
            UPDATE
                bethadba.hist_funcionarios
            SET
                dt_alteracoes = '{}'
            WHERE
                i_funcionarios = {} AND
                i_entidades = {} AND
                dt_alteracoes = '{}';
        """.format(dtAlteracoesNovo, idFuncionario, idEntidade, dtAlteracoes)

        s = """
            SELECT 
                *
            FROM
                bethadba.hist_funcionarios
            WHERE 
                i_funcionarios = {} AND 
                i_entidades = {} AND
                dt_alteracoes = '{}';

        """.format(idFuncionario, idEntidade, dtAlteracoesNovo)

        if len(select(s)) > 0:
            updateInsertDelete(
                """
                    DELETE FROM bethadba.hist_funcionarios WHERE i_funcionarios = {} AND i_entidades = {} AND dt_alteracoes = '{}';
                """.format(idFuncionario, idEntidade, dtAlteracoes)
            )

        else:
            updateInsertDelete(u)

#Coloca a data de rescisão na data de alteração
def alteracaoSalarialMaiorDataRescisao():

    resultado = select(
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
                hs.dt_alteracoes > STRING(r.dt_rescisao, ' 23:59:59')
            ORDER BY 
                hs.dt_alteracoes DESC;
        """
    )

    for i in resultado:
        idFuncionario = i[0]    
        idEntidade = i[1]               
        dtAlteracoes = i[2]
        dtRescisao = i[3] 
        dtAlteracoesNovo = i[4]

        u = """
            UPDATE
                bethadba.hist_salariais
            SET
                dt_alteracoes = '{}'
            WHERE
                i_funcionarios = {} AND 
                i_entidades = {} AND
                dt_alteracoes = '{}';

        """.format(dtAlteracoesNovo, idFuncionario, idEntidade, dtAlteracoes)

        s = """
            SELECT 
                *
            FROM
                bethadba.hist_salariais
            WHERE 
                i_funcionarios = {} AND 
                i_entidades = {} AND
                dt_alteracoes = '{}';

        """.format(idFuncionario, idEntidade, dtAlteracoesNovo)

        if len(select(s)) > 0:
            updateInsertDelete(
                """
                    DELETE FROM bethadba.hist_salariais WHERE i_funcionarios = {} AND i_entidades = {} AND dt_alteracoes = '{}';
                """.format(idFuncionario, idEntidade, dtAlteracoes)
            )

        else:
            updateInsertDelete(u)

#Coloca a data de rescisão na data de alteração
def alteracaoCargoMaiorDataRescisao():

    resultado = select(
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
                hc.dt_alteracoes > STRING(r.dt_rescisao, ' 23:59:59')
            ORDER BY 
                hc.dt_alteracoes DESC;
        """
    )

    for i in resultado:
        idFuncionario = i[0]    
        idEntidade = i[1]               
        dtAlteracoes = i[2]
        dtRescisao = i[3] 
        dtAlteracoesNovo = i[4]

        u = """
            UPDATE
                bethadba.hist_cargos
            SET
                dt_alteracoes = '{}'
            WHERE
                i_funcionarios = {} AND 
                i_entidades = {} AND
                dt_alteracoes = '{}';
        """.format(dtAlteracoesNovo, idFuncionario, idEntidade, dtAlteracoes)

        s = """
            SELECT 
                *
            FROM
                bethadba.hist_cargos
            WHERE 
                i_funcionarios = {} AND 
                i_entidades = {} AND
                dt_alteracoes = '{}';

        """.format(idFuncionario, idEntidade, dtAlteracoesNovo)

        if len(select(s)) > 0:
            updateInsertDelete(
                """
                    DELETE FROM bethadba.hist_cargos WHERE i_funcionarios = {} AND i_entidades = {} AND dt_alteracoes = '{}';
                """.format(idFuncionario, idEntidade, dtAlteracoes)
            )

        else:
            updateInsertDelete(u)
        
#Coloca 7 - (Licença SEM vencimentos) para as classificações que estão com código errado no tipo de afastamento
def classificacaoErradaTipoAfastamento():

    updateInsertDelete(
        """
            UPDATE
                bethadba.tipos_afast
            SET
                classif = 7
            WHERE
                classif IN (1, NULL);   
        """
    )

#Renomeia os tipos de atos repetidos
def tipoAtoRepetido():

    resultado = select(
        """
            SELECT 
                list(i_tipos_atos), 
                nome,
                count(nome) AS quantidade 
            FROM 
                bethadba.tipos_atos 
            GROUP BY 
                nome 
            HAVING
                quantidade > 1;
        """
    )

    for i in resultado:
        ids = i[0].split(',')
        descricao = i[1]
        
        for index, identificador in enumerate(ids):

            if index == 0:
                continue
            
            descricaoNovo = descricao + " |" + str(index) 

            if len(descricao) > 37:
                descricaoNovo = descricao[:37] + " |" + str(index) 

            u = "UPDATE bethadba.tipos_atos SET nome = '{}' WHERE i_tipos_atos = {};".format(descricaoNovo, identificador)
            
            print(u)
            updateInsertDelete(u)

#Renomeia as descrições repetidas no horario ponto
def descricaoHorarioPontoRepetido():

    resultado = select(
        """
            SELECT 
                list(i_entidades), 
                list(i_horarios_ponto), 
                descricao,
                count(descricao) AS quantidade 
            FROM 
                bethadba.horarios_ponto 
            GROUP BY 
                descricao 
            HAVING
                quantidade > 1;
        """
    )

    for i in resultado:
        idsEntidade = i[0].split(',')
        idsHorarioPonto = i[1].split(',')
        descricao = i[2]
        
        for index in range(len(idsEntidade)):
            
            if index == 0:
                continue
            
            descricaoNovo = descricao + " |" + str(index)

            if len(descricao) > 47:
                descricaoNovo = descricao[:47] + " |" + str(index) 

            u = """
                UPDATE 
                    bethadba.horarios_ponto 
                SET 
                    descricao = '{}' 
                WHERE 
                    i_entidades = {} AND i_horarios_ponto = {};
            """.format(descricaoNovo, idsEntidade[index], idsHorarioPonto[index])
            
            print(u)
            updateInsertDelete(u)

#Renomeia as descrições repetidas na turma
def descricaoTurmaRepetido():

    resultado = select(
        """
            SELECT 
                list(i_entidades), 
                list(i_turmas), 
                descricao,
                count(descricao) AS quantidade 
            FROM 
                bethadba.turmas 
            GROUP BY 
                descricao 
            HAVING
                quantidade > 1;
        """
    )

    for i in resultado:
        idsEntidade = i[0].split(',')
        idsTurma = i[1].split(',')
        descricao = i[2]
        
        for index in range(len(idsEntidade)):
            
            if index == 0:
                continue
            
            descricaoNovo = descricao + " |" + str(index)

            if len(descricao) > 57:
                descricaoNovo = descricao[:57] + " |" + str(index) 

            u = """
                UPDATE 
                    bethadba.turmas 
                SET 
                    descricao = '{}' 
                WHERE 
                    i_entidades = {} AND i_turmas = {};
            """.format(descricaoNovo, idsEntidade[index], idsTurma[index])
            
            print(u)
            updateInsertDelete(u)

#Coloca um ponto (.) nos separadores nulos
def nivelOrganogramaSeparadorNulo():

    updateInsertDelete(
        """
            UPDATE 
                bethadba.niveis_organ 
            SET 
                separador_nivel = '.'
            WHERE
                separador_nivel IS NULL;
        """
    )

#Adiciona a natureza de texto juridico mais utilizada no ato
def atoNaturezaTextoJuridicoNulo():

    updateInsertDelete(
        """
            UPDATE 
                bethadba.atos 
            SET 
                i_natureza_texto_juridico = (SELECT TOP 1 i_natureza_texto_juridico FROM bethadba.atos GROUP BY i_natureza_texto_juridico ORDER BY count(i_natureza_texto_juridico) DESC)
            WHERE
                i_natureza_texto_juridico IS NULL; 
        """
    )

#Coloca a data de publicação do ato na data de fonte de divulgação
def atoFonteDivulgacaoMenorPublicacao():

    updateInsertDelete(
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

#Inseri um tipo de afastamento na configuração do cancelamento de férias
def tipoAfastamentoConfiguracaoCancelamentoFerias():

    updateInsertDelete(
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

#Renomeia descricao de cofiguração de organograma maior que 30 caracteres
def descricaoConfigOrganogramaMaior30():

    updateInsertDelete(
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

#Renomeia descricao de cofiguração de organograma repetido
def descricaoConfigOrganogramaRepetido():

    resultado = select(
        """
            SELECT 
                list(i_config_organ), 
                descricao, 
                count(descricao) AS quantidade 
            FROM 
                bethadba.config_organ 
            GROUP BY 
                descricao 
            HAVING 
                quantidade > 1
        """
    )

    for i in resultado:
        ids = i[0].split(',')
        nome = i[1]

        for index, identificador in enumerate(ids):

            if index == 0:
                continue
            
            nomeNovo = nome + " |" + str(index) 

            if len(nome) > 27:
                nomeNovo = nome[:27] + " |" + str(index) 
            
            u = "UPDATE bethadba.config_organ SET descricao = '{}'  WHERE i_config_organ = {};".format(nomeNovo, identificador)

            print(u)
            updateInsertDelete(u)

#Adiciona um CPF valido
def cpfInvalido():

    resultado = select(
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
        idPessoa = i[0]
        cpf = i[1]
       
        if not validarCpf(cpf):
            u = "UPDATE bethadba.pessoas_fisicas SET cpf = NULL WHERE i_pessoas = {};".format(idPessoa)

            print(u)
            updateInsertDelete(u)

#Adiciona um CNPJ valido
def cnpjInvalido():

    resultado = select(
        """
           SELECT
                i_pessoas,
                cnpj
            FROM 
                bethadba.pessoas_juridicas
        """
    )

    for i in resultado:
        idPessoa = i[0]
        cnpj = i[1]
       
        if not validarCnpj(cnpj):
            u = "UPDATE bethadba.pessoas_juridicas SET cnpj = '{}'  WHERE i_pessoas = {};".format(gerarCnpj(), idPessoa)

            print(u)
            updateInsertDelete(u)
            
#Adiciona um RG aleatorio
def RgRepetido():

    resultado = select(
        """
            SELECT
                list(i_pessoas),
                rg,
                count(rg) AS quantidade
            FROM 
                bethadba.pessoas_fisicas 
            GROUP BY 
                rg 
            HAVING 
                quantidade > 1
        """
    )

    for i in resultado:
        ids = i[0].split(',')
        rg = i[1]

        for index, identificador in enumerate(ids):
            if index == 0:
                continue
            
            u = "UPDATE bethadba.pessoas_fisicas SET rg = '{}'  WHERE i_pessoas = {};".format(gerarRg(), identificador)

            print(u)
            updateInsertDelete(u)

#Renomeia os cargos com descricão repetidos
#Já existe um cargo com a descrição informada
def cargoDescricaoRepetido():

    resultado = select(
        """
            SELECT
                list(i_cargos),
                list(i_entidades),
                nome,
                count(nome) AS quantidade
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
        """.format(idEntidadesAgrupadas)
    )

    for i in resultado:
        idsCargo = i[0].split(',')
        idsEntidade = i[1].split(',')
        nome = i[2]
        
        for index in range(len(idsEntidade)):
            
            if index == 0:
                continue
            
            nomeNovo = nome + " |" + str(index)

            if len(nome) > 97:
                nomeNovo = nome[:97] + " |" + str(index) 

            u1 = """
                UPDATE 
                    bethadba.cargos 
                SET 
                    nome = '{}' 
                WHERE 
                    i_entidades = {} AND i_cargos = {};
            """.format(nomeNovo, idsEntidade[index], idsCargo[index])


            u2 = """
                UPDATE 
                    bethadba.hist_cargos_cadastro 
                SET 
                    nome = '{}' 
                WHERE 
                    i_entidades = {} AND i_cargos = {};
            """.format(nomeNovo, idsEntidade[index], idsCargo[index])


            print(u1)
            print(u2)

            updateInsertDelete(u1)
            updateInsertDelete(u2)
            
#Adiciona um valor fixo para o termino de vigencia maior que 2099
#Essa verificação é necessaria para não dar loop ao migrar a pessoa fisica
def terminoVigenciaMaior2099():

    updateInsertDelete(
        """
            UPDATE 
                bethadba.bases_calc_outras_empresas
            SET 
                dt_vigencia_fin = '2099-01-01'   
            WHERE
                dt_vigencia_fin > 20990101;        
        """
    )

#Remove os emails invalidos
def emailInvalido():

    resultado = select(
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
        idPessoa = i[0]
        email = i[1]

        if not validate_email(email) or len(email) < 5:

            u = "UPDATE bethadba.pessoas SET email = NULL WHERE i_Pessoas = {};".format(idPessoa)

            print(u)
            updateInsertDelete(u)

#Remove o número do endereço que está vazio
def numeroEnderecoVazio():

    updateInsertDelete(
        """
            UPDATE 
                bethadba.pessoas_enderecos
            SET 
                numero = null
            WHERE
                numero = '';    
        """
    )

#Adiona um nome aleatorio para o nome da rua que está vazio
def nomeRuaVazio():

    updateInsertDelete(
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

#Adiciona previdencia federal para os funcionarios sem previdencia
def funcionariosSemPrevidencia():
    
    updateInsertDelete(
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
        """.format(idEntidadesAgrupadas)
    )

#Exclui os eventos de média/vantagem que não tem eventos vinculados
#Os eventos de composição da média são obrigatórios
def eventoMediaVantagemSemComposicao():

    resultado = select(
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
        updateInsertDelete(d)

#Exclui os eventos de média/vantagem pai que estão vinculados a outros
def eventoMediaVantagemComposicao():

    resultado = select(
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
        idEventosMedias = i[0]
        idEventos = i[1]
        
        d = "DELETE FROM bethadba.mediasvant_eve WHERE i_eventos_medias = {} AND i_eventos = {};".format(idEventosMedias, idEventos)
        
        print(d)
        updateInsertDelete(d)

#Verifica a data de admissão da matrícula se é posterior a data de início da matrícula nesta lotação física
def dataAdmissaoMatriculaMaiorDataLotacaoFisica():

    updateInsertDelete(
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
                        f.dt_admissao > lm.dt_inicial 
                ) AS lotacaoFisica
            WHERE 
                lmv.i_entidades = lotacaoFisica.i_entidades AND
                lmv.i_funcionarios = lotacaoFisica.i_funcionarios AND
                lmv.dt_inicial = lotacaoFisica.dt_inicial AND
                lmv.i_locais_trab = lotacaoFisica.i_locais_trab;
        """
    )

#Limita a descrição do motivo de alteração do ponto em 30 caracteres
#A descrição não pode conter mais de 30 caracteres
def descricaoMotivoAlteracaoPontoMaior30():

    updateInsertDelete(
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
    
#Limita o numero de caracteres em 150 no motivo dos afastamentos
def observacaoAfastamentoMaior150():

    updateInsertDelete(
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

#Verifica a data inicial no afastamento se é maior que a data final 
#A quantidade de dias não pode ser menor que 0
def dataInicialAfastamentoMaiorDataFinal():

    updateInsertDelete(
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
                        dt_gozo_ini > dt_gozo_fin 
                ) AS afastamento
            WHERE 
                f.i_entidades = afastamento.i_entidades AND
                f.i_funcionarios = afastamento.i_funcionarios AND
                f.i_ferias = afastamento.i_ferias;    
        """
    )

#Adiciona o motivo de aposentadoria 1 - Aposentadoria por tempo de serviço, com rescisão contratual
#O motivo de rescisão é obrigatório
def motivoAposentadoriaNulo():

    updateInsertDelete(
        """
            UPDATE
                bethadba.rescisoes
            SET
                i_motivos_apos = 1
            WHERE
                i_motivos_resc = 7 AND 
                i_motivos_apos IS NULL;                                    
        """
    )

#Renomeia os grupos funcionais repetidos
def gruposFuncionaisRepetido():

    resultado = select(
        """
            SELECT
                list(i_entidades),
                list(i_grupos),
                nome,
                count(nome) AS quantidade
            FROM 
                bethadba.grupos
            WHERE
                i_entidades IN ({}) 
            GROUP BY 
                nome 
            HAVING 
                quantidade > 1
        """.format(idEntidadesAgrupadas)
    )

    for i in resultado:
        idsEntidade = i[0].split(',')
        idsGrupo = i[1].split(',')
        nome = i[2]
        
        for index in range(len(idsEntidade)):

            if index == 0:
                continue
            
            nomeNovo = nome + " |" + str(index)

            if len(nome) > 57:
                nomeNovo = nome[:57] + " |" + str(index) 

            u = """
                UPDATE 
                    bethadba.grupos 
                SET 
                    nome = '{}' 
                WHERE 
                    i_entidades = {} AND i_grupos = {};
            """.format(nomeNovo, idsEntidade[index], idsGrupo[index])
            
            print(u)
            updateInsertDelete(u)


def dataInicialDependenteMaiorTitular():

    updateInsertDelete(
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
                        vigencia_inicial_titular = (select vigencia_inicial FROM bethadba.func_planos_saude WHERE i_sequenciais = 1 AND i_funcionarios = fps.i_funcionarios)
                    FROM 
                        bethadba.func_planos_saude fps 
                    WHERE 
                        fps.i_sequenciais != 1 AND 
                        fps.vigencia_inicial < vigencia_inicial_titular 
                ) AS plano_saude
            WHERE 
                fp.i_entidades = plano_saude.i_entidades AND
                fp.i_funcionarios = plano_saude.i_funcionarios AND
                fp.i_pessoas = plano_saude.i_pessoas AND
                fp.i_sequenciais = plano_saude.i_sequenciais;    
        """
    ) 

#Remove caracteres especiais e espaços para que o número do telefone seja menor ou igual a 11
def telefoneLotacaoFisicaMaior11():

    resultado = select(
        """
            SELECT 
                i_entidades,
                i_locais_trab,
                fone,
                LENGTH(fone) AS quantidade
            FROM 
                bethadba.locais_trab
            WHERE 
                quantidade > 11     
        """
    )

    for i in resultado:
        idEntidade = i[0]
        idLotacaoFisica = i[1]
        telefone = i[2]

        telefone = re.sub('[^0-9]', '', telefone)

        telefone = telefone[(len(telefone) - 8):]

        u = "UPDATE bethadba.locais_trab SET fone = '{}' WHERE i_entidades = {} AND i_locais_trab = {};".format(telefone, idEntidade, idLotacaoFisica)
        
        print(u)
        updateInsertDelete(u)
        
#Coloca a data de vigor na data de criação
#A data de criação é obrigatória
def dataCriacaoAtoNulo():

    updateInsertDelete(
        """
            UPDATE 
                bethadba.atos a
            SET 
                a.dt_inicial = a.dt_vigorar
            WHERE 
                a.dt_inicial IS NULL;                                  
        """
    ) 

#Renomeia as descrições repetidas dos niveis salariais
def descricaoNivelSalarialRepetido():

    resultado = select(
        """
            SELECT 
                list(i_entidades), 
                list(i_niveis), 
                TRIM(nome),
                count(nome) AS quantidade
            FROM 
                bethadba.niveis 
            GROUP BY 
                TRIM(nome)   
            HAVING
                quantidade > 1
        """
    )

    for i in resultado:
        idsEntidade = i[0].split(',')
        idsNiveis = i[1].split(',')
        descricao = i[2]
        
        for index in range(len(idsEntidade)):
            
            if index == 0:
                continue
            
            descricaoNovo = descricao + " |" + str(index)

            if len(descricao) > 46:
                descricaoNovo = descricao[:46] + " |" + str(index) 

            u = """
                UPDATE 
                    bethadba.niveis 
                SET 
                    nome = '{}' 
                WHERE 
                    i_entidades = {} AND i_niveis = {};
            """.format(descricaoNovo, idsEntidade[index], idsNiveis[index])
            
            print(u)
            updateInsertDelete(u)

#Recodifica os cartões pontos que estão diferentes de sua matricula ou repetidos
#Esta função só ira funcionar se os números das matriculas estiverem recodificados (que não se repetem)
def cartaoPontoRepetido():

    matriculas = select(
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

    if len(matriculas) > 0:
        return 0

    print("Cartão ponto sendo configurado, aguarde!")

    updateInsertDelete(
        """
            UPDATE 
                bethadba.hist_funcionarios
            SET 
                num_cp = i_funcionarios
            WHERE 
                bate_cartao = 'S';                                  
        """
    ) 

    updateInsertDelete(
        """
            UPDATE 
                bethadba.hist_funcionarios
            SET 
                num_cp = NULL
            WHERE 
                bate_cartao = 'N';                                  
        """
    ) 

#Coloca a data de nomeação na data de posse
#O funcionário x da entidade x deve ter a data de posse (0000-00-00) posterior à data de nomeação (0000-00-00)!
def dataNomeacaoMaiorDataPosse():

    updateInsertDelete(
        """
            UPDATE 
                bethadba.hist_cargos
            SET 
                dt_nomeacao = dt_posse
            WHERE 
                dt_nomeacao > dt_posse;                                  
        """
    ) 

#Colaca os dados da conta bancaria de acordo com o cadastro de conta bancaria da pessoa
#Quando a forma de pagamento for "Crédito em conta" é necessário informar a conta bancária
def contaBancariaFuncionarioInvalida():

    updateInsertDelete(
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
                        (pc.i_bancos != hf.i_bancos OR pc.i_agencias != hf.i_agencias) AND hf.forma_pagto = 'R'
                ) AS conta_bancaria
            WHERE 
                hff.i_entidades = conta_bancaria.i_entidades AND
                hff.i_funcionarios = conta_bancaria.i_funcionarios AND
                hff.dt_alteracoes = conta_bancaria.dt_alteracoes;
        """
    ) 

#Coloca previdencia federal para os historicos de funcionarios com mais do que uma previdencia informada
#Apenas uma previdência pode ser informada
def previdenciaMaiorQueUm():

    updateInsertDelete(
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
                        quantidade > 1
                ) AS historico_funcionario
            WHERE 
                hff.i_entidades = historico_funcionario.i_entidades AND
                hff.i_funcionarios = historico_funcionario.i_funcionarios AND
                hff.dt_alteracoes = historico_funcionario.dt_alteracoes;
        """
    ) 

#Ajusta os afastamentos com data inicial menor que data de admissão
#A data inicial não poderá ser menor que a data de admissão
def dataInicialAfastamentoMenorDataAdmissao():

    resultado = select(
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
                a.dt_afastamento < data_admissao;
        """
    )

    for i in resultado:
        dataInicial = i[0]  
        dataFinal = i[1]
        idEntidade = i[2]
        idFuncionario = i[3]
        dataAdmissao = i[4]

        if dataFinal < dataAdmissao:
            dataFinal = dataAdmissao

        u = "UPDATE bethadba.afastamentos SET dt_afastamento = '{}', dt_ultimo_dia = '{}' WHERE i_funcionarios = {} AND i_entidades = {} AND dt_afastamento = '{}';".format(dataAdmissao, dataFinal, idFuncionario, idEntidade, dataInicial)

        print(u)
        updateInsertDelete(u)

#Renomeia as areas de atuação com descrição repetido
#Já existe uma área de atuação com a descrição informada
def areasAtuacaoDescricaoRepetido():

    resultado = select(
        """
           SELECT 
                list(i_areas_atuacao), 
                TRIM(nome), 
                count(nome) 
            FROM 
                bethadba.areas_atuacao 
            GROUP BY 
                TRIM(nome) 
            HAVING 
                count(nome) > 1
        """
    )

    for i in resultado:
        ids = i[0].split(',')
        nome = i[1]

        for index, identificador in enumerate(ids):
            if index == 0:
                continue
            
            u = "UPDATE bethadba.areas_atuacao SET nome = '{}'  WHERE i_areas_atuacao = {};".format((nome + " |" + str(index)), identificador)

            print(u)
            updateInsertDelete(u)

#Coloca 0 - Outros para os dependentes sem motivo de termino
#O motivo de término é obrigatório
def dependenteMotivoTerminoNulo():

    updateInsertDelete(
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

#Coloca a configuração de feroas mais utilizada para os cargos sem configuração de ferias
#A configuração de férias é obrigatória
def cargoConfiguracaoFeriasNulo():

    updateInsertDelete(
        """
            UPDATE
                bethadba.cargos_compl
            SET 
                i_config_ferias = (SELECT TOP 1 i_config_ferias FROM bethadba.cargos_compl GROUP BY i_config_ferias ORDER BY count(*) DESC),
                i_config_ferias_subst = (SELECT TOP 1 i_config_ferias_subst FROM bethadba.cargos_compl GROUP BY i_config_ferias_subst ORDER BY count(*) DESC)
            WHERE
                i_config_ferias IS NULL OR 
                i_config_ferias_subst IS NULL;                               
        """
    )  

#Alterações realizadas manualmente
def alteracao():
    alteracao = open("vertical-pessoal-desktop-to-cloud\\src\\sql\\alteracao.sql", "r", encoding = 'utf-8')    
    updateInsertDelete(
        """
          {}                           
        """.format(alteracao.read())
    )
    alteracao.close()    
    print("Executado arquivo de alterações.")

#--------------------Executar--------------------#
campoAdicionalDescricaoRepetido()
pessoaDataVencimentoCNHMenorDataEmissao()
pessoaDataPrimeiraCNHMaiorNascimento()
dependentesOutros()
pessoaDataNascimentoNulo()
#cpfNulo()
cpfRepetido()
pisRepetido()
pisInvalido()
cnpjNulo()
logradourosDescricaoCaracterEspecial()
logradourosDescricaoRepetido()
tiposBasesRepetido()
logradourosSemCidade()
atosNumeroNulo()
atosRepetido()
cargoCboNulo()
eSocialNuloVinculoEmpregaticio()
vinculoEmpregaticioRepetido()
eSocialNuloMotivoRescisao()
fechamentoFolha(competenciaFechamentoFolha)
folhaFeriasDataPagamentoNulo()
eSocialNuloMotivoAposentadoria()
historicoSalarialZerado()
#dataFinalLancamentoMaiorDataRescisao()
movimentacaoPessoalRepetido()
tipoAfastamentoRepetido()
#alteracaoFuncionarioMaiorDataRescisao()
alteracaoSalarialMaiorDataRescisao()
alteracaoCargoMaiorDataRescisao()
classificacaoErradaTipoAfastamento()
tipoAtoRepetido()
descricaoHorarioPontoRepetido()
descricaoTurmaRepetido()
nivelOrganogramaSeparadorNulo()
atoNaturezaTextoJuridicoNulo()
atoFonteDivulgacaoMenorPublicacao()
tipoAfastamentoConfiguracaoCancelamentoFerias()
descricaoConfigOrganogramaMaior30()
descricaoConfigOrganogramaRepetido()
cpfInvalido()
cnpjInvalido()
RgRepetido()
cargoDescricaoRepetido()
terminoVigenciaMaior2099()
emailInvalido()
numeroEnderecoVazio()
nomeRuaVazio()
funcionariosSemPrevidencia()
eventoMediaVantagemSemComposicao()
eventoMediaVantagemComposicao()
dataAdmissaoMatriculaMaiorDataLotacaoFisica()
descricaoMotivoAlteracaoPontoMaior30()
observacaoAfastamentoMaior150()
dataInicialAfastamentoMaiorDataFinal()
motivoAposentadoriaNulo()
gruposFuncionaisRepetido()
dataInicialDependenteMaiorTitular()
telefoneLotacaoFisicaMaior11()
dataCriacaoAtoNulo()
descricaoNivelSalarialRepetido()
cartaoPontoRepetido()
dataNomeacaoMaiorDataPosse()
contaBancariaFuncionarioInvalida()
previdenciaMaiorQueUm()
#dataInicialAfastamentoMenorDataAdmissao()
areasAtuacaoDescricaoRepetido()
dependenteMotivoTerminoNulo()
cargoConfiguracaoFeriasNulo()
alteracao()