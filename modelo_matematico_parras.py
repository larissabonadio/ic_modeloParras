# Instalação das bibliotecas a partir do terminal do VSCode
# pip install pyomo
# pip install pandas
# pip install numpy
# pip install wntr
# pip install mip

# Bibliotecas 
import pyomo.environ as pyo
from   pyomo.opt import SolverFactory
import numpy as np
import pandas as pd
import wntr
# from mip import Model, xsum, minimize, BINARY

#   Criando o modelo de rede
wn = wntr.network.WaterNetworkModel('rede.inp')

#   Variáveis Globais
g  = 9.8                                                            #
T  = int((wn.options.time.duration) / 3600)                         #   Duração total do período de simulação
Nh = (wn.options.time.pattern_timestep) / 3600                      #   Número de horas em cada período (normalmente 1h)
no_consumidor = [];                                                 #   Lista dos nós que possuem demanda (demanda associada ao reservatório)
Ck = []                                                             #   Custo do kW no período t
reservatorios = []                                                  #   Lista dos tanques que são considerados reservatórios (tira o tanque que é ETA)
rendimento_bomba = float(wn.options.energy.global_efficiency / 100) #   Rendimento das bombas do sistema (todas as bombas do sistemas terão o mesmo rendimento)
D  = 720                                                            #   Demanda energética (kW) contratada por dia
S  = 2
td = 5.12                                                           #   Taxa (em R$/kW) para contratação de demanda energética - COnsiderado pela Isabela

#   Lista com o ID do tipo de Bomba -- Também informa a quantidade de cada tipo de bomba
nc = []
ns = []
ne = []
nt = []

#   Lista com a potencia consumida de cada bomba - Também informa a potência consumida do conjunto de bombas
Pc = []
Pn = []
Pe = []
Pt = []

#   Lista que contém o ID dos tanques que são considerados ETAs
lista_eta = ['6']

#   Lista dos reservátorios - tirando o ETA
for tank, tanque in wn.tanks():
    if tanque.name != lista_eta[0]:
        reservatorios.append(tanque.name)
         
#   Somatória de itens
P  = len(wn.reservoir_name_list)    # Pontos de captação superficiais
E  = len(lista_eta)                 # Estações de tratamento de água 
R  = len(reservatorios)             # Reservatórios


#   Função que classifica as bombas e retorna a lista com o nome delas em cada tipo
def classifica_bomba():    
    for pump, bomba in wn.pumps(): 
        
        # Se a bomba está ligada a algum reservatório, então a bomba é de captação superficial
        if (bomba.start_node_name in wn.reservoir_name_list) or (bomba.end_node_name in wn.reservoir_name_list):
            nc.append(bomba.name)
        
        # Se a bomba está ligada ao ETA, então a bomba é de elevação
        elif (bomba.start_node_name in lista_eta) or (bomba.end_node_name in lista_eta):
            ne.append(bomba.name)
        
        # Se a bomba está ligada a um tanque e esse tanque não está na lista do ETA, então é de transferência 
        elif (bomba.start_node_name in wn.tank_name_list) or (bomba.end_node_name in wn.tank_name_list):
            if bomba.start_node_name in lista_eta:    
                nt.append(bomba.name)
            elif bomba.end_node_name not in lista_eta:
                nt.append(bomba.name)
        
        # Caso contrário a bomba é de captação subterrânea
        else:
            ns.append(bomba.name)

#   Função que retorna a altura geométrica
def altura_geometrica (node1, node2):
    
    if node1 in wn.reservoir_name_list: 
        node1 = wn.get_node(node1)
        cota1 = node1.base_head              
    
    if node1 in wn.tank_name_list:
        node1 = wn.get_node(node1)
        cota1 = node1.elevation
            
    if node2 in wn.reservoir_name_list:
        node2 = wn.get_node(node2)
        cota2 = node2.base_head
    
    if node2 in wn.tank_name_list:
        node2 = wn.get_node(node2)
        cota2 = node2.elevation 
        
    return abs(cota1 - cota2)

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
        
#   Função que retorna o comprimento da tubulação especificada (em metros)
def comprimento_tubulacao(node):
    for pipe, trecho in wn.pipes():
        if trecho.start_node_name == node:
            return trecho.length
        
#   Função que retorna o diametro da tubulação especificada (em metros)
def diametro_tubulacao(node):
    for pipe, trecho in wn.pipes():
        if trecho.start_node_name == node:
            return trecho.diameter
        
#   Função que retorna a velocidade de escoamento
def velocidade(diamentro, vazao):
    a = np.pi * pow(diamentro, 2) / 4
    return (vazao / 3600) / a

#   Função que retorna a vazão da bomba
def vazao_bomba(id_bomba):
    bomba = wn.get_link(id_bomba)
    if bomba.pump_curve_name in wn.curve_name_list:
        curva = wn.get_curve(bomba.pump_curve_name)
    return 3600 * float(curva.points[0][0])

