import torch
import random
import numpy as np
from collections import deque
from game import AGV
from model import Linear_QNet, QTrainer
from helper import plot

# Agent setup

MAX_MEMORY = 100_100
BATCH_SIZE = 1000
LR = 0.001



class Agent:
    def __init__(self):
        
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(8, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def get_state(self, game):

        player_pos = game.player_pos
        parking_pos = game.parking_pos
        player_angle = game.player_angle

        d1 = game.d1
        d2 = game.d2
        d3 = game.d3

        dir_u = player_angle % 360 >= -45 and player_angle % 360 < 45
        dir_r = player_angle % 360 >= 45 and player_angle % 360 < 135
        dir_b = player_angle % 360 >= 135 and player_angle % 360 < 45
        dir_l = player_angle % 360 > -45 and player_angle % 360 < 45


        state = [
            # Danger straight
            #(d2 < 50 or d3 < 50),

            # Danger left
            #(d1 < 50),

            # Move direction
            dir_u,
            dir_r,
            dir_b,
            dir_l,

            parking_pos[0] < player_pos[0], # parking left
            parking_pos[0] > player_pos[0], # parking right
            parking_pos[1] < player_pos[1], # parking up
            parking_pos[1] > player_pos[1], # parking down

        ]

        return np.array(state, dtype=int)



        

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

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
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        #train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train the long memory
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            #plot
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


            




if __name__ == '__main__':
    train()