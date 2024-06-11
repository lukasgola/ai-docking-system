import torch
import random
import numpy as np
from collections import deque
from game import AGV
from model import Linear_QNet, QTrainer
from helper import plot

# Genetic Algorithm setup
POPULATION_SIZE = 50
NUM_GENERATIONS = 20
NUM_PARENTS = 10
OFFSPRING_SIZE = 2
MUTATION_RATE = 0.1
NUM_FEATURES = 11  # Number of features in the state representation

# Agent setup
MAX_MEMORY = 100_100
BATCH_SIZE = 1000
EPISODE_LENGTH = 1000
LR = 0.001

class GeneticAgent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate

    def initialize_population(self):
        population = []
        for _ in range(POPULATION_SIZE):
            individual = [random.uniform(-1, 1) for _ in range(NUM_FEATURES)]
            population.append(individual)
        return population

    def evaluate_population(self, population):
        scores = []
        for individual in population:
            score = self.evaluate_individual(individual)
            scores.append(score)
        return scores

    def evaluate_individual(self, individual):
        game = AGV()
        total_reward = 0
        for _ in range(EPISODE_LENGTH):
            state = self.get_state(game)
            action = self.choose_action(state, individual)
            reward, game_over, score = game.play_step(action)
            total_reward += reward
            if game_over:
                break
        return total_reward

    def choose_action(self, state, individual):
        action_value = np.dot(state, individual)
        if action_value < -0.33:
            return [1, 0, 0]  # Left
        elif action_value < 0.33:
            return [0, 1, 0]  # Straight
        else:
            return [0, 0, 1]  # Right

    def select_parents(self, population, scores):
        parents_indices = np.argsort(scores)[-NUM_PARENTS:]
        parents = [population[i] for i in parents_indices]
        return parents

    def crossover(self, parents):
        offspring = []
        for _ in range(OFFSPRING_SIZE):
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            crossover_point = random.randint(1, len(parent1) - 1)
            child = parent1[:crossover_point] + parent2[crossover_point:]
            offspring.append(child)
        return offspring

    def mutate(self, offspring_population):
        for i in range(len(offspring_population)):
            if random.random() < MUTATION_RATE:
                gene_to_mutate = random.randint(0, len(offspring_population[i]) - 1)
                offspring_population[i][gene_to_mutate] = random.uniform(-1, 1)
        return offspring_population

    def train_genetic(self):
        best_individual = None
        best_score = float('-inf')
        population = self.initialize_population()
        
        for generation in range(NUM_GENERATIONS):
            # Evaluate the population
            scores = self.evaluate_population(population)
            
            # Debugging: Ensure population and scores have the same length
            print(f"Generation {generation}: Population Size: {len(population)}, Scores Size: {len(scores)}")
            
            if len(population) != len(scores):
                raise ValueError("Population size and scores size do not match.")
            
            # Select the best parents
            parents = self.select_parents(population, scores)
            
            # Generate offspring
            offspring = self.crossover(parents)
            offspring = self.mutate(offspring)
            
            # Update population
            population = parents + offspring
            
            # Ensure the new population size is correct
            print(f"Generation {generation}: Population Size After Reproduction: {len(population)}")
            
            if len(population) != POPULATION_SIZE:
                raise ValueError("Population size after reproduction does not match POPULATION_SIZE.")
            
            # Determine the best score and individual in this generation
            best_generation_score = max(scores)
            best_individual_index = scores.index(best_generation_score)
            
            # Debugging: Ensure the best individual's index is within the bounds
            print(f"Generation {generation}: Best Score Index: {best_individual_index}, Best Score: {best_generation_score}")
            
            if best_generation_score > best_score:
                best_score = best_generation_score
                best_individual = population[best_individual_index]
            
            print(f"Generation {generation}: Best Score: {best_generation_score}")
        
        return best_individual


    
    def get_state(self, game):
        player_pos = game.player_pos
        parking_pos = game.parking_pos
        player_angle = game.player_angle

        d1 = game.d1
        d2 = game.d2
        d3 = game.d3

        # Relative positions of the parking spot
        relative_parking_x = parking_pos[0] - player_pos[0]
        relative_parking_y = parking_pos[1] - player_pos[1]

        state = [
            d1,  # Distance to the nearest wall from bottom_left
            d2,  # Distance to the nearest wall from top_left
            d3,  # Distance to the nearest wall from top_right
            player_angle,
            player_pos[0],
            player_pos[1],
            relative_parking_x,
            relative_parking_y,
            game.parking_rect.width,
            game.parking_rect.height,
            game.score
        ]

        return np.array(state, dtype=np.float32)

if __name__ == '__main__':
    agent = GeneticAgent()
    best_individual = agent.train_genetic()
    print("Best Individual:", best_individual)
