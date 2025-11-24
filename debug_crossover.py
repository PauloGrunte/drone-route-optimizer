import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from drone_optimizer.genetic_algorithm import Individual, GeneticAlgorithm
from drone_optimizer.drone_model import Drone
from drone_optimizer.weather_model import WeatherForecast

def test_crossover():
    """Testa o crossover com dados reais"""
    ceps = [
        {'cep': '82821020', 'latitude': -25.548, 'longitude': -49.238},
        {'cep': '80010010', 'latitude': -25.428, 'longitude': -49.267},
        {'cep': '80020020', 'latitude': -25.435, 'longitude': -49.275},
        {'cep': '80030030', 'latitude': -25.442, 'longitude': -49.283},
        {'cep': '80040040', 'latitude': -25.449, 'longitude': -49.291}
    ]
    
    drone = Drone()
    weather = WeatherForecast()
    
    # Criar dois indivíduos
    parent1 = Individual(ceps, drone, weather)
    parent2 = Individual(ceps, drone, weather)
    
    print("=== TESTE DE CROSSOVER ===")
    print(f"Parent 1 rota: {[p['cep'] for p in parent1.route]}")
    print(f"Parent 2 rota: {[p['cep'] for p in parent2.route]}")
    
    # Testar crossover
    ga = GeneticAlgorithm({'population_size': 10}, ceps, drone, weather)
    
    try:
        child1, child2 = ga.crossover(parent1, parent2)
        print("✅ Crossover bem-sucedido!")
        print(f"Child 1 rota: {[p['cep'] for p in child1.route]}")
        print(f"Child 2 rota: {[p['cep'] for p in child2.route]}")
        
        # Verificar integridade
        assert len(child1.route) == len(parent1.route), "Tamanho da rota incorreto"
        assert child1.route[0]['cep'] == '82821020', "Não começa no Unibrasil"
        assert child1.route[-1]['cep'] == '82821020', "Não termina no Unibrasil"
        assert None not in child1.route, "Há None na rota"
        
        print("Todas as verificações passaram!")
        
    except Exception as e:
        print(f"Erro no crossover: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_crossover()