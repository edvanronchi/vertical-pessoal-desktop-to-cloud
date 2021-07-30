from src.conexao import *
from variaveis import *

def ajustar_vinculo_empregaticio(conselheiro: str, vinculo: int, lista_entidade: str):

    resultado = consultar(
        """
            SELECT 
                f.i_funcionarios,
                f.i_entidades,
                hf.dt_alteracoes,
                hf.i_vinculos
            FROM 
                bethadba.funcionarios f
            INNER JOIN
                bethadba.hist_funcionarios hf ON (f.i_funcionarios = hf.i_funcionarios AND f.i_entidades = hf.i_entidades)
            WHERE
                f.tipo_func = 'A' and f.conselheiro_tutelar = '{}' and f.i_entidades IN ({}) and hf.i_vinculos != {}
            GROUP BY
                f.i_funcionarios,
                f.i_entidades,
                hf.i_vinculos,
                hf.dt_alteracoes
            ORDER BY 
                f.i_funcionarios;
        """.format(conselheiro, lista_entidade, vinculo)
    )

    if conselheiro == 'S':
        u = "UPDATE bethadba.vinculos SET tipo_vinculo = 3 WHERE i_vinculos = {};\n".format(vinculo)
        u += "UPDATE bethadba.vinculos SET categoria_esocial = 771 WHERE i_vinculos = {};".format(vinculo)

        print(u)
        executar(u)
    else:
        u = "UPDATE bethadba.vinculos SET categoria_esocial = 701 WHERE i_vinculos = {};".format(vinculo)

        print(u)
        executar(u)

    for i in resultado:
        u = "UPDATE bethadba.hist_funcionarios SET i_vinculos = {} WHERE i_funcionarios= {} AND i_entidades = {} AND dt_alteracoes = '{}';".format(vinculo, i[0], i[1], i[2])

        print(u)
        executar(u)

#-----------------------Executar---------------------#
#ajustar_vinculo_empregaticio('S', vinculo_empregaticio_autonomo_conselheiro, lista_entidade)
ajustar_vinculo_empregaticio('N', vinculo_empregaticio_autonomo, lista_entidade)