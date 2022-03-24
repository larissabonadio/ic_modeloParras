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

# Criando o modelo de rede
inp_file = 'rede.inp'
wn = wntr.network.WaterNetworkModel('rede.inp')

# Leitura das variáveis de entrada
tempo_total = wn.options.time.duration # Em segundos
qt_reservatorio = 0
qt_eta = 0
g = 9.81
eta_altura = 0

# Restrições

#   Informações sobre os reservatórios de nível fixo: 
for  reservoir, reservatorio in wn.reservoirs():
    qt_reservatorio += 1
    id_reservatorio = reservatorio
    
#   Informações sobre a(s) estação(ões) de tratamento:
for tank, tanque in wn.tanks():
    if tanque.name == '3':
        eta_altura = tanque.elevation 
        qt_eta += 1
        id_eta = tanque

#   Verifica se o reservatório de nível fixo esta ligada a uma bomba - verificar os Node1 e 2
for pumps, bomba in wn.pumps():
    if str(bomba.start_node_name) == str(id_reservatorio):
        print('o nó inicial dessa bomba está conectado com o RNF')
        no_inicial = bomba.start_node_name
    if str(bomba.end_node_name) == str(id_reservatorio):
        print('o nó final dessa bomba está conectado com o RNF')
        no_final = bomba.end_node_name
    
# Informações sobre a(s) bomba(s) ligada(s) ao reservatório fixo        
    

# 1. Restrições de Potência 

#   PC - Potência consumida pela(s) bomba(s) de captação de ponto(s) de superficia(is)


#   PN - Potência consumida pela(s) bomba(s) de captação de ponto(s) de subterrâneo(s)


#   PE - Potência consumida pela(s) bomba(s) de captação de ponto(s) de elevação


#   PT - Potência consumida pela(s) bomba(s) de captação de ponto(s) de transferência


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

