# Instalação das bibliotecas a partir do terminal do VSCode
# pip install pyomo
# pip install pandas
# pip install numpy
# pip install wntr

# Bibliotecas 
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import numpy as np
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
        
#   Função que classifica as bombas e retorna a lista com o nome delas em cada tipo
def classifica_bomba(id_reservatorio, id_eta, tipo_bomba):
    nc = []
    ns = []
    ne = []
    nt = []    
    for pump, bomba in wn.pumps():
        if str(id_reservatorio) == bomba.start_node_name:
            nc.append(bomba.name)
        if str(id_eta) == bomba.start_node_name:    
            ne.append(bomba.name)
        if str(id_eta) != bomba.start_node_name and str(id_reservatorio) != bomba.start_node_name:
            nt.append(bomba.name)
            
    if (tipo_bomba ==  'CAPTACAO_SUPERFICIAL'):
        return nc
    if (tipo_bomba ==  'CAPTACAO_SUBTERRANEA'):
        return 0.0
    if (tipo_bomba ==  'ELEVACAO'):
        return ne
    if (tipo_bomba ==  'TRANSFERENCIA'):
        return nt         
   
#   Função que define a altura geométrica
def altura_geometrica (node1, node2):
    if tipo_elemento(str(node1)) == 'RESERVATORIO':
        for reservoir, reservatorio in wn.reservoirs():
            if reservatorio.name == str(node1):
                node1 = reservatorio
                cota1 = node1.base_head
    else:
        for tank, tanque in wn.tanks():
            if tanque.name == str(node1):
                cota1 = tanque.elevation
        
    if tipo_elemento(str(node2)) == 'RESERVATORIO':
        for reservoir, reservatorio in wn.reservoirs():
            if reservatorio.name == str(node2):
                node2 = reservatorio
                cota2 = node1.base_head
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

#   PC - Potência consumida pela(s) bomba(s) de captação de ponto(s) de superficia(is)
def potencia_captacao_superficial(id_reservatorio, id_eta):
    Pc = []
    g = 9.8
    for pump, bomba in wn.pumps():
        if str(id_reservatorio) == bomba.start_node_name:
            Hpe = altura_geometrica(id_reservatorio, id_eta)
            Fpe = fator_atrito_dw('CAPTACAO', 'NOVA')
            Lpe = comprimento_tubulacao(verifica_ligacao(id_reservatorio, bomba))
            Dpe = diametro_tubulacao(verifica_ligacao(id_reservatorio, bomba))
            Qpe = vazao_bomba(id_reservatorio)
            Vpe = velocidade(Dpe, Qpe)
            Npe = rendimento_bomba(bomba)
            Pc.append((Hpe + (Fpe * (Lpe / Dpe) * (pow(Vpe, 2) / 2 * g))) * Qpe * 0.735499 / 270 * Npe)
    return Pc

#   PN - Potência consumida pela(s) bomba(s) de captação de ponto(s) de subterrâneo(s)
def potencia_captacao_subterranea(id_reservatorio, id_eta):
    return 0.0

#   PE - Potência consumida pela(s) bomba(s) de captação de ponto(s) de elevação
def potencia_elevacao(id_eta):
    Pe = []
    g = 9.8
    for pump, bomba in wn.pumps():
        if str(id_eta) == bomba.start_node_name:
            Her = altura_geometrica(id_eta, verifica_ligacao(id_eta, bomba)[1])
            Fer = fator_atrito_dw('ELEVACAO', 'NOVA')
            Ler = comprimento_tubulacao(verifica_ligacao(id_eta, bomba))
            Der = diametro_tubulacao(verifica_ligacao(id_eta, bomba))
            Qer = vazao_bomba(id_eta)
            Ver = velocidade(Der, Qer)
            Ner = rendimento_bomba(bomba)
            Pe.append((Her + (Fer * (Ler / Der) * (pow(Ver, 2) / 2 * g))) * Qer * 0.735499 / 270 * Ner)
    return Pe

#   PT - Potência consumida pela(s) bomba(s) de captação de ponto(s) de transferência
def potencia_transferencia(id_eta):
    Pt = []
    g = 9.8
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
                Pt.append((Hrj + (Frj * (Lrj / Drj) * (pow(Vrj, 2) / 2 * g))) * Qrj * 0.735499 / 270 * Nrj)
    return Pt

#   Função que retorna o volume de água do reservatório r no periodo t
def pi():
    return 0.0

#   Função que retorna     
def volume_reservatorio(id_tanque):
    vazamento = 0.0
    volume_anterior = 0.0
    parte_subterraneo = 0.0
    for tank, tanque in wn.tanks():
        if str(tanque) == str(id_tanque):
            print('tratar aqui')
            


    
