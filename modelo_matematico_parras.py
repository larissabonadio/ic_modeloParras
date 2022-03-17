# Instalação das bibliotecas a partir do terminal do VSCode
# pip install pyomo
# pip install pandas
# pip install numpy
# pip install wntr

# Bibliotecas 
import pyomo.environ as pyo
import numpy as np
import time
from pyomo.environ import *
from pyomo.opt import SolverFactory
import pandas as pd
import wntr


# Leitura das variáveis de entrada

# Create a water network model
inp_file = 'vanzyl.inp'
wn = wntr.network.WaterNetworkModel(inp_file)
#sim = wntr.sim.EpanetSimulator(wn)
#results = sim.run_sim()

elementos = wntr.network.elements


# Restrições

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



# Teste com a biblioteca do EPANET

for reservoir_name, reservoir in wn.reservoirs():
    id_reserv = reservoir.name
    
for pipe_name, pipe in wn.pipe():
    print(pipe.name)

print(Hpe)
         
# pega o nome do elemento
wn.get_link(id_reserv)








