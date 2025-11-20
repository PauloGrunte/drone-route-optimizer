# tests/test_route_calculator.py
import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from drone_optimizer.route_calculator import RouteCalculator

def test_haversine_distance():
    calculator = RouteCalculator()
    
    # Distância entre dois pontos próximos
    distance = calculator.haversine_distance(
        -25.428, -49.267,  # Ponto 1
        -25.435, -49.275   # Ponto 2 (~1km de distância)
    )
    
    assert distance > 0
    assert distance < 2  # Deve ser menos de 2km

def test_bearing_calculation():
    calculator = RouteCalculator()
    
    bearing = calculator.calculate_bearing(
        -25.428, -49.267,  # Ponto 1
        -25.435, -49.275   # Ponto 2
    )
    
    assert 0 <= bearing <= 360

def test_flight_parameters_calculation():
    calculator = RouteCalculator()
    
    # Mock do weather (será testado separadamente)
    class MockWeather:
        def get_wind_for_time(self, day, time):
            return (10, 'E')  # 10 km/h, Leste
        
        def calculate_effective_speed(self, air_speed, bearing, wind_speed, wind_direction):
            return air_speed  # Simplificado para teste
    
    weather = MockWeather()
    
    start_coord = {'latitude': -25.428, 'longitude': -49.267}
    end_coord = {'latitude': -25.435, 'longitude': -49.275}
    
    params = calculator.calculate_flight_parameters(
        start_coord, end_coord, 36, weather, 1, '06:00:00'
    )
    
    assert 'distance_km' in params
    assert 'bearing_degrees' in params
    assert 'effective_speed_kmh' in params
    assert params['distance_km'] > 0