#   FUNÇÃO PRINCIPAL
# Variáveis
qt_reservatorio = 0
qt_eta = 0
g = 9.81
eta_altura = 0
qt_tanque = 0
T = int((wn.options.time.duration) / 3600)
Nh = (wn.options.time.pattern_timestep) / 3600

#   Informações sobre os reservatórios de nível fixo: 
for  reservoir, reservatorio in wn.reservoirs():
    qt_reservatorio += 1
    id_reservatorio = reservatorio   

for tank, tanque in wn.tanks():
    if(tanque.name == '6'):
        id_eta  = tanque
        qt_eta += 1
    else:
        qt_tanque += 1
        
#   FUNÇÃO PRINCIPAL
# Variáveis
qt_reservatorio = 0
qt_eta = 0
g = 9.81
eta_altura = 0
id_tanque = []
#   Informações sobre os reservatórios de nível fixo: 
for  reservoir, reservatorio in wn.reservoirs():
    qt_reservatorio += 1
    id_reservatorio = reservatorio   

for tank, tanque in wn.tanks():
    if(tanque.name == '6'):
        id_eta = tanque
    else:
        id_tanque.append(int(tanque.name))


# Resolvendo o modelo com CPLEX
model = pyo.ConcreteModel()

#   Variáveis de decisão
model.Xnc = pyo.Var(bounds=(0,1))
model.Ins = pyo.Var(bounds=(0,1))
model.Yne = pyo.Var(bounds=(0,1))
model.Znt = pyo.Var(bounds=(0,1))

Xnc = model.Xnc
Ins = model.Ins
Yne = model.Yne
Znt = model.Znt

#   Valores que posteriormente serão de entrada
u = 0.05
D = 100
a = 0.05
Sj = 2
Dmin = 10   # demanda mínima (em kW) a ser contratada;
i = 0

# Restrição 1: Restrições para cálculo da demanda contratada
#model.C1 = pyo.Constraint(expr= qt_reservatorio * qt_eta * T * qnt_bomba(id_reservatorio, id_eta, 'CAPTACAO_SUPERFICIAL') * (sum(Pc) * Xnc * Nh) 
#                                    + qt_eta * qt_tanque * T * qnt_bomba(id_reservatorio, id_eta, 'ELEVACAO') * (sum(Pe) * Yne * Nh) 
#                                        + qt_tanque * Sj * T * qnt_bomba(id_reservatorio, id_eta, 'TRANSFERENCIA') * (sum(Pt) * Znt * Nh) 
#                                        <= (1 + u) * D)

#model.C2 = pyo.Constraint(expr= D >= Dmin)

# Restrição 2: Cálculo do volume de água nos reservatórios
 
while i < len(id_tanque):
    volume_reservatorio(id_tanque[i])
    i+=1

#model.C3 = pyo.Constraint(expr= volume_reservatorio = (1 - vazamento) * volume_reservatorio + qt_eta * qt_reservatorio * qt_ne * (vazao_bomba() * Yne * Nh) + qt_subterraneo * qt_reservatorio * qt_ns * (vazao_bomba() * Ins * Nh) + qt_reservatorio * Uj * qt_nt * (vazao_bomba() * Znt * Nh) - qt_reservatorio * Sj * qt_nt * (vazao_bomba() * Znt * Nh) - Wrt)

# Restrição 3: Restrições para as zonas de pressão


# Função Objetivo
#model.obj = pyo.Objective(expr= qt_reservatorio * qt_eta * T * qt_nc * (Pc * Xnc * Nh) + qt_eta * qt_tanque * T * qt_ne * (Pe * Yne * Nh) + qt_tanque * Sj * T * qt_nt * (Pt * Znt * Nh), sense=pyo.minimize)

# Resultado da resolução:
#opt = SolverFactory('cplex')
#opt.solve(model)

#model.pprint()
# Escrevendo as regras no arquivo INP da rede


# Teste com a biblioteca do EPANET
# 4. Restrições para as zonas de pressão
Hrk = 0
Pdmin = 10
Pemax = 50
Ctmax = 0

#for tank, tanque in wn.tanks():
#    if(tanque.name != '6'):
#        print((tanque.diameter / 2))
#       print(np.pi * pow((tanque.diameter / 2), 2))
#for pattern, pat in wn.patterns():
#    print(pat.multipliers)
#demanda_no_9 = 0
#for t in range(T):
#    for pattern, demanda in wn.patterns():
#        if demanda.name == 'Demandano9':
#            demanda_no_9 += demanda.multipliers[t]

#print(demanda_no_9)


