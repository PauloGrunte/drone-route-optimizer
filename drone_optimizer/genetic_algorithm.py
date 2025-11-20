import numpy as np
import random
from copy import deepcopy
from .route_calculator import RouteCalculator

class Individual:
    def __init__(self, ceps, drone, weather):
        self.ceps = ceps
        self.drone = drone
        self.weather = weather
        self.route_calculator = RouteCalculator()
        
        # Genes
        self.route = []  # Ordem dos CEPs (como dicionários)
        self.speeds = []  # Velocidades para cada trecho
        self.recharges = []  # Pontos de recarga
        self.departure_times = []  # Horários de partida
        
        # Fitness e métricas
        self.fitness = 0.0
        self.total_cost = 0.0
        self.total_flight_time = 0.0
        self.num_recharges = 0
        self.days_used = 0
        self.is_valid = True
        
        self.initialize_random()
    
    def initialize_random(self):
        """Inicializa indivíduo com genes aleatórios"""
        # Encontrar Unibrasil
        unibrasil = next((cep for cep in self.ceps if cep['cep'] == '82821020'), self.ceps[0])
        
        # Gerar rota aleatória (excluindo Unibrasil do meio)
        other_ceps = [cep for cep in self.ceps if cep['cep'] != '82821020']
        random.shuffle(other_ceps)
        
        # Garantir que a rota seja uma lista de dicionários
        self.route = [unibrasil] + other_ceps + [unibrasil]
        
        # Gerar velocidades aleatórias válidas
        available_speeds = self.drone.get_available_speeds()
        self.speeds = [random.choice(available_speeds) for _ in range(len(self.route)-1)]
        
        # Gerar pontos de recarga (20% de chance por ponto)
        self.recharges = [random.random() < 0.2 for _ in range(len(self.route)-1)]
        
        # Gerar horários de partida iniciais
        self.departure_times = ['06:00:00']  # Começa às 6h
        
        self.evaluate()
    
    def evaluate(self):
        """Avalia fitness do indivíduo"""
        try:
            self._calculate_metrics()
            self._calculate_fitness()
            self.is_valid = True
        except Exception as e:
            # print(f"Erro na avaliação: {e}")  # Descomente para debug
            self.fitness = 0.0001
            self.is_valid = False
    
    def _calculate_metrics(self):
        """Calcula métricas de custo e tempo"""
        total_flight_time = 0
        total_cost = 0
        current_battery = self.drone.calculate_autonomy(self.speeds[0])
        current_day = 1
        current_time = self._time_to_seconds('06:00:00')
        num_recharges = 0
        
        max_day_time = self._time_to_seconds('19:00:00')
        late_penalty_time = self._time_to_seconds('17:00:00')
        
        for i in range(len(self.route) - 1):
            start_cep = self.route[i]
            end_cep = self.route[i + 1]
            
            # Calcular parâmetros de voo
            start_time_str = self._seconds_to_time(current_time)
            flight_params = self.route_calculator.calculate_flight_parameters(
                start_cep, end_cep, self.speeds[i], self.weather, 
                current_day, start_time_str
            )
            
            # Tempo de voo
            flight_time = self.drone.calculate_flight_time(
                flight_params['distance_km'], 
                flight_params['effective_speed_kmh']
            )
            
            # Consumo de bateria
            energy_consumption = self.drone.calculate_energy_consumption(
                flight_params['distance_km'], 
                self.speeds[i]
            )
            
            # Verificar se precisa recarregar
            needs_recharge = (energy_consumption + self.drone.stop_penalty > current_battery)
            
            if needs_recharge or self.recharges[i]:
                # Pouso para recarga
                num_recharges += 1
                current_battery = self.drone.calculate_autonomy(self.speeds[i])
                
                # Custo adicional se após 17h
                if current_time > late_penalty_time:
                    total_cost += self.drone.recharge_cost
                
                # Tempo de parada para recarga (considerar próximo dia se necessário)
                current_time += self.drone.stop_penalty
                if current_time > max_day_time:
                    current_day += 1
                    if current_day > 7:
                        raise ValueError("Prazo de 7 dias excedido")
                    current_time = self._time_to_seconds('06:00:00')
            
            # Atualizar bateria e tempo
            current_battery -= energy_consumption
            if current_battery < 0:
                raise ValueError("Bateria insuficiente")
                
            current_time += flight_time
            total_flight_time += flight_time
            
            # Penalidade de parada para fotos
            current_battery -= self.drone.stop_penalty
            current_time += self.drone.stop_penalty
            
            if current_battery < 0:
                raise ValueError("Bateria insuficiente após parada")
            
            # Verificar horário
            if current_time > max_day_time:
                current_day += 1
                if current_day > 7:
                    raise ValueError("Prazo de 7 dias excedido")
                current_time = self._time_to_seconds('06:00:00')
        
        self.total_flight_time = total_flight_time
        self.total_cost = total_cost + (total_flight_time / 3600) * 10  # R$10 por hora
        self.num_recharges = num_recharges
        self.days_used = current_day
    
    def _calculate_fitness(self):
        """Calcula fitness baseado no custo total"""
        # Fitness é inversamente proporcional ao custo
        base_fitness = 1.0 / (1.0 + self.total_cost)
        
        # Bônus por usar menos dias
        day_bonus = (8 - self.days_used) * 0.1
        
        # Bônus por menos recargas
        recharge_bonus = (10 - self.num_recharges) * 0.05
        
        self.fitness = base_fitness * (1 + day_bonus + recharge_bonus)
    
    def _time_to_seconds(self, time_str):
        """Converte string de tempo para segundos"""
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s
    
    def _seconds_to_time(self, seconds):
        """Converte segundos para string de tempo"""
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"

