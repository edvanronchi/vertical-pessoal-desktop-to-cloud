from variaveis import *
from src.funcoes import *
from src.conexao import *


# Busca os aposentados que foram demitidos com motivo de aposentadoria e vinculo de aposentadoria
def mostrar_aposentados() -> dict:
    aposentados_vinculado = []

    resultado = consultar(
        """ 
            SELECT 
                hf.i_entidades, 
                hf.i_funcionarios,
                f.i_pessoas,
                r.dt_rescisao
            FROM 
                bethadba.hist_funcionarios hf
            INNER JOIN
                bethadba.funcionarios f ON (hf.i_funcionarios = f.i_funcionarios)	
            INNER JOIN 
                bethadba.rescisoes r ON (r.i_motivos_resc = 7 AND hf.i_vinculos = 11 AND r.i_funcionarios = hf.i_funcionarios)
            WHERE
                f.i_entidades IN ({})
            GROUP BY 
                hf.i_entidades, 
                hf.i_funcionarios,
                f.i_pessoas,
                dt_rescisao
            ORDER BY 
                f.i_pessoas
        """.format(lista_entidade)
    )

    for i in resultado:
        entidade = i[0]
        funcionario = i[1]
        pessoa = i[2]
        dt_rescisao = str(i[3]).replace("-", "")

        # Busca os vinculos dos aposentados
        vinculo = consultar(
            """
                SELECT 
                    hf.i_entidades,
                    hf.i_funcionarios,
                    r.dt_rescisao  
                FROM
                    bethadba.hist_funcionarios hf 
                INNER JOIN	
                    bethadba.rescisoes r ON (hf.i_funcionarios = r.i_funcionarios and hf.i_entidades = r.i_entidades)	
                WHERE
                    hf.i_pessoas = {} AND r.dt_rescisao <= {} AND hf.i_funcionarios != {}
                GROUP BY 
                    hf.i_entidades,
                    hf.i_funcionarios,
                    r.dt_rescisao
                ORDER BY 
                    r.dt_rescisao DESC,
                    hf.i_funcionarios
            """.format(pessoa, dt_rescisao, funcionario)
        )

        if len(vinculo) == 0:
            continue

        print("Matricula aposentado: {}".format(funcionario))
        print("Data aposentado: {}".format(i[3]))
        print("Matricula demitido: {}".format(vinculo[0][1]))
        print("Data demitido: {}".format(vinculo[0][2]))
        print("---------------------------------------")

        aposentados_vinculado.append({
            'aposentado': funcionario,
            'demitido': vinculo[0][1],
            'entidade': entidade
        })

    return aposentados_vinculado


# Faz o vinculo do aposentado com sua matricula anterior
def vincular_aposentados(vincular):
    resultado = consultar("SELECT * FROM bethadba.caracteristicas WHERE i_caracteristicas = 19999")

    if len(resultado) == 0:
        executar(
            "INSERT INTO bethadba.caracteristicas (i_caracteristicas, nome, tipo_dado) VALUES(19999, 'Vinculo Matricula Aposen.', 2);")

        maximo = consultar("SELECT MAX(ordem)+1 AS id from bethadba.funcionarios_caract_cfg")[0][0]

        executar(
            "INSERT INTO bethadba.funcionarios_caract_cfg (i_caracteristicas, ordem, permite_excluir, dt_expiracao) VALUES(19999, {}, 'S', '2999-12-31');".format(
                maximo))
        print("Criado o campo adicionao para migração!")
    if not vincular:
        return

    vinculo = mostrar_aposentados()
    for i in vinculo:

        funcionarios_prop_adic = consultar(
            """
                SELECT 
                    * 
                FROM 
                    bethadba.funcionarios_prop_adic 
                WHERE 
                    i_caracteristicas = 19999 AND 
                    i_funcionarios = {} AND 
                    i_entidades = {};
            """.format(i['aposentado'], i['entidade'])
        )

        if len(funcionarios_prop_adic) > 0:
            executar(
                """
                    UPDATE 
                        bethadba.funcionarios_prop_adic
                    SET
                        i_entidades = {0},
                        i_funcionarios = {1},
                        valor_numerico = {2}
                    WHERE
                        i_caracteristicas = 19999 AND
                        i_entidades = {0} AND
                        i_funcionarios = {1};
                """.format(i['entidade'], i['aposentado'], i['demitido'])
            )

            print("Registro atualizado: Aposentado -> {}, Demitido -> {}, Entidade -> {}".format(i['aposentado'],
                                                                                                 i['demitido'],
                                                                                                 i['entidade']))

        else:
            executar(
                """
                    INSERT INTO 
                        bethadba.funcionarios_prop_adic (i_caracteristicas, i_entidades, i_funcionarios, valor_numerico) 
                    VALUES
                        (19999, {}, {}, {});
                """.format(i['entidade'], i['aposentado'], i['demitido'])
            )

            print("Registro inserido: Aposentado -> {}, Demitido -> {}, Entidade -> {}".format(i['aposentado'],
                                                                                               i['demitido'],
                                                                                               i['entidade']))


# -----------------------Executar---------------------#
# mostrar_aposentados()
vincular_aposentados(False)
