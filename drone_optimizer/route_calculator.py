# drone_optimizer/route_calculator.py
import math

class RouteCalculator:
    def __init__(self):
        self.earth_radius_km = 6371.0
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calcula distância entre duas coordenadas usando fórmula de Haversine"""
        # Converter para radianos
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Diferenças
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Fórmula de Haversine
        a = (math.sin(dlat/2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distance_km = self.earth_radius_km * c
        return distance_km
    
    def calculate_bearing(self, lat1, lon1, lat2, lon2):
        """Calcula o azimute (direção) entre duas coordenadas"""
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlon = lon2_rad - lon1_rad
        
        x = math.sin(dlon) * math.cos(lat2_rad)
        y = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon))
        
        bearing_rad = math.atan2(x, y)
        bearing_deg = math.degrees(bearing_rad)
        
        # Normalizar para 0-360
        bearing_deg = (bearing_deg + 360) % 360
        
        return bearing_deg
    
    def calculate_flight_parameters(self, start_coord, end_coord, air_speed, weather, day, start_time):
        """Calcula todos os parâmetros de voo entre duas coordenadas"""
        distance = self.haversine_distance(
            start_coord['latitude'], start_coord['longitude'],
            end_coord['latitude'], end_coord['longitude']
        )
        
        bearing = self.calculate_bearing(
            start_coord['latitude'], start_coord['longitude'],
            end_coord['latitude'], end_coord['longitude']
        )
        
        wind_speed, wind_direction = weather.get_wind_for_time(day, start_time)
        effective_speed = weather.calculate_effective_speed(
            air_speed, bearing, wind_speed, wind_direction
        )
        
        return {
            'distance_km': distance,
            'bearing_degrees': bearing,
            'effective_speed_kmh': effective_speed,
            'wind_speed_kmh': wind_speed,
            'wind_direction': wind_direction
        }