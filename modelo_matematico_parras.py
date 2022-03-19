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

# Create a water network model
inp_file = 'rede.inp'
wn = wntr.network.WaterNetworkModel('rede.inp')

#sim = wntr.sim.EpanetSimulator(wn)
#results = sim.run_sim()

#elementos = wntr.network.elements

# Leitura das variáveis de entrada

# Variáveis
qnt_reservatorio = 0
qnt_eta = 0

#tempo é dado em segundos
duracao = wn.options.time.duration
print('duracao em segundos: ',duracao)

# Restrições

# 1. Restrições de Potência 

#   PC - Potência consumida pela(s) bomba(s) de captação de ponto(s) de superficia(is)


#   PN - Potência consumida pela(s) bomba(s) de captação de ponto(s) de subterrâneo(s)


#   PE - Potência consumida pela(s) bomba(s) de captação de ponto(s) de elevação


#   PT - Potência consumida pela(s) bomba(s) de captação de ponto(s) de transferência



# 2. Restrições para cálculo da demanda contratada

#   somatório da quantidade de reservatórios de nível fixo 
for  reservoir in wn.reservoirs():
    qnt_reservatorio += 1
print("quantidade de reservatorios de nível fixo: ", qnt_reservatorio)
#   somatório da quantidade de estação(ões) de tratamento
#for tank, tanque in wn.tanks():
#    print(tanque.name)
qnt_eta = 1
tempo = duracao / 3600


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

#for reservoir_name, reservoir in wn.reservoirs():
#    id_reserv = reservoir.name
    
#for pipe_name, pipe in wn.pipe():
#    print(pipe.name)

#print(Hpe)
         
# pega o nome do elemento
#wn.get_link(id_reserv)








