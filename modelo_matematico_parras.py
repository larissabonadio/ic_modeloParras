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
        if id_elemento == int(bomba.name):
            return 'BOMBA'

    for i, no in wn.junctions():
        if id_elemento == int(no.name):
            return 'NO'

    for i, reservatorio in wn.reservoirs():
        if id_elemento == int(reservatorio.name):
            return 'RESERVATORIO'
            
    for i, tanque in wn.tanks():
        if id_elemento == int(tanque.name):
            return 'TANQUE'
            
    for i, trecho in wn.pipes():
        if id_elemento == int(trecho.name):
            return 'TRECHO'

    for i, valvula in wn.valves():
        if id_elemento == int(valvula.name):
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

#   Função que verifica a ligação entre os dois componentes e a qual trecho ele corresponde
def caminho(node1):
    global node2
    
    # Verificar se o node1 está conectado a uma bomba - Reservatório está sempre ligado a uma bomba
    for pump, bomba in wn.pumps():
        if bomba.start_node_name == str(node1):
            print(bomba.start_node_name)
            node2 = bomba.end_node_name
            print(node2)

    return (node1, node2)

#   Função que pega o ID do elemento e verifica com quem está conectado
def comprimento_tubulacao():
    return 0.0    

    
    
#   Função que retorna o valor em decimal do rendimento / eficiência da bomba   
def rendimento_bomba(id_bomba):
    return wn.options.energy.global_efficiency / 100 


# Leitura das variáveis de entrada
qt_reservatorio = 0
qt_eta = 0
g = 9.81
eta_altura = 0
Hpe = 0
Fpe = 0
Npe = 0
Lpe = 0

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
    

#   Verifica se o reservatório de nível fixo esta ligada a uma bomba - pega o node final 
#for pumps, bomba in wn.pumps():
#    if str(bomba.start_node_name) == str(id_reservatorio):
#       no_reserv_bomba = bomba.end_node_name
       
#   Para chegar em outro componente analiso o cano - tenho o nó inicial e procuro qual é ID do componente final
#for pipes, cano in wn.pipes():
#    if(str(cano.start_node_name) == str(no_reserv_bomba)):
#        print('A bomba está conectada com o cano: ', cano)
    
# Informações sobre a(s) bomba(s) ligada(s) ao reservatório fixo        
    

# 1. Restrições de Potência 

#   PC - Potência consumida pela(s) bomba(s) de captação de ponto(s) de superficia(is)

Hpe += altura_geometrica(reservatorio.base_head, id_eta.elevation)
Fpe += fator_atrito_dw('CAPTACAO', 'NOVA')
#Lpe = comprimento_tubulacao(1)
#Dpe += diametro_tubulacao()
#Vpe += velocidade_escoamento()
#Qpe += vazao_bomba()
Npe += rendimento_bomba(2)
node = caminho(1)
print(node[0], node[1])

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

