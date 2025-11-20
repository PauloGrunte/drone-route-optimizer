import math

class WeatherForecast:
    def __init__(self):
        self.wind_data = {
            1: {
                '06h': (17, 'ENE'), '09h': (18, 'E'), '12h': (19, 'E'),
                '15h': (19, 'E'), '18h': (20, 'E'), '21h': (20, 'E')
            },
            2: {
                '06h': (20, 'E'), '09h': (19, 'E'), '12h': (16, 'E'),
                '15h': (19, 'E'), '18h': (21, 'E'), '21h': (21, 'E')
            },
            3: {
                '06h': (15, 'ENE'), '09h': (17, 'NE'), '12h': (8, 'NE'),
                '15h': (20, 'E'), '18h': (16, 'E'), '21h': (15, 'ENE')
            },
            4: {
                '06h': (8, 'ENE'), '09h': (11, 'ENE'), '12h': (7, 'NE'),
                '15h': (6, 'NE'), '18h': (11, 'E'), '21h': (11, 'E')
            },
            5: {
                '06h': (3, 'WSW'), '09h': (3, 'WSW'), '12h': (7, 'WSW'),
                '15h': (7, 'SSW'), '18h': (10, 'E'), '21h': (11, 'ENE')
            },
            6: {
                '06h': (4, 'NE'), '09h': (5, 'ENE'), '12h': (4, 'NE'),
                '15h': (8, 'E'), '18h': (15, 'E'), '21h': (15, 'E')
            },
            7: {
                '06h': (5, 'NE'), '09h': (6, 'ENE'), '12h': (5, 'NE'),
                '15h': (9, 'E'), '18h': (16, 'E'), '21h': (16, 'E')
            }
        }
        
        self.direction_angles = {
            'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
            'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
            'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
            'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5
        }
    
    def get_wind_for_time(self, day, hour_minute):
        hour_str = self._get_time_slot(hour_minute)
        
        if day not in self.wind_data or hour_str not in self.wind_data[day]:
            return (15, 'E')  # 15 km/h, Leste
        
        return self.wind_data[day][hour_str]
    
    def _get_time_slot(self, hour_minute):
        hour = hour_minute.split(':')[0]
        minute = int(hour_minute.split(':')[1])
        
        if minute < 30:
            return f"{hour}h"
        else:
            next_hour = int(hour) + 1
            return f"{next_hour:02d}h"
    
    def calculate_effective_speed(self, air_speed, flight_direction, wind_speed, wind_direction):
        """Calcula velocidade efetiva considerando vento"""
        flight_angle_rad = math.radians(flight_direction)
        wind_angle_rad = math.radians(self.direction_angles[wind_direction])
        
        # Componentes da velocidade do drone
        drone_x = air_speed * math.sin(flight_angle_rad)
        drone_y = air_speed * math.cos(flight_angle_rad)
        
        # Componentes do vento
        wind_x = wind_speed * math.sin(wind_angle_rad)
        wind_y = wind_speed * math.cos(wind_angle_rad)
        
        # Velocidade efetiva (solo)
        effective_x = drone_x + wind_x
        effective_y = drone_y + wind_y
        
        # Magnitude da velocidade efetiva
        effective_speed = math.sqrt(effective_x**2 + effective_y**2)
        
        return max(0.1, effective_speed)  # Evitar divisão por zero
    
    def get_wind_angle(self, direction_str):
        """Retorna ângulo em graus para uma direção cardinal"""
        return self.direction_angles.get(direction_str, 90)  # Default: Leste