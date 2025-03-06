import pandas as pd
import random
from collections import deque


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


def get_neighbors(route, num_neighbors):
    neighbors = []
    for _ in range(num_neighbors):
        i, j = sorted(random.sample(range(1, len(route) - 1), 2))  
        new_route = route[:]
        new_route[i:j+1] = reversed(new_route[i:j+1])
        neighbors.append(new_route)
    return neighbors


def tabu_search(initial_route, distance_matrix, max_iterations, num_neighbors, tabu_size, tolerance):
    best_route = initial_route[:]
    best_distance = total_distance(best_route, distance_matrix)
    current_route = best_route[:]
    tabu_list = deque(maxlen=tabu_size)
    no_improve_count = 0
    distances = []

    for iteration in range(max_iterations):
        neighbors = get_neighbors(current_route, num_neighbors)
        best_neighbor = None
        best_neighbor_distance = float('inf')

        for neighbor in neighbors:
            neighbor_tuple = tuple(neighbor)
            neighbor_distance = total_distance(neighbor, distance_matrix)

            if neighbor_tuple in tabu_list and neighbor_distance >= best_distance:
                continue

            if neighbor_distance < best_neighbor_distance:
                best_neighbor = neighbor
                best_neighbor_distance = neighbor_distance

        if best_neighbor is None:
            break

        current_route = best_neighbor
        tabu_list.append(tuple(current_route))
        distances.append(best_distance)

        if best_neighbor_distance < best_distance:
            best_route = best_neighbor[:]
            best_distance = best_neighbor_distance
            no_improve_count = 0
        else:
            no_improve_count += 1

        if no_improve_count >= tolerance:
            break

    return best_route, best_distance
