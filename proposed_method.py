import pandas as pd
import numpy as np
import random
from sklearn.cluster import KMeans


def cluster_points(distance_matrix, initial_route, n_clusters):
    
    coordinates = []
    points = []
    for point in initial_route:
        coords = distance_matrix[
            (distance_matrix['point_a'] == str(point))
        ][['lat', 'lon']].iloc[0].values
        coordinates.append(coords)
        points.append(point)
    coordinates = np.array(coordinates)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(coordinates)
    
    return dict(zip(points, cluster_labels))


def distance(point1, point2, distance_matrix):
    point1=str(point1).strip()
    point2=str(point2).strip()
    if point1 != point2:
        if len(distance_matrix[(distance_matrix["point_a"] == point1) & 
                        (distance_matrix["point_b"] == point2)])>0:
                return distance_matrix[(distance_matrix["point_a"] == point1) & 
                        (distance_matrix["point_b"] == point2)]["distance_km"].values[0]
        else:
            return 0
    else:
        return 0


def total_distance(route, distance_matrix): 
    total_distance=0
    for i in range(len(route)-1):
        total_distance+=distance(route[i], route[i+1], distance_matrix)
    return total_distance

       
def select_parents(population, fitnesses):
    total_fitness = sum(fitnesses)
    selection_probs = [fitness / total_fitness for fitness in fitnesses]
    parent1 = random.choices(population, weights=selection_probs, k=1)[0]
    parent2 = random.choices(population, weights=selection_probs, k=1)[0]
    return parent1, parent2


def crossover(parent1, parent2):
    parent1 = list(parent1)
    parent2 = list(parent2)
    crossover_point = random.randint(0, len(parent1))
    child1 = parent1[:crossover_point]
    child2 = parent2[:crossover_point]
    remaining_poi_parent2 = [poi for poi in parent2 if poi not in child1]
    child1.extend(remaining_poi_parent2)
    remaining_poi_parent1 = [poi for poi in parent1 if poi not in child2]
    child2.extend(remaining_poi_parent1)
    return child1, child2
    

def mutate(route, mutation_rate):
    random_number = random.random()
    if random_number  <= mutation_rate:
        index1, index2 = random.sample(range(len(route)), 2)
        route[index1], route[index2] = route[index2], route[index1]
    return route


def fitness(route, distance_matrix):
    return 1 / total_distance(route, distance_matrix)


def initial_population(population_size, route):
  population = []
  for _ in range(population_size):
      new_route = route.copy()
      idx1, idx2 = random.sample(range(len(new_route)), 2) 
      new_route[idx1], new_route[idx2] = new_route[idx2], new_route[idx1]
      population.append(new_route)
  return population




def genetic_algorithm_proposed(distance_matrix, initial_route, population_size, mutation_rate, generations,tolerance, elite_size, first_location):
    
    init_distance=total_distance(initial_route, distance_matrix)
    if (init_distance==0):
        return []
        
    population = initial_population(population_size, initial_route)
    population = [[first_location] + route for route in population]

    best_km_list=[10**10]
    no_improvement_count=0
    gen=0
    
    while gen < generations:
        new_population = []
        fitnesses = [fitness(route, distance_matrix) for route in population]
        
        # for parallel processing
        # from multiprocessing import Pool
        # import os
        # num_cpus = os.cpu_count() - 2
        # with Pool(processes=num_cpus) as pool:
            # fitnesses = pool.starmap(fitness, [(route, distance_matrix) for route in population])

        best_route = min(population, key=lambda route: total_distance(route, distance_matrix))
        best_routes = sorted(population, key=lambda route: total_distance(route, distance_matrix))[:elite_size]
        
        best_km= total_distance(best_route, distance_matrix)
        if best_km_list[-1]>best_km + 1:
            no_improvement_count=0
        else:
            no_improvement_count+=1
        best_km_list.append(best_km)

        new_population.extend(best_routes)  

        for _ in range((population_size - elite_size) // 2):
            parent1, parent2 = select_parents(population, fitnesses)
            parent1_without_first = parent1[1:]
            parent2_without_first = parent2[1:]
    
            child1, child2 = crossover(parent1_without_first, parent2_without_first)
            child1 = mutate(child1, mutation_rate)
            child2 = mutate(child2, mutation_rate)
            
            child1 = [first_location] + child1
            child2 = [first_location] + child2
            
            new_population.extend([child1, child2])
        population = new_population
        final_route = min(population, key=lambda route: total_distance(route,distance_matrix))
        
        if (no_improvement_count > tolerance) and mutation_rate<0.55:
            mutation_rate*=1.09
                
        gen+=1

    return final_route