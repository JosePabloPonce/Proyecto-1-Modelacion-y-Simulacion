import random
import math
from scipy.stats import poisson
import numpy as np
import simpy


#Variables Iniciales
TOTAL_CLIENTES_HORA = 100 #LAMBDA
CLIENTES = 0 
tiempoEspera = 0 
tiempoFinal = 0 
CANTIDAD_CAJEROS = 5


class Cajero:

  CLIENTE_X_HORA = 20 #LAMBDA1

  def __init__(self, env):
    #Configuracion de Simpy, se crean los recursos para los cajeros
    self.env = env
    self.lista_cajeros = [simpy.Resource(self.env, capacity=1) for j in range(CANTIDAD_CAJEROS)] 
    self.capacidad_cajeros = [0 for k in range(CANTIDAD_CAJEROS)] 
  
  def despacho_cliente(self, cliente):
    beta = 1 / self.CLIENTE_X_HORA  #Beta = 1/Lambda
    tiempo_despacho = np.random.exponential(beta)
    yield self.env.timeout(tiempo_despacho)  
    print('No. Simulacion: ' + str(self.env.now)[:4] + ' - Cliente ' + str(cliente) + ' despachado en ' + str(tiempo_despacho*60)[:4] +' min')

def client(env, client_id, Cajero):
  global CLIENTES
  global tiempoEspera
  global tiempoFinal

  tiempo_inicio = env.now
  print('No. Simulacion: ' + str(env.now)[:4] + ' - El cliente ' + str(client_id) + ' esta en la espera de un cajero')


  opcion_cajero = []

  #Se comparan los cajeros y se verifica que opcion de cajero es la mejor
  for i in range(CANTIDAD_CAJEROS):
    if Cajero.capacidad_cajeros[i] == min(Cajero.capacidad_cajeros):
      opcion_cajero.append(i)

  ##########################################
  cajero_actual = random.choice(opcion_cajero)

  #Liberamos el recurso para poder solicitarlo nuevamente
  with Cajero.lista_cajeros[cajero_actual].request() as req:
    Cajero.capacidad_cajeros[cajero_actual] += 1
  

    yield req
    tiempo_finalizacion = env.now
    print('No. Simulacion: ' + str(env.now)[:4] + ' - Cliente ' + str(client_id) + ' esta siendo atendido por el cajero ' + str(cajero_actual))

    Cajero.capacidad_cajeros[cajero_actual] -= 1

    
    yield env.process(Cajero.despacho_cliente(client_id))
    print('No. Simulacion: ' + str(env.now)[:4] + ' - Cliente ' + str(client_id) + ' fue atendido por el cajero ' + str(cajero_actual))
    tiempoFinal = env.now
    CLIENTES += 1
    tiempoEspera += tiempo_finalizacion - tiempo_inicio

def poissonMedTime(x, lambda_val):
  return -(math.log(1 - x) / lambda_val)


# function that set uo the enviorment with the time intervals
def setup(env, Cajero):
  client_id = 0

  while True:
    CLIENTES_interval = poissonMedTime(random.random(), TOTAL_CLIENTES_HORA)
    yield env.timeout(CLIENTES_interval)
    env.process(client(env, client_id, Cajero))
    client_id += 1

#Clean globals
CLIENTES = 0
tiempoEspera = 0
caja_request = 0


env = simpy.Environment()

Cajero = Cajero(env)

env.process(setup(env, Cajero))
env.run(until=1)


print("Total de clientes: ", CLIENTES)
print("Tiempo promedio de un cliente en la cola: ", tiempoEspera / CLIENTES)
print("Numero de clientes en la cola por hora: ", (1 / (tiempoEspera / CLIENTES)) if tiempoEspera > 0 else 0)
print("Grado de utilizacion de cada cajero: ", CLIENTES/CANTIDAD_CAJEROS)


