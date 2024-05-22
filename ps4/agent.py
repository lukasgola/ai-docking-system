import torch
import random
import numpy as np
from collections import deque
from ps4.game import AGV

# Agent setup

MAX_MEMORY = 100_100
BATCH_SIZE = 1000
LR = 0.001



class Agent:
    def __init__(self):
        
        self.n_games = 0
        self.epsilon = 0
        self.gama = 0
        self.memory = deque(maxlen=MAX_MEMORY)

        # model, trainer


    def get_state(self, game):

        player_pos = game.player_pos
        parking_pos = game.parking_pos

        state = [
            
        ]



        

    def remember(self, state, action, reward, next_state, done):
        pass

    def train_long_memory(self):
        pass

    def train_short_memory(self, state, action, reward, next_state, done):
        pass

    def get_action(self, state):
        pass


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = AGV()

    while True:
        #get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done = game.play_step(final_move)
        state_new = agent.get_state(game)

        #train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train the long memory
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            print("Game: ",  agent.n_games)

            #plot


            




if __name__ == '__main__':
    train()