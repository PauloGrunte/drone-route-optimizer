import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from drone_optimizer.genetic_algorithm import Individual, GeneticAlgorithm
from drone_optimizer.drone_model import Drone
from drone_optimizer.weather_model import WeatherForecast

@pytest.fixture
def sample_ceps():
    return [
        {'cep': '82821020', 'latitude': -25.548, 'longitude': -49.238},
        {'cep': '80010010', 'latitude': -25.428, 'longitude': -49.267},
        {'cep': '80020020', 'latitude': -25.435, 'longitude': -49.275}
    ]

@pytest.fixture
def sample_drone():
    return Drone()

@pytest.fixture
def sample_weather():
    return WeatherForecast()

def test_individual_initialization(sample_ceps, sample_drone, sample_weather):
    individual = Individual(sample_ceps, sample_drone, sample_weather)
    
    # Verificar se a rota é uma lista de dicionários
    assert len(individual.route) == len(sample_ceps) + 1  # +1 para retorno ao Unibrasil
    assert len(individual.speeds) == len(individual.route) - 1
    assert len(individual.recharges) == len(individual.route) - 1
    
    # Verificar que o primeiro e último são Unibrasil (como dicionários)
    assert isinstance(individual.route[0], dict), f"Expected dict, got {type(individual.route[0])}"
    assert individual.route[0]['cep'] == '82821020'  # Começa no Unibrasil
    assert individual.route[-1]['cep'] == '82821020'  # Termina no Unibrasil
    
    # Verificar que todos os elementos da rota são dicionários
    for point in individual.route:
        assert isinstance(point, dict), f"Expected dict in route, got {type(point)}"

def test_individual_evaluation(sample_ceps, sample_drone, sample_weather):
    individual = Individual(sample_ceps, sample_drone, sample_weather)
    
    assert hasattr(individual, 'fitness')
    assert hasattr(individual, 'total_cost')
    assert hasattr(individual, 'total_flight_time')
    assert hasattr(individual, 'is_valid')
    
    # Verificar que a avaliação foi executada
    assert individual.fitness > 0 or not individual.is_valid

def test_genetic_algorithm_initialization(sample_ceps, sample_drone, sample_weather):
    config = {
        'population_size': 10,
        'generations': 5,
        'mutation_rate': 0.1,
        'crossover_rate': 0.8,
        'elitism_count': 2,
        'tournament_size': 3
    }
    
    ga = GeneticAlgorithm(config, sample_ceps, sample_drone, sample_weather)
    
    assert len(ga.population) == config['population_size']
    assert ga.best_individual is not None
    
    # Verificar que todos os indivíduos têm rotas válidas
    for individual in ga.population:
        assert len(individual.route) > 0
        assert isinstance(individual.route[0], dict)

def test_selection(sample_ceps, sample_drone, sample_weather):
    config = {
        'population_size': 10,
        'generations': 5,
        'mutation_rate': 0.1,
        'crossover_rate': 0.8,
        'elitism_count': 2,
        'tournament_size': 3
    }
    
    ga = GeneticAlgorithm(config, sample_ceps, sample_drone, sample_weather)
    selected = ga.selection()
    
    assert selected in ga.population
    assert isinstance(selected.route[0], dict)

def test_crossover_creates_valid_offspring(sample_ceps, sample_drone, sample_weather):
    """Testa se o crossover cria filhos com rotas válidas"""
    config = {
        'population_size': 10,
        'generations': 5,
        'mutation_rate': 0.1,
        'crossover_rate': 0.8,
        'elitism_count': 2,
        'tournament_size': 3
    }
    
    ga = GeneticAlgorithm(config, sample_ceps, sample_drone, sample_weather)
    
    # Selecionar dois pais
    parent1 = ga.population[0]
    parent2 = ga.population[1]
    
    # Aplicar crossover
    child1, child2 = ga.crossover(parent1, parent2)
    
    # Verificar que os filhos têm estrutura válida
    for child in [child1, child2]:
        assert len(child.route) == len(parent1.route)
        assert isinstance(child.route[0], dict)
        assert child.route[0]['cep'] == '82821020'  # Começa no Unibrasil
        assert child.route[-1]['cep'] == '82821020'  # Termina no Unibrasil
        assert len(child.speeds) == len(child.route) - 1
        assert len(child.recharges) == len(child.route) - 1

        #So Deus sabe como isso funciona