class GeneticAlgorithm:
    def __init__(self, config, ceps, drone, weather):
        self.config = config
        self.ceps = ceps
        self.drone = drone
        self.weather = weather
        self.population = []
        self.best_individual = None
        self.fitness_history = []
        
        self.initialize_population()
    
    def initialize_population(self):
        """Inicializa população com indivíduos aleatórios"""
        self.population = []
        for _ in range(self.config['population_size']):
            individual = Individual(self.ceps, self.drone, self.weather)
            self.population.append(individual)
        
        self.update_best_individual()
    
    def update_best_individual(self):
        """Atualiza o melhor indivíduo da população"""
        valid_individuals = [ind for ind in self.population if ind.is_valid]
        if valid_individuals:
            self.best_individual = max(valid_individuals, key=lambda x: x.fitness)
        else:
            # Se não há válidos, pega o primeiro e força reavaliação
            self.best_individual = self.population[0]
            self.best_individual.evaluate()
    
    def selection(self):
        """Seleção por torneio"""
        tournament = random.sample(self.population, self.config['tournament_size'])
        valid_tournament = [ind for ind in tournament if ind.is_valid]
        
        if valid_tournament:
            return max(valid_tournament, key=lambda x: x.fitness)
        else:
            return random.choice(self.population)
    
    def crossover(self, parent1, parent2):
        """Crossover OX (Order Crossover) para rotas"""
        child1 = Individual(self.ceps, self.drone, self.weather)
        child2 = Individual(self.ceps, self.drone, self.weather)
        
        # Crossover para rota
        route1, route2 = self._ox_crossover_robust(parent1.route, parent2.route)
        child1.route = route1
        child2.route = route2
        
        # Crossover uniforme para velocidades e recargas
        child1.speeds = self._uniform_crossover(parent1.speeds, parent2.speeds)
        child2.speeds = self._uniform_crossover(parent2.speeds, parent1.speeds)
        
        child1.recharges = self._uniform_crossover_bool(parent1.recharges, parent2.recharges)
        child2.recharges = self._uniform_crossover_bool(parent2.recharges, parent1.recharges)
        
        child1.evaluate()
        child2.evaluate()
        
        return child1, child2
    
    def _ox_crossover_robust(self, route1, route2):
        """Order Crossover robusto - versão corrigida"""
        size = len(route1)
        
        # Garantir que as rotas são válidas
        if not all(isinstance(point, dict) for point in route1 + route2):
            return route1, route2  # Fallback para rotas originais
        
        # Escolher pontos de corte (excluindo primeiro e último que são Unibrasil)
        start, end = sorted(random.sample(range(1, size-1), 2))
        
        # Filho 1
        child1 = [None] * size
        child1[0] = route1[0]  # Unibrasil no início
        child1[-1] = route1[-1]  # Unibrasil no final
        
        # Copiar segmento do parent1
        child1[start:end+1] = route1[start:end+1]
        
        # Preencher restante com genes do parent2
        parent2_pos = 0
        for i in range(1, size-1):
            if child1[i] is None:
                # Encontrar próximo gene do parent2 que não está em child1
                while parent2_pos < size:
                    gene = route2[parent2_pos]
                    parent2_pos += 1
                    
                    # Verificar se é um gene válido e não está na child1
                    if (isinstance(gene, dict) and 
                        gene.get('cep') != '82821020' and 
                        gene not in child1):
                        child1[i] = gene
                        break
        
        # Filho 2 (processo similar)
        child2 = [None] * size
        child2[0] = route2[0]
        child2[-1] = route2[-1]
        child2[start:end+1] = route2[start:end+1]
        
        parent1_pos = 0
        for i in range(1, size-1):
            if child2[i] is None:
                while parent1_pos < size:
                    gene = route1[parent1_pos]
                    parent1_pos += 1
                    
                    if (isinstance(gene, dict) and 
                        gene.get('cep') != '82821020' and 
                        gene not in child2):
                        child2[i] = gene
                        break
        
        # Garantir que não há None nas rotas finais
        child1 = [gene if gene is not None else route1[i] for i, gene in enumerate(child1)]
        child2 = [gene if gene is not None else route2[i] for i, gene in enumerate(child2)]
        
        return child1, child2
    
    def _uniform_crossover(self, list1, list2):
        """Crossover uniforme para listas numéricas"""
        child = []
        for i in range(len(list1)):
            if random.random() < 0.5:
                child.append(list1[i])
            else:
                child.append(list2[i])
        return child
    
    def _uniform_crossover_bool(self, list1, list2):
        """Crossover uniforme para listas booleanas"""
        child = []
        for i in range(len(list1)):
            if random.random() < 0.5:
                child.append(list1[i])
            else:
                child.append(list2[i])
        return child
    
    def mutation(self, individual):
        """Aplica mutações no indivíduo"""
        mutated = deepcopy(individual)
        
        # Mutação de rota (swap) - apenas entre pontos que não são Unibrasil
        if random.random() < self.config['mutation_rate']:
            # Escolher índices que não são o primeiro nem último
            available_indices = list(range(1, len(mutated.route)-1))
            if len(available_indices) >= 2:
                idx1, idx2 = random.sample(available_indices, 2)
                mutated.route[idx1], mutated.route[idx2] = mutated.route[idx2], mutated.route[idx1]
        
        # Mutação de velocidade
        if random.random() < self.config['mutation_rate']:
            idx = random.randint(0, len(mutated.speeds)-1)
            available_speeds = self.drone.get_available_speeds()
            mutated.speeds[idx] = random.choice(available_speeds)
        
        # Mutação de recarga
        if random.random() < self.config['mutation_rate']:
            idx = random.randint(0, len(mutated.recharges)-1)
            mutated.recharges[idx] = not mutated.recharges[idx]
        
        mutated.evaluate()
        return mutated
    
    def run(self):
        """Executa o algoritmo genético"""
        print(f"Executando AG por {self.config['generations']} gerações...")
        
        for generation in range(self.config['generations']):
            new_population = []
            
            # Elitismo - pegar os melhores indivíduos válidos
            valid_individuals = [ind for ind in self.population if ind.is_valid]
            if valid_individuals:
                elite = sorted(valid_individuals, key=lambda x: x.fitness, reverse=True)[:self.config['elitism_count']]
            else:
                elite = self.population[:self.config['elitism_count']]
            new_population.extend(elite)
            
            # Preencher resto da população
            while len(new_population) < self.config['population_size']:
                parent1 = self.selection()
                parent2 = self.selection()
                
                if random.random() < self.config['crossover_rate']:
                    try:
                        child1, child2 = self.crossover(parent1, parent2)
                    except Exception as e:
                        # Em caso de erro no crossover, usar os pais
                        # print(f"Erro no crossover: {e}")  # Descomente para debug
                        child1, child2 = parent1, parent2
                else:
                    child1, child2 = parent1, parent2
                
                child1 = self.mutation(child1)
                child2 = self.mutation(child2)
                
                new_population.extend([child1, child2])
            
            # Manter tamanho da população
            self.population = new_population[:self.config['population_size']]
            self.update_best_individual()
            self.fitness_history.append(self.best_individual.fitness)
            
            if generation % 100 == 0:
                valid_count = sum(1 for ind in self.population if ind.is_valid)
                print(f"Geração {generation}: Melhor fitness = {self.best_individual.fitness:.6f}, "
                      f"Válidos: {valid_count}/{len(self.population)}")
        
        print("Otimização concluída!")
        return self.best_individual, self.fitness_history