# drone_optimizer/csv_exporter.py
import pandas as pd
from .route_calculator import RouteCalculator

def export_solution(best_solution, file_path):
    """Exporta a melhor solução para arquivo CSV"""
    route_calculator = RouteCalculator()
    records = []
    
    current_time = best_solution._time_to_seconds('06:00:00')
    current_day = 1
    current_battery = best_solution.drone.calculate_autonomy(best_solution.speeds[0])
    
    max_day_time = best_solution._time_to_seconds('19:00:00')
    late_penalty_time = best_solution._time_to_seconds('17:00:00')
    
    for i in range(len(best_solution.route) - 1):
        start_cep = best_solution.route[i]
        end_cep = best_solution.route[i + 1]
        
        start_time_str = best_solution._seconds_to_time(current_time)
        
        # Calcular parâmetros de voo
        flight_params = route_calculator.calculate_flight_parameters(
            start_cep, end_cep, best_solution.speeds[i], 
            best_solution.weather, current_day, start_time_str
        )
        
        flight_time = best_solution.drone.calculate_flight_time(
            flight_params['distance_km'], 
            flight_params['effective_speed_kmh']
        )
        
        energy_consumption = best_solution.drone.calculate_energy_consumption(
            flight_params['distance_km'], 
            best_solution.speeds[i]
        )
        
        # Determinar se há pouso
        needs_recharge = (energy_consumption + best_solution.drone.stop_penalty > current_battery)
        pouso = "SIM" if (needs_recharge or best_solution.recharges[i]) else "NÃO"
        
        # Calcular hora final
        end_time_seconds = current_time + flight_time + best_solution.drone.stop_penalty
        end_time_str = best_solution._seconds_to_time(end_time_seconds)
        
        # Criar registro
        record = {
            'CEP_inicial': start_cep['cep'],
            'Latitude_inicial': start_cep['latitude'],
            'Longitude_inicial': start_cep['longitude'],
            'Dia_do_voo': current_day,
            'Hora_inicial': start_time_str,
            'Velocidade': best_solution.speeds[i],
            'CEP_final': end_cep['cep'],
            'Latitude_final': end_cep['latitude'],
            'Longitude_final': end_cep['longitude'],
            'Pouso': pouso,
            'Hora_final': end_time_str
        }
        
        records.append(record)
        
        # Atualizar estado para próximo trecho
        if pouso == "SIM":
            current_battery = best_solution.drone.calculate_autonomy(best_solution.speeds[i])
            current_time += best_solution.drone.stop_penalty
        else:
            current_battery -= energy_consumption
        
        current_battery -= best_solution.drone.stop_penalty
        current_time = end_time_seconds
        
        # Verificar mudança de dia
        if current_time > max_day_time:
            current_day += 1
            current_time = best_solution._time_to_seconds('06:00:00')
    
    # Criar DataFrame e exportar
    df = pd.DataFrame(records)
    df.to_csv(file_path, index=False)
    print(f"Solução exportada para {file_path}")