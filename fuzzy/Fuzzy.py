import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

class FuzzyLogicController:
    def __init__(self):
        #self.setup_fuzzy_logic()
        self.rotate()
        # self.show_plot()

    def setup_fuzzy_logic(self):
        
        # Define fuzzy variables
        self.dist1 = ctrl.Antecedent(np.arange(0, 800, 1), 'dist1')
        self.dist2 = ctrl.Antecedent(np.arange(0, 800, 1), 'dist2')
        self.dist3 = ctrl.Antecedent(np.arange(0, 800, 1), 'dist3')
        self.speedL = ctrl.Consequent(np.arange(-50, 100, 1), 'speedL')
        self.speedR = ctrl.Consequent(np.arange(-50, 100, 1), 'speedR')

        # Membership functions for distances
        self.dist1['close'] = fuzz.trapmf(self.dist1.universe, [0, 0, 30, 40])
        self.dist1['ok'] = fuzz.trapmf(self.dist1.universe, [30, 40, 50, 60])
        self.dist1['far'] = fuzz.trapmf(self.dist1.universe, [50, 60, 790, 800])

        self.dist2['close'] = fuzz.trimf(self.dist2.universe, [0, 0, 60])
        self.dist2['ok'] = fuzz.trimf(self.dist2.universe, [40, 60, 80])
        self.dist2['far'] = fuzz.trimf(self.dist2.universe, [60, 800, 800])
        
        self.dist3['close'] = fuzz.trimf(self.dist3.universe, [0, 0, 60])
        self.dist3['ok'] = fuzz.trimf(self.dist3.universe, [40, 60, 80])
        self.dist3['far'] = fuzz.trimf(self.dist3.universe, [60, 800, 800])

        # Membership functions for speed
        self.speedL['back'] = fuzz.trapmf(self.speedL.universe, [-50, -30, -15, 0])
        self.speedL['stop'] = fuzz.trapmf(self.speedL.universe, [-15, -5, 5, 15])
        self.speedL['slow'] = fuzz.trapmf(self.speedL.universe, [0, 10, 20, 30])
        self.speedL['fast'] = fuzz.trapmf(self.speedL.universe, [20, 30, 40, 50])

        self.speedR['back'] = fuzz.trapmf(self.speedR.universe, [-50, -30, -15, 0])
        self.speedR['stop'] = fuzz.trapmf(self.speedR.universe, [-15, -5, 5, 15])
        self.speedR['slow'] = fuzz.trapmf(self.speedR.universe, [0, 10, 20, 30])
        self.speedR['fast'] = fuzz.trapmf(self.speedR.universe, [20, 30, 40, 50])

        
        # Define fuzzy rules for speedL and speedR
        rules = [
            ctrl.Rule(self.dist1['close'] & self.dist2['close'] & self.dist3['close'], (self.speedL['back'], self.speedR['back'])),
            ctrl.Rule(self.dist1['close'] & self.dist2['close'] & self.dist3['far'], (self.speedL['slow'], self.speedR['stop'])),
            ctrl.Rule(self.dist1['close'] & self.dist2['far'] & self.dist3['far'], (self.speedL['fast'], self.speedR['fast'])),

            ctrl.Rule(self.dist1['far'] & self.dist2['far'] & self.dist3['far'], (self.speedL['slow'], self.speedR['fast'])),
            ctrl.Rule(self.dist1['far'] & self.dist2['far'] & self.dist3['close'], (self.speedL['slow'], self.speedR['back'])),
            ctrl.Rule(self.dist1['far'] & self.dist2['close'] & self.dist3['close'], (self.speedL['back'], self.speedR['back'])),

            ctrl.Rule(self.dist1['far'] & self.dist2['close'] & self.dist3['ok'], (self.speedL['back'], self.speedR['stop'])),
            ctrl.Rule(self.dist1['far'] & self.dist2['ok'] & self.dist3['close'], (self.speedL['stop'], self.speedR['back'])),
            

            # Remove duplicate
            ctrl.Rule(self.dist1['far'] & self.dist2['ok'] & self.dist3['far'], (self.speedL['stop'], self.speedR['fast'])),
            ctrl.Rule(self.dist1['far'] & self.dist2['far'] & self.dist3['ok'], (self.speedL['fast'], self.speedR['stop'])),
            ctrl.Rule(self.dist1['far'] & self.dist2['ok'] & self.dist3['ok'], (self.speedL['stop'], self.speedR['stop'])),

        ]

        # Initialize the control system with the list of rules
        self.steering_ctrl = ctrl.ControlSystem(rules)

        self.steering = ctrl.ControlSystemSimulation(self.steering_ctrl)

    def compute_action(self, d1, d2, d3):
        self.steering.input['dist1'] = d1
        self.steering.input['dist2'] = d2
        self.steering.input['dist3'] = d3
        self.steering.compute()

        return self.steering.output['speedL'], self.steering.output['speedR']
    
    def show_plot(self):
        # Visualize these universes and membership functions
        fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(8, 6))


        #ax0.plot(self.dist1.universe, self.dist1['close'].mf, 'b', linewidth=1.5, label='Close')
        #ax0.plot(self.dist1.universe, self.dist1['ok'].mf, 'g', linewidth=1.5, label='Ok')
        #ax0.plot(self.dist1.universe, self.dist1['far'].mf, 'r', linewidth=1.5, label='Far')
        #ax0.set_title('Dist1')
        #ax0.legend()

        ax1.plot(self.speedL.universe, self.speedL['back'].mf, 'b', linewidth=1.5, label='Back')
        ax1.plot(self.speedL.universe, self.speedL['stop'].mf, 'g', linewidth=1.5, label='Stop')
        ax1.plot(self.speedL.universe, self.speedL['slow'].mf, 'r', linewidth=1.5, label='Slow')
        ax1.plot(self.speedL.universe, self.speedL['fast'].mf, 'orange', linewidth=1.5, label='Fast')
        ax1.set_title('SpeedL')
        ax1.legend()

        ax2.plot(self.speedR.universe, self.speedR['back'].mf, 'b', linewidth=1.5, label='Back')
        ax2.plot(self.speedR.universe, self.speedR['stop'].mf, 'g', linewidth=1.5, label='Stop')
        ax2.plot(self.speedR.universe, self.speedR['slow'].mf, 'r', linewidth=1.5, label='Slow')
        ax2.plot(self.speedR.universe, self.speedR['fast'].mf, 'orange', linewidth=1.5, label='Fast')
        ax2.set_title('SpeedR')
        ax2.legend()

        # Turn off top/right axes
        for ax in (ax1, ax2):
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.get_xaxis().tick_bottom()
            ax.get_yaxis().tick_left()

        plt.tight_layout()
        plt.show()  # Display the plot


