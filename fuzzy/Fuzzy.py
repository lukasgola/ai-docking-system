import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class FuzzyLogicController:
    def __init__(self):
        self.setup_fuzzy_logic()

    def setup_fuzzy_logic(self):
        # Define fuzzy variables
        self.dist1 = ctrl.Antecedent(np.arange(0, 800, 1), 'dist1')
        self.dist2 = ctrl.Antecedent(np.arange(0, 800, 1), 'dist2')
        self.dist3 = ctrl.Antecedent(np.arange(0, 800, 1), 'dist3')
        self.angle = ctrl.Consequent(np.arange(-45, 46, 1), 'angle')
        self.speed = ctrl.Consequent(np.arange(0, 6, 1), 'speed')

        # Membership functions for distances
        self.dist1['close'] = fuzz.trimf(self.dist1.universe, [0, 0, 50])
        self.dist1['far'] = fuzz.trimf(self.dist1.universe, [25, 800, 800])
        
        self.dist2['close'] = fuzz.trimf(self.dist2.universe, [0, 0, 50])
        self.dist2['far'] = fuzz.trimf(self.dist2.universe, [25, 800, 800])
        
        self.dist3['close'] = fuzz.trimf(self.dist3.universe, [0, 0, 50])
        self.dist3['far'] = fuzz.trimf(self.dist3.universe, [25, 800, 800])

        # Membership functions for angle
        self.angle['left'] = fuzz.trimf(self.angle.universe, [-60, -60, 0])
        self.angle['straight'] = fuzz.trimf(self.angle.universe, [-10, 0, 10])
        self.angle['right'] = fuzz.trimf(self.angle.universe, [0, 60, 60])

        # Membership functions for speed
        self.speed['slow'] = fuzz.trimf(self.speed.universe, [0, 0, 3])
        self.speed['fast'] = fuzz.trimf(self.speed.universe, [3, 5, 5])

        # Define fuzzy rules
        rule1 = ctrl.Rule(self.dist1['close'] & self.dist2['close'] & self.dist3['close'], (self.angle['straight'], self.speed['slow']))
        rule2 = ctrl.Rule(self.dist1['close'] & self.dist2['close'] & self.dist3['far'], (self.angle['right'], self.speed['slow']))
        rule3 = ctrl.Rule(self.dist1['close'] & self.dist2['far'] & self.dist3['close'], (self.angle['left'], self.speed['slow']))
        rule4 = ctrl.Rule(self.dist1['far'] & self.dist2['close'] & self.dist3['close'], (self.angle['straight'], self.speed['fast']))
        rule5 = ctrl.Rule(self.dist1['far'] & self.dist2['far'] & self.dist3['close'], (self.angle['right'], self.speed['fast']))
        rule6 = ctrl.Rule(self.dist1['far'] & self.dist2['close'] & self.dist3['far'], (self.angle['left'], self.speed['fast']))
        rule7 = ctrl.Rule(self.dist1['close'] & self.dist2['far'] & self.dist3['far'], (self.angle['straight'], self.speed['fast']))
        rule8 = ctrl.Rule(self.dist1['far'] & self.dist2['far'] & self.dist3['far'], (self.angle['left'], self.speed['fast']))

        self.steering_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8])
        self.steering = ctrl.ControlSystemSimulation(self.steering_ctrl)

    def compute_action(self, d1, d2, d3):
        self.steering.input['dist1'] = d1
        self.steering.input['dist2'] = d2
        self.steering.input['dist3'] = d3
        self.steering.compute()

        return self.steering.output['angle'], self.steering.output['speed']
