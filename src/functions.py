from validate_docbr import CPF, CNPJ, PIS
from src.database import *
import random

#Tabelas que tem o nome da coluna especifica
def tabelaColuna(colunas: list = []) -> list:
    colunas = str(colunas).replace("[", "").replace("]", "").replace(" ", "")

    resultado = select(
        """
            SELECT
                list(cname) as lista,
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

def gerarCpf(ponto: bool = False) -> bool:                                                        
    return CPF().generate(ponto)

def gerarPis(ponto: bool = False) -> bool:
    return PIS().generate(ponto)

def gerarCnpj(ponto: bool = False) -> bool:                                                     
    return CNPJ().generate(ponto)

def gerarRg(ponto: bool = False) -> bool:                                                       
    rg = [random.randint(0, 9) for x in range(7)]                              
                                                                                
    for _ in range(2):                                                          
        val = sum([(len(rg) + 1 - i) * v for i, v in enumerate(rg)]) % 9      
                                                                                
        rg.append(9 - val if val > 1 else 0)                                  

    if ponto:
        return '%s%s.%s%s%s.%s%s%s-%s' % tuple(rg)
    
    return '%s%s%s%s%s%s%s%s%s' % tuple(rg)

def validarCpf(cpf) -> bool:

    if not cpf:
        return False

    numbers = [int(digit) for digit in cpf if digit.isdigit()]

    if len(numbers) != 11 or len(set(numbers)) == 1:
        return False

    validador = CPF()
    
    return validador.validate(cpf)

def validarCnpj(cnpj) -> bool:

    if not cnpj:
        return False

    numbers = [int(digit) for digit in cnpj if digit.isdigit()]

    if len(numbers) != 14 or len(set(numbers)) == 1:
        return False

    validate_cnpj = CNPJ()
    
    return validate_cnpj.validate(cnpj)