#   PC - Potência consumida pela(s) bomba(s) de captação de ponto(s) de superficia(is)
def potencia_consumida(tipo_bomba):
    
    #   Para cada bomba é calculado sua potência    
    for pump, bomba in wn.pumps():

        #   Se a bomba for de captação de pontos superficiais
        if bomba.name in nc:
            Hpe = altura_geometrica(bomba.start_node_name, lista_eta[0])
            Fpe = fator_atrito_dw('CAPTACAO', 'NOVA')
            Lpe = comprimento_tubulacao(bomba.end_node_name)
            Dpe = diametro_tubulacao(bomba.end_node_name)
            Qpe = vazao_bomba(bomba.name)
            Vpe = velocidade(Dpe, Qpe)
            Npe = rendimento_bomba
            Pc.append((Hpe + (Fpe * (Lpe / Dpe) * (pow(Vpe, 2) / 2 * g))) * Qpe * 0.735499 / 270 * Npe)

        #   Se a bomba for de captação de pontos subterrânea


        #   Se a bomba for de elevação            
        if bomba.name in ne:
            Her = altura_geometrica(bomba.start_node_name, lista_eta[0])
            Fer = fator_atrito_dw('ELEVACAO', 'NOVA')
            Ler = comprimento_tubulacao(bomba.end_node_name)
            Der = diametro_tubulacao(bomba.end_node_name)
            Qer = vazao_bomba(bomba.name)
            Ver = velocidade(Der, Qer)
            Ner = rendimento_bomba
            Pe.append((Her + (Fer * (Ler / Der) * (pow(Ver, 2) / 2 * g))) * Qer * 0.735499 / 270 * Ner)

        #   Se a bomba for de transferência
        if bomba.name in nt:
            Hrj = altura_geometrica(bomba.start_node_name, lista_eta[0])
            Frj = fator_atrito_dw('TRANSFERENCIA', 'NOVA')
            Lrj = comprimento_tubulacao(bomba.end_node_name)
            Drj = diametro_tubulacao(bomba.end_node_name)
            Qrj = vazao_bomba(bomba.name)
            Vrj = velocidade(Drj, Qrj)
            Nrj = rendimento_bomba            
            Pt.append((Hrj + (Frj * (Lrj / Drj) * (pow(Vrj, 2) / 2 * g))) * Qrj * 0.735499 / 270 * Nrj)            
  
    #   Retorna a potencia consumida dos tipos de bombas especificado 
    if tipo_bomba == 'SUPERFICIAL':
        return Pc
    if tipo_bomba == 'SUBTERRANEA':
        return Pn
    if tipo_bomba == 'ELEVACAO':
        return Pe
    if tipo_bomba == 'TRANSFERENCIA':
        return Pt

#   Função que retorna o custo (em reais) do kW no período t
def custo_kW(t):
    return float(wn.get_pattern('PrecokWh')[t])

    
#   Testes        
#classifica_bomba()
#potencia_consumida()

#print('Potencia consumida superficial', Pc)
#print('Potencia consumida elevação', Pe)
#print('Potencia consumida transferencia', Pt)
  
#   FUNÇÃO PRINCIPAL

#   Resolvendo o modelo com CPLEX - Modelo vai obter uma resposta a cada t (período)
#   De 0 até a duração total da simulação, a partir dos intervalos de (timestep) escolhido
for t in range(0, T, int(Nh)):
    #   Função que classifica as bombas (capt. superficial, capt. subterrânea, elevação e transferência)
    classifica_bomba()

    #   Inicializando modelo 
    modelo = pyo.ConcreteModel()

    # Inicializando indice do vetor das bombas
    modelo.Nc = pyo.Set(initialize=(nc))
    modelo.Ns = pyo.Set(initialize=(ns))
    modelo.Ne = pyo.Set(initialize=(ne))
    modelo.Nt = pyo.Set(initialize=(nt))
            
    #   Nomeando as variáveis de decisão não-binárias
    modelo.Xnc = pyo.Var(range(0,1), domain=pyo.NonNegativeReals)
    modelo.Ins = pyo.Var(domain=pyo.NonNegativeReals)
    modelo.Yne = pyo.Var(domain=pyo.NonNegativeReals)
    modelo.Znt = pyo.Var(domain=pyo.NonNegativeReals)

    Xnc = modelo.Xnc
    Ins = modelo.Ins
    Yne = modelo.Yne
    Znt = modelo.Znt

    #   Nomeando as variáveis de decisão binárias
    #   Função objetivo


    modelo.objetivo = pyo.Objective(expr= P * E * len(nc) * T * (sum(potencia_consumida('SUPERFICIAL')   * Xnc * Nh * custo_kW(t)))
                                        + # * R * len(ns) * T * (sum(potencia_consumida('SUBTERRANEA')   * Ins * Nh * custo_kW(t)))
                                        + E * R * len(ne) * T * (sum(potencia_consumida('ELEVACAO')      * Yne * Nh * custo_kW(t)))
                                        + R * S * len(nt) * T * (sum(potencia_consumida('TRANSFERENCIA') * Znt * Nh * custo_kW(t)))                                      
                                        + D * td, sense=pyo.minimize)

    