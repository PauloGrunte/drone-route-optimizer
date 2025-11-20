import math

class Drone:
    def __init__(self):
        self.max_speed = 96  # km/h
        self.min_speed = 36  # km/h
        self.base_autonomy = 5000 * 0.93  
        self.stop_penalty = 72  
        self.recharge_cost = 80.0 
        
    def calculate_autonomy(self, speed):
        """Calcula autonomia em segundos para uma dada velocidade"""
        if speed < self.min_speed or speed > self.max_speed:
            raise ValueError(f"Velocidade {speed} km/h fora dos limites permitidos")
        
        return self.base_autonomy * (36 / speed) ** 2
        
    def calculate_energy_consumption(self, distance_km, speed):
        """Calcula consumo de energia para uma distância e velocidade"""
        if speed == 0:
            return float('inf')
        
        flight_time_seconds = (distance_km / speed) * 3600
        return flight_time_seconds
        
    def get_available_speeds(self):
        """Retorna lista de velocidades permitidas (múltiplos de 4 entre min e max)"""
        speeds = []
        for speed in range(self.min_speed, self.max_speed + 1, 4):
            speeds.append(speed)
        return speeds
        
    def calculate_flight_time(self, distance_km, effective_speed):
        """Calcula tempo de voo em segundos"""
        if effective_speed == 0:
            return float('inf')
        return (distance_km / effective_speed) * 3600
        
    def validate_speed(self, speed):
        """Verifica se velocidade é válida"""
        return (speed >= self.min_speed and 
                speed <= self.max_speed and 
                speed % 4 == 0)