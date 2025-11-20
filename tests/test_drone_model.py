# tests/test_drone_model.py
import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from drone_optimizer.drone_model import Drone

def test_drone_initialization():
    drone = Drone()
    assert drone.max_speed == 96
    assert drone.min_speed == 36
    assert drone.base_autonomy == 5000 * 0.93

def test_autonomy_calculation():
    drone = Drone()
    
    # Teste na velocidade de referência
    autonomy_36 = drone.calculate_autonomy(36)
    assert abs(autonomy_36 - 4650) < 1  # 5000 * 0.93
    
    # Teste em outra velocidade
    autonomy_48 = drone.calculate_autonomy(48)
    expected_48 = 4650 * (36/48) ** 2
    assert abs(autonomy_48 - expected_48) < 1

def test_energy_consumption():
    drone = Drone()
    
    consumption = drone.calculate_energy_consumption(10, 36)
    expected = (10 / 36) * 3600  # 1000 segundos
    assert abs(consumption - expected) < 1

def test_available_speeds():
    drone = Drone()
    speeds = drone.get_available_speeds()
    
    assert len(speeds) > 0
    assert all(speed % 4 == 0 for speed in speeds)
    assert min(speeds) == 36
    assert max(speeds) == 96

def test_speed_validation():
    drone = Drone()
    
    assert drone.validate_speed(36) == True
    assert drone.validate_speed(40) == True
    assert drone.validate_speed(96) == True
    assert drone.validate_speed(35) == False
    assert drone.validate_speed(97) == False
    assert drone.validate_speed(37) == False  # Não é múltiplo de 4