# Instalação das bibliotecas a partir do terminal do VSCode
# pip install pyomo
# pip install pandas
# pip install numpy
# pip install wntr

# Bibliotecas 
import pyomo.environ as pyo
import numpy as np
from pyomo.environ import *
from pyomo.opt import SolverFactory
import pandas as pd
import wntr

#   Criando o modelo de rede
wn = wntr.network.WaterNetworkModel('rede.inp')

#   Variáveis Globais
node1 = 0
node2 = 0

# Função para identificar o tipo de elemento a partir do seu ID
def tipo_elemento (id_elemento):
    for i, bomba in wn.pumps():
        if id_elemento == str(bomba.name):
            return 'BOMBA'

    for i, no in wn.junctions():
        if id_elemento == str(no.name):
            return 'NO'

    for i, reservatorio in wn.reservoirs():
        if id_elemento == str(reservatorio.name):
            return 'RESERVATORIO'
            
    for i, tanque in wn.tanks():
        if id_elemento == str(tanque.name):
            return 'TANQUE'
            
    for i, trecho in wn.pipes():
        if id_elemento == str(trecho.name):
            return 'TRECHO'

    for i, valvula in wn.valves():
        if id_elemento == str(valvula.name):
            return 'VALVULA'
        
#   Função que define a altura geométrica
def altura_geometrica (cota1, cota2):
    return cota1 - cota2

#   Função que define o valor do fator de atrito de Darcy–Weisbach
def fator_atrito_dw(tipo_bomba, tipo_tubulacao):
    if tipo_bomba == 'CAPTACAO':
        if tipo_tubulacao == 'NOVA':
            return 0.020
        else:
            return 0.054
    if tipo_bomba == 'ELEVACAO':
        if tipo_tubulacao == 'NOVA':
            return 0.019
        else:
            return 0.048
    if tipo_bomba == 'TRANSFERENCIA':
        if tipo_tubulacao == 'NOVA':
            return 0.025
        else:
            return 0.072
    if tipo_bomba == 'ABASTECIMENTO':
        if tipo_tubulacao == 'NOVA':
            return 0.019
        else:
            return 0.046  
        
#   Função que a partir de um elemento percorre a rede (em sequência) para encontrar um trecho (para assim pegar as informações de comprimento, diamentro e rugosidade)
def verifica_ligacao(node1): 
    node1 = str(node1)
    if tipo_elemento(node1) == 'TRECHO':
        return node1
    # Se for esses tipos de elementos eles só serão o nó de inicio / final
    if tipo_elemento(node1) == 'RESERVATORIO' or tipo_elemento(node1) == 'TANQUE' or tipo_elemento(node1) == 'NO':
        for pump, bomba in wn.pumps():
            if bomba.start_node_name == str(node1):
                node1 = bomba.end_node_name
                verifica_ligacao(node1)
        for pipe, trecho in wn.pipes():
            if trecho.start_node_name == str(node1):
                node1 = trecho
                return node1 

#   Função que retorna o comprimenro da tubulação especificada (em metros)
def comprimento_tubulacao(id_trecho):
    for pipe, trecho in wn.pipes():
        if (str(trecho) == str(id_trecho)):
            return trecho.length    
        
#   Função que retorna o diametro da tubulação especificada (em metros)
def diametro_tubulacao(id_trecho):
    for pipe, trecho in wn.pipes():
        if (str(trecho) == str(id_trecho)):
            return trecho.diameter

#   Função que identifica a curva a partir do nome e retorna a vazão
def identifica_curva(nome_curva):
    for curve, curva in wn.curves():
        if nome_curva == curva.name:
            return float(curva.points[0][0])
    
#   Função que retorna a vazão de uma bomba
def vazao_bomba(node1):
    for pump, bomba in wn.pumps():
        if bomba.start_node_name == str(node1):
            # A partir do ID da bomba acha o nome da curva usada na bomba
            return 3600 * identifica_curva(bomba.pump_curve_name) 
        
#   Função que retorna a velocidade de escoamento
def velocidade(diamentro, vazao):
    a = np.pi * pow(diamentro, 2) / 4
    return (vazao / 3600) / a
   
#   Função que retorna o valor em decimal do rendimento / eficiência da bomba   
def rendimento_bomba(id_bomba):
    return wn.options.energy.global_efficiency / 100 



#   FUNÇÃO PRINCIPAL
# Variáveis
qt_reservatorio = 0
qt_eta = 0
g = 9.81
eta_altura = 0
Pc = 0.0

#   Informações sobre os reservatórios de nível fixo: 
for  reservoir, reservatorio in wn.reservoirs():
    qt_reservatorio += 1
    id_reservatorio = reservatorio
        
#   Informações sobre a(s) estação(ões) de tratamento:
for tank, tanque in wn.tanks():
#    Coloquei 3 pq sei que representa a ETA
    if tanque.name == '6':        
        qt_eta += 1
        id_eta = tanque    

# 1. Restrições de Potência 

#   PC - Potência consumida pela(s) bomba(s) de captação de ponto(s) de superficia(is)
#   Verifica dada bomba, se ela estiver ligada a ao reservatório então calcula a PC
for pump, bomba in wn.pumps():
    if str(id_reservatorio) == bomba.start_node_name:
        Hpe = altura_geometrica(reservatorio.base_head, id_eta.elevation)
        Fpe = fator_atrito_dw('CAPTACAO', 'NOVA')
        Lpe = comprimento_tubulacao(verifica_ligacao(id_reservatorio))
        Dpe = diametro_tubulacao(verifica_ligacao(id_reservatorio))
        Qpe = vazao_bomba(id_reservatorio)
        Vpe = velocidade(Dpe, Qpe)
        Npe = rendimento_bomba(2)
        Pc += (Hpe + (Fpe * (Lpe / Dpe) * (pow(Vpe, 2) / 2 * g))) * Qpe * 0.735499 / 270 * Npe
print('Potencia consumida pelas bombas de captação superficial: ', Pc)        
        
#   PN - Potência consumida pela(s) bomba(s) de captação de ponto(s) de subterrâneo(s)


#   PE - Potência consumida pela(s) bomba(s) de captação de ponto(s) de elevação


#   PT - Potência consumida pela(s) bomba(s) de captação de ponto(s) de transferência



# 2. Restrições para cálculo da demanda contratada


#   total de horas simuladas
#tempo = duracao / 3600

#   somatório da quantidade de bombas de captação de ponto superficial que estão conectados ao ETA 
# verificar a quantidade de bomba que tenho entre os reservatórios físicos e o eta
# posso verificar a partir da coluno Node1 e Node2 se eles estão inteligados pela bomba;

# 3. Cálculo do volume de água nos reservatórios


# 4. Restrições para as zonas de pressão


# 5. Restrições para o volume de água nos reservatórios


# 6. Restrição para a vazão de água captada

  
# 7. Restrições para os acionamentos das bombas

 

# Função Objetivo

# 1. Somatório de pontos de captacação superfícial


# 2. Somatório de estações de tratamento (ETA)

# 3. Somatório de bombas de captação (nc) 

# 4. Somatório do periodo de simulação

# Resolvendo o modelo com CPLEX


# Resultado da resolução:


# Escrevendo as regras no arquivo INP da rede


# Teste com a biblioteca do EPANET

