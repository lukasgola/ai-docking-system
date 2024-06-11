import torch
import random
import numpy as np
from collections import deque
from model import Linear_QNet, QTrainer
import math
from game import AGV  # Assuming this is your environment
from helper import plot

POPULATION_SIZE = 100
GENOME_LENGTH = 20
MUTATION_RATE = 0.01
CROSSOVER_RATE = 0.7
GENERATIONS = 200

class Agent:
    def __init__(self):
        print('init')

    def random_genome(self, length):
        return [random.randint(0, 1) for _ in range(length)]
    
    def init_population(self, population_size, genome_length):
        return [self.random_genome(genome_length) for _ in range(population_size)]

    def fitness(self, genome):
        return sum(genome)
    
    def select_parent(self, population, fitness_values):
        total_fitness = sum(fitness_values)
        pick = random.uniform(0, total_fitness)
        current = 0
        for individual, fitness_value in zip(population, fitness_values):
            current += fitness_value
            if current > pick:
                return individual
            
    def crossover(self, parent1, parent2):
        if random.random() < CROSSOVER_RATE:
            crossover_point = random.randint(1, len(parent1) - 1)
            offspring1 = parent1[:crossover_point] + parent2[crossover_point:]
            offspring2 = parent2[:crossover_point] + parent1[crossover_point:]
            return offspring1, offspring2
        else:
            return parent1, parent2

    def mutate(self, genome):
        for i in range(len(genome)):
            if random.random() < MUTATION_RATE:
                genome[i] = 1 - genome[i]  # Toggle between 0 and 1
        return genome

def train():
    agent = Agent()

    population = agent.init_population(POPULATION_SIZE, GENOME_LENGTH)

    for generation in range(GENERATIONS):
        fitness_values = [agent.fitness(genome) for genome in population]
        
        new_population = []
        for _ in range(POPULATION_SIZE // 2):
            parent1 = agent.select_parent(population, fitness_values)
            parent2 = agent.select_parent(population, fitness_values)

            offspring1, offspring2 = agent.crossover(parent1, parent2)

            new_population.extend([agent.mutate(offspring1), agent.mutate(offspring2)])

        population = new_population

        fitness_values = [agent.fitness(genome) for genome in population]

        best_fitness = max(fitness_values)
        print(f"Generation {generation}: Best fitness = {best_fitness}")

    best_index = fitness_values.index(max(fitness_values))
    best_solution = population[best_index]

    print(f'Best solution: {best_solution}')
    print(f'Best fitness: {agent.fitness(best_solution)}')

if __name__ == '__main__':
    train()
