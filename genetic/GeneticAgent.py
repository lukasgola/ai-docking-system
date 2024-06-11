# https://machinelearningmastery.com/simple-genetic-algorithm-from-scratch-in-python/
# https://medium.com/@Data_Aficionado_1083/genetic-algorithms-optimizing-success-through-evolutionary-computing-f4e7d452084f
# https://www.youtube.com/watch?v=EJeTWRP3Bd0&ab_channel=DigitalSreeni

import torch
import random
import numpy as np
from collections import deque
from model import Linear_QNet, QTrainer
import math
from game import AGV  # Assuming this is your environment

POPULATION_SIZE = 100
MUTATION_RATE = 0.1
NUM_GENERATIONS = 50

class Agent:
    def __init__(self, model):
        self.model = model
        self.fitness = 0

    def get_state(self, game):
        player_pos = game.player_pos
        player_angle = game.player_angle

        d1 = game.d1 / game.screen_width  # Normalized distance
        d2 = game.d2 / game.screen_width  # Normalized distance
        d3 = game.d3 / game.screen_width  # Normalized distance

        norm_player_x = player_pos[0] / game.screen_width
        norm_player_y = player_pos[1] / game.screen_height

        dx, dy, distance = game.compute_relative_position()
        relative_angle = game.compute_relative_angle()

        state = [
            d1,
            d2,
            d3,
            math.sin(math.radians(player_angle)),
            math.cos(math.radians(player_angle)),
            norm_player_x,
            norm_player_y,
            dx,
            dy,
            distance,
            relative_angle
        ]

        return np.array(state, dtype=float)

    def set_model_weights(self, weights):
        self.model.load_state_dict(weights)

    def get_model_weights(self):
        return self.model.state_dict()

def create_population():
    population = []
    for _ in range(POPULATION_SIZE):
        model = Linear_QNet(11, 256, 3)  # Assuming this is how you create your model
        agent = Agent(model)
        population.append(agent)
    return population

def calculate_fitness(agent, game):
    score = 0
    for _ in range(100):  # Play the game for 100 steps
        state = agent.get_state(game)
        state_tensor = torch.tensor(state, dtype=torch.float)
        prediction = agent.model(state_tensor)
        action = torch.argmax(prediction).item()
        final_move = action  # Changed to single integer action
        reward, done, step_score = game.play_step(final_move)
        score += step_score
        if done:
            game.reset_game()
    agent.fitness = score 


def crossover(parent1, parent2):
    child_model = Linear_QNet(11, 256, 3)
    for key in child_model.state_dict().keys():
        if random.random() < 0.5:
            child_model.state_dict()[key] = parent1.get_model_weights()[key]
        else:
            child_model.state_dict()[key] = parent2.get_model_weights()[key]
    return Agent(child_model)

def mutate(agent):
    child_model = agent.model
    for key in child_model.state_dict().keys():
        if random.random() < MUTATION_RATE:
            child_model.state_dict()[key] += torch.randn_like(child_model.state_dict()[key]) * 0.1  # Mutation strength
    return Agent(child_model)

def select_parents(population):
    return random.choices(population, weights=[agent.fitness for agent in population], k=2)

def evolve_population(population):
    new_population = []
    for _ in range(POPULATION_SIZE):
        parent1, parent2 = select_parents(population)
        child = crossover(parent1, parent2)
        child = mutate(child)
        new_population.append(child)
    return new_population

def train():
    population = create_population()
    game = AGV()  # Assuming this is your game environment
    for generation in range(NUM_GENERATIONS):
        for agent in population:
            calculate_fitness(agent, game)
        population.sort(key=lambda x: x.fitness, reverse=True)
        print(f"Generation {generation + 1}, Best Fitness: {population[0].fitness}")
        if sum(agent.fitness for agent in population) == 0:
            print("All agents have zero fitness. Exiting training.")
            return
        population = evolve_population(population)


if __name__ == '__main__':
    train()
