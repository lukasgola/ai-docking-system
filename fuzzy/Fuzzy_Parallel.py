import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

class FuzzyParallelLogicController:
    def __init__(self):
        self.setup_fuzzy_logic()
        # self.show_plot()

    def setup_fuzzy_logic(self):
        # Define fuzzy variables
        self.diff = ctrl.Antecedent(np.arange(-800, 800, 1), 'diff')
        self.speedL = ctrl.Consequent(np.arange(-50, 100, 1), 'speedL')
        self.speedR = ctrl.Consequent(np.arange(-50, 100, 1), 'speedR')

        # Membership functions for difference
        self.diff['negative'] = fuzz.trapmf(self.diff.universe, [-800, -800, -20, -1])
        self.diff['zero'] = fuzz.trimf(self.diff.universe, [-2, 0, 2])
        self.diff['positive'] = fuzz.trapmf(self.diff.universe, [1, 20, 800, 800])

        # Membership functions for speed
        self.speedL['back'] = fuzz.trimf(self.speedL.universe, [-50, -20, 0])
        self.speedL['stop'] = fuzz.trimf(self.speedL.universe, [-5, 0, 5])
        self.speedL['slow'] = fuzz.trimf(self.speedL.universe, [0, 20, 40])
        self.speedL['fast'] =fuzz.trimf(self.speedL.universe, [30, 35, 40])

        self.speedR['back'] = fuzz.trimf(self.speedL.universe, [-50, -20, 0])
        self.speedR['stop'] = fuzz.trimf(self.speedL.universe, [-5, 0, 5])
        self.speedR['slow'] = fuzz.trimf(self.speedL.universe, [0, 30, 35])
        self.speedR['fast'] =fuzz.trimf(self.speedL.universe, [30, 35, 40])

        # Define fuzzy rules for speedL and speedR based on the difference
        rules = [
            ctrl.Rule(self.diff['negative'], (self.speedL['fast'], self.speedR['slow'])),
            ctrl.Rule(self.diff['zero'], (self.speedL['fast'], self.speedR['fast'])),
            ctrl.Rule(self.diff['positive'], (self.speedL['slow'], self.speedR['fast']))
        ]

        # Initialize the control system with the list of rules
        self.steering_ctrl = ctrl.ControlSystem(rules)
        self.steering = ctrl.ControlSystemSimulation(self.steering_ctrl)

    def compute_action(self, diff):
        self.steering.input['diff'] = diff
        self.steering.compute()

        return self.steering.output['speedL'], self.steering.output['speedR']
    
    def show_plot(self):
        # Visualize these universes and membership functions
        fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(8, 6))

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

