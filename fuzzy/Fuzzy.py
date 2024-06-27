import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

class FuzzyLogicController:
    def __init__(self):
        self.setup_fuzzy_logic()
        self.show_plot()

    def setup_fuzzy_logic(self):
        
        # Define fuzzy variables
        self.dist1 = ctrl.Antecedent(np.arange(0, 800, 1), 'dist1')
        self.dist2 = ctrl.Antecedent(np.arange(0, 800, 1), 'dist2')
        self.dist3 = ctrl.Antecedent(np.arange(0, 800, 1), 'dist3')
        self.speedL = ctrl.Consequent(np.arange(-50, 100, 1), 'speedL')
        self.speedR = ctrl.Consequent(np.arange(-50, 100, 1), 'speedR')

        # Membership functions for distances
        self.dist1['close'] = fuzz.trimf(self.dist1.universe, [0, 0, 50])
        self.dist1['ok'] = fuzz.trimf(self.dist1.universe, [40, 60, 80])
        self.dist1['far'] = fuzz.trimf(self.dist1.universe, [60, 800, 800])
        
        self.dist2['close'] = fuzz.trimf(self.dist2.universe, [0, 0, 50])
        self.dist2['ok'] = fuzz.trimf(self.dist2.universe, [40, 60, 80])
        self.dist2['far'] = fuzz.trimf(self.dist2.universe, [60, 800, 800])
        
        self.dist3['close'] = fuzz.trimf(self.dist3.universe, [0, 0, 50])
        self.dist3['ok'] = fuzz.trimf(self.dist3.universe, [40, 60, 80])
        self.dist3['far'] = fuzz.trimf(self.dist3.universe, [60, 800, 800])

        # Membership functions for speed
        self.speedL['back'] = fuzz.trimf(self.speedL.universe, [-50, -10, 0])
        self.speedL['stop'] = fuzz.trimf(self.speedL.universe, [-15, 0, 15])
        self.speedL['slow'] = fuzz.trimf(self.speedL.universe, [0, 10, 30])
        self.speedL['fast'] = fuzz.trimf(self.speedL.universe, [20, 40, 40])

        # Membership functions for speed
        self.speedR['back'] = fuzz.trimf(self.speedR.universe, [-50, -10, 0])
        self.speedR['stop'] = fuzz.trimf(self.speedR.universe, [-15, 0, 15])
        self.speedR['slow'] = fuzz.trimf(self.speedR.universe, [0, 10, 30])
        self.speedR['fast'] = fuzz.trimf(self.speedR.universe, [20, 40, 40])

        
        # Define fuzzy rules for speedL and speedR
        rule1 = ctrl.Rule(self.dist1['close'] & self.dist2['close'] & self.dist3['close'], (self.speedL['stop'], self.speedR['stop']))
        rule2 = ctrl.Rule(self.dist1['close'] & self.dist2['close'] & self.dist3['far'], (self.speedL['slow'], self.speedR['stop']))
        rule3 = ctrl.Rule(self.dist1['close'] & self.dist2['far'] & self.dist3['close'], (self.speedL['slow'], self.speedR['slow']))
        rule4 = ctrl.Rule(self.dist1['far'] & self.dist2['close'] & self.dist3['close'], (self.speedL['slow'], self.speedR['fast']))
        rule5 = ctrl.Rule(self.dist1['far'] & self.dist2['far'] & self.dist3['close'], (self.speedL['slow'], self.speedR['stop']))
        rule6 = ctrl.Rule(self.dist1['far'] & self.dist2['close'] & self.dist3['far'], (self.speedL['slow'], self.speedR['stop']))
        rule7 = ctrl.Rule(self.dist1['close'] & self.dist2['far'] & self.dist3['far'], (self.speedL['fast'], self.speedR['fast']))
        rule8 = ctrl.Rule(self.dist1['far'] & self.dist2['far'] & self.dist3['far'], (self.speedL['slow'], self.speedR['fast']))

        # Additional rules for 'ok' and 'stop'
        rule9 = ctrl.Rule(self.dist1['ok'] & self.dist2['close'] & self.dist3['close'], (self.speedL['slow'], self.speedR['slow']))
        rule10 = ctrl.Rule(self.dist1['ok'] & self.dist2['ok'] & self.dist3['far'], (self.speedL['stop'], self.speedR['slow']))
        rule11 = ctrl.Rule(self.dist1['ok'] & self.dist2['far'] & self.dist3['ok'], (self.speedL['slow'], self.speedR['stop']))
        rule12 = ctrl.Rule(self.dist1['close'] & self.dist2['ok'] & self.dist3['ok'], (self.speedL['slow'], self.speedR['stop']))
        rule13 = ctrl.Rule(self.dist1['ok'] & self.dist2['ok'] & self.dist3['ok'], (self.speedL['stop'], self.speedR['stop']))
        rule14 = ctrl.Rule(self.dist1['far'] & self.dist2['ok'] & self.dist3['ok'], (self.speedL['slow'], self.speedR['stop']))
        rule15 = ctrl.Rule(self.dist1['ok'] & self.dist2['far'] & self.dist3['far'], (self.speedL['fast'], self.speedR['fast']))
        rule16 = ctrl.Rule(self.dist1['far'] & self.dist2['far'] & self.dist3['ok'], (self.speedL['slow'], self.speedR['fast']))
        rule17 = ctrl.Rule(self.dist1['far'] & self.dist2['ok'] & self.dist3['far'], (self.speedL['slow'], self.speedR['stop']))

        self.steering_ctrl = ctrl.ControlSystem([
            rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8,
            rule9, rule10, rule11, rule12, rule13, rule14, rule15, rule16,
            rule17
        ])
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


