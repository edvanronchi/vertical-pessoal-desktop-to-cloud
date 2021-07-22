from iteration_utilities import duplicates, unique_everseen
from validate_docbr import CPF, CNPJ, PIS
from src.conexao import consultar
from random import randint
import re

def buscar_duplicatas(listNums: list) -> list:
	return list(unique_everseen(duplicates(listNums)))

def email_validar(email: str) -> bool:

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
 
    if re.match(regex, email) and "@." not in email:
        return True
 
    return False

#Tabelas que tem o nome da coluna especifica
def tabela_coluna(colunas: list = []) -> list:

    colunas = str(colunas).replace("[", "").replace("]", "").replace(" ", "")

    resultado = consultar(
        """
            SELECT
                LIST(cname) as lista,
                tname 
            FROM 
                sys.syscolumns
            WHERE 
                cname IN ({}) AND 
                creator = 'bethadba' AND 
                tname NOT LIKE '%audit_%' AND 
                tname NOT LIKE '%vw_%' AND
                tname NOT LIKE '%cloud_%' AND 
                tname NOT LIKE '%esocial%'
            GROUP BY
                tname
        """.format(colunas)
    )

    return [i[1] for i in resultado if len(i[0]) >= len(colunas.replace("'", ""))]

def cpf_gerar(ponto: bool = False) -> bool:                                                        
    return CPF().generate(ponto)

def pis_gerar(ponto: bool = False) -> bool:
    return PIS().generate(ponto)

def cnpj_gerar(ponto: bool = False) -> bool:                                                     
    return CNPJ().generate(ponto)

def rg_gerar(ponto: bool = False) -> bool:                                                       
    rg = [randint(0, 9) for x in range(7)]                              
                                                                                
    for _ in range(2):                                                          
        numero = sum([(len(rg) + 1 - i) * v for i, v in enumerate(rg)]) % 9      
                                                                                
        rg.append(9 - numero if numero > 1 else 0)                                  

    if ponto:
        return '%s%s.%s%s%s.%s%s%s-%s' % tuple(rg)
    
    return '%s%s%s%s%s%s%s%s%s' % tuple(rg)

def cpf_validar(cpf) -> bool:

    if not cpf:
        return False

    numero = [int(digit) for digit in cpf if digit.isdigit()]

    if len(numero) != 11 or len(set(numero)) == 1:
        return False

    valida = CPF()
    
    return valida.validate(cpf)

def pis_validar(pis) -> bool:

    if not pis:
        return False

    valida = PIS()
    
    return valida.validate(pis)

def cnpj_validar(cnpj) -> bool:

    if not cnpj:
        return False

    numero = [int(digit) for digit in cnpj if digit.isdigit()]

    if len(numero) != 14 or len(set(numero)) == 1:
        return False

    valida = CNPJ()
    
    return valida.validate(cnpj)

def remove_repetidos(li: list) -> list:
    return sorted(dict(zip(li, li)).keys())