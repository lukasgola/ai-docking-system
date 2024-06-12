import random
import numpy as np

# Constants
POPULATION_SIZE = 100
GENOME_LENGTH = 10  # Sequence of actions
MUTATION_RATE = 0.01
CROSSOVER_RATE = 0.7
GENERATIONS = 200
MAX_DISTANCE = 100  # Maximum distance from the wall

# Car environment
class Car:
    def __init__(self, actions):
        self.position = MAX_DISTANCE
        self.speed = 0
        self.actions = actions
        self.crashed = False

    def update(self):
        for action in self.actions:
            if action == 0:  # Accelerate
                self.speed += 1
            elif action == 1:  # Brake
                self.speed -= 1
            self.position -= self.speed
            if self.position <= 0:
                self.crashed = True
                break
            if self.speed < 0:
                self.speed = 0

        print(f'Speed: {self.speed}')

# Genetic Algorithm
class GA:
    def __init__(self):
        pass

    def random_genome(self, length):
        return [random.randint(0, 1) for _ in range(length)]

    def init_population(self, population_size, genome_length):
        return [self.random_genome(genome_length) for _ in range(population_size)]

    def fitness(self, genome):
        car = Car(genome)
        car.update()
        if car.crashed:
            return -float('inf')  # Penalize crashing
        return -abs(car.position)  # Reward stopping close to the wall

    def select_parent(self, population, fitness_values):
        total_fitness = sum(fitness_values)
        if total_fitness == 0:
            return random.choice(population)  # Prevent division by zero if all fitness values are zero
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
        if genome is None:
            return self.random_genome(GENOME_LENGTH)  # Handle the case where genome is None
        for i in range(len(genome)):
            if random.random() < MUTATION_RATE:
                genome[i] = 1 - genome[i]
        return genome

def train():
    ga = GA()
    population = ga.init_population(POPULATION_SIZE, GENOME_LENGTH)

    for generation in range(GENERATIONS):
        fitness_values = [ga.fitness(genome) for genome in population]

        new_population = []
        for _ in range(POPULATION_SIZE // 2):
            parent1 = ga.select_parent(population, fitness_values)
            parent2 = ga.select_parent(population, fitness_values)

            if parent1 is None or parent2 is None:
                continue  # Skip if parent selection fails

            offspring1, offspring2 = ga.crossover(parent1, parent2)

            new_population.extend([ga.mutate(offspring1), ga.mutate(offspring2)])

        population = new_population

        fitness_values = [ga.fitness(genome) for genome in population]

        best_fitness = max(fitness_values)
        print(f"Generation {generation}: Best fitness = {best_fitness}")

    best_index = fitness_values.index(max(fitness_values))
    best_solution = population[best_index]

    print(f'Best solution: {best_solution}')
    print(f'Best fitness: {ga.fitness(best_solution)}')

if __name__ == '__main__':
    train()
