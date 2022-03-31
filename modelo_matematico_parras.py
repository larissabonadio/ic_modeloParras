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
def altura_geometrica (node1, node2):
    if tipo_elemento(str(node1)) == 'RESERVATORIO':
        cota1 = node1.base_head
    else:
        for tank, tanque in wn.tanks():
            if tanque.name == str(node1):
                cota1 = tanque.elevation
        
    if tipo_elemento(str(node2)) == 'RESERVATORIO':
        cota2 = node2.base_head
    else:
        for tank, tanque in wn.tanks():
            if tanque.name == str(node2):
                cota2 = tanque.elevation
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
def verifica_ligacao(node1, elemento):
    node1 = str(node1)
   
    if tipo_elemento(node1) == 'RESERVATORIO' or tipo_elemento(node1) == 'TANQUE':
        for pump, bomba in wn.pumps():
            if bomba.start_node_name == node1 and elemento == bomba:
                node1 = bomba.end_node_name
                node2 = verifica_ligacao(node1, elemento)
                
                return node1, node2
                
    if tipo_elemento(node1) == 'NO':
        for pipe, trecho in wn.pipes():
            if trecho.start_node_name == node1:
                if tipo_elemento(trecho.end_node_name) == 'TANQUE':                
                    return trecho.end_node_name

#   Função que retorna o comprimenro da tubulação especificada (em metros)
def comprimento_tubulacao(node):
    for pipe, trecho in wn.pipes():
        if trecho.start_node_name == str(node[0]) and trecho.end_node_name == str(node[1]):
            return trecho.length
        
#   Função que retorna o diametro da tubulação especificada (em metros)
def diametro_tubulacao(node):
    for pipe, trecho in wn.pipes():
        if trecho.start_node_name == str(node[0]) and trecho.end_node_name == str(node[1]):
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
Pe = 0.0
Pt = 0.0

#   Informações sobre os reservatórios de nível fixo: 
for  reservoir, reservatorio in wn.reservoirs():
    qt_reservatorio += 1
    id_reservatorio = reservatorio   

for tank, tanque in wn.tanks():
    if(tanque.name == '6'):
        id_eta = tanque

# 1. Restrições de Potência 

#   PC - Potência consumida pela(s) bomba(s) de captação de ponto(s) de superficia(is)
for pump, bomba in wn.pumps():
    if str(id_reservatorio) == bomba.start_node_name:
        Hpe = altura_geometrica(reservatorio, id_eta)
        Fpe = fator_atrito_dw('CAPTACAO', 'NOVA')
        Lpe = comprimento_tubulacao(verifica_ligacao(id_reservatorio, bomba))
        Dpe = diametro_tubulacao(verifica_ligacao(id_reservatorio, bomba))
        Qpe = vazao_bomba(id_reservatorio)
        Vpe = velocidade(Dpe, Qpe)
        Npe = rendimento_bomba(bomba)
        Pc += (Hpe + (Fpe * (Lpe / Dpe) * (pow(Vpe, 2) / 2 * g))) * Qpe * 0.735499 / 270 * Npe
        
#   PN - Potência consumida pela(s) bomba(s) de captação de ponto(s) de subterrâneo(s)


#   PE - Potência consumida pela(s) bomba(s) de captação de ponto(s) de elevação
for pump, bomba in wn.pumps():
    if str(id_eta) == bomba.start_node_name:
        Her = altura_geometrica(id_eta, verifica_ligacao(id_eta, bomba)[1])
        Fer = fator_atrito_dw('ELEVACAO', 'NOVA')
        Ler = comprimento_tubulacao(verifica_ligacao(id_eta, bomba))
        Der = diametro_tubulacao(verifica_ligacao(id_eta, bomba))
        Qer = vazao_bomba(id_eta)
        Ver = velocidade(Der, Qer)
        Ner = rendimento_bomba(bomba)
        Pe += (Her + (Fer * (Ler / Der) * (pow(Ver, 2) / 2 * g))) * Qer * 0.735499 / 270 * Ner
        
#   PT - Potência consumida pela(s) bomba(s) de captação de ponto(s) de transferência
for tank, tanque in wn.tanks():
    for pump, bomba in wn.pumps():
        if bomba.start_node_name == str(tanque) and tanque != id_eta:
            Hrj = altura_geometrica(tanque, verifica_ligacao(tanque, bomba)[1])
            Frj = fator_atrito_dw('TRANSFERENCIA', 'NOVA')
            Lrj = comprimento_tubulacao(verifica_ligacao(tanque, bomba))
            Drj = diametro_tubulacao(verifica_ligacao(tanque, bomba))
            Qrj = vazao_bomba(tanque)
            Vrj = velocidade(Drj, Qrj)
            Nrj = rendimento_bomba(bomba)            
            Pt += (Hrj + (Frj * (Lrj / Drj) * (pow(Vrj, 2) / 2 * g))) * Qrj * 0.735499 / 270 * Nrj

print('Potencia consumida pelas bombas de captação spf: ', Pc)        
print('Potencia consumida pelas bombas de elevação: ', Pe) 
print('Potencia consumida pelas bombas de transporte: ', Pt) 

# 2. Restrições para cálculo da demanda contratada


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
