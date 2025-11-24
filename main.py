import numpy as np
import pandas as pd
from drone_optimizer.genetic_algorithm import GeneticAlgorithm
from drone_optimizer.drone_model import Drone
from drone_optimizer.weather_model import WeatherForecast
from drone_optimizer.csv_exporter import export_solution
import time

def load_ceps_coordinates(file_path):
    """Carrega as coordenadas dos CEPs do arquivo CSV"""
    try:
        df = pd.read_csv(file_path)
        ceps = []
        for _, row in df.iterrows():
            ceps.append({
                'cep': row['CEP'],
                'latitude': row['Latitude'],
                'longitude': row['Longitude']
            })
        return ceps
    except FileNotFoundError:
        print("Arquivo não encontrado")
        return None

def main():
    print("=== Otimizador de Rota para Drone UNIBRASIL Surveyor ===")
    print("Carregando configurações...")
    
    config = {
        'population_size': 100,  # Reduzido para melhor estabilidade
        'generations': 500,      # Reduzido para teste mais rápido
        'mutation_rate': 0.02,   # Mais baixo para estabilidade
        'crossover_rate': 0.7,   # Mais baixo inicialmente
        'elitism_count': 5,
        'tournament_size': 3
    }
    
    print("Carregando coordenadas dos CEPs...")
    ceps = load_ceps_coordinates('data/ceps_coordinates.csv')
    if ceps is None:
        print("Encerrando execução: dados necessários não encontrados.")
        return
    print("Inicializando modelos...")
    weather = WeatherForecast()
    drone = Drone()
    
    print("Iniciando algoritmo genético...")
    start_time = time.time()
    
    ga = GeneticAlgorithm(config, ceps, drone, weather)
    best_solution, fitness_history = ga.run()
    
    end_time = time.time()
    
    print(f"\n--- RESULTADOS ---")
    print(f"Tempo de execução: {end_time - start_time:.2f} segundos")
    print(f"Melhor fitness: {best_solution.fitness:.6f}")
    print(f"Custo total: R$ {best_solution.total_cost:.2f}")
    print(f"Tempo total de voo: {best_solution.total_flight_time/3600:.2f} horas")
    print(f"Número de recargas: {best_solution.num_recharges}")
    print(f"Dias utilizados: {best_solution.days_used}")
    
    print("\nExportando solução para CSV...")
    export_solution(best_solution, 'data/best_solution.csv')
    
    print("Processo concluído! Verifique o arquivo 'data/best_solution.csv'")

if __name__ == "__main__":
    main()