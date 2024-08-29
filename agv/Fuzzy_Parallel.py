import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

class FuzzyParallelLogicController:
    def __init__(self):
        self.setup_fuzzy_logic()
        self.show_plot()

    def setup_fuzzy_logic(self):
        # Define fuzzy variables
        self.diff = ctrl.Antecedent(np.arange(-200, 200, 1), 'diff')
        self.dist2 = ctrl.Antecedent(np.arange(0, 5000, 1), 'dist2')
        self.dist3 = ctrl.Antecedent(np.arange(0, 5000, 1), 'dist3')
        self.speedL = ctrl.Consequent(np.arange(-50, 100, 1), 'speedL')
        self.speedR = ctrl.Consequent(np.arange(-50, 100, 1), 'speedR')

        # Membership functions for difference
        self.diff['negative'] = fuzz.trapmf(self.diff.universe, [-200, -150, -20, -1])
        self.diff['zero'] = fuzz.trimf(self.diff.universe, [-2, 0, 2])
        self.diff['positive'] = fuzz.trapmf(self.diff.universe, [1, 20, 150, 200])

        self.dist2['close'] = fuzz.trapmf(self.dist2.universe, [0, 0, 150, 160])
        self.dist2['ok'] = fuzz.trapmf(self.dist2.universe, [150, 200, 250, 300])
        self.dist2['far'] = fuzz.trapmf(self.dist2.universe, [250, 300, 4900, 5000])

        self.dist3['close'] = fuzz.trapmf(self.dist3.universe, [0, 0, 150, 160])
        self.dist3['ok'] = fuzz.trapmf(self.dist3.universe, [150, 200, 250, 300])
        self.dist3['far'] = fuzz.trapmf(self.dist3.universe, [250, 300, 4900, 5000])

        # Membership functions for speed
        self.speedL['back'] = fuzz.trimf(self.speedL.universe, [-50, -20, 0])
        self.speedL['stop'] = fuzz.trimf(self.speedL.universe, [-5, 0, 5])
        self.speedL['slow'] = fuzz.trimf(self.speedL.universe, [0, 20, 40])
        self.speedL['fast'] = fuzz.trimf(self.speedL.universe, [30, 35, 40])

        self.speedR['back'] = fuzz.trimf(self.speedR.universe, [-50, -20, 0])
        self.speedR['stop'] = fuzz.trimf(self.speedR.universe, [-5, 0, 5])
        self.speedR['slow'] = fuzz.trimf(self.speedR.universe, [0, 20, 40])
        self.speedR['fast'] = fuzz.trimf(self.speedR.universe, [30, 35, 40])
        
        # Define combined fuzzy rules
        rules = [
            # Rules combining diff with dist2 and dist3 conditions
            ctrl.Rule(self.diff['negative'] & (self.dist2['far'] & self.dist3['far']), (self.speedL['fast'], self.speedR['slow'])),
            ctrl.Rule(self.diff['negative'] & (self.dist2['ok'] & self.dist3['far']), (self.speedL['fast'], self.speedR['slow'])),
            ctrl.Rule(self.diff['zero'] & (self.dist2['far'] & self.dist3['far']), (self.speedL['fast'], self.speedR['fast'])),
            ctrl.Rule(self.diff['positive'] & (self.dist2['far'] & self.dist3['far']), (self.speedL['slow'], self.speedR['fast'])),

            # Rules to stop the vehicle if dist2 or dist3 is close or ok
            ctrl.Rule((self.dist2['close'] | self.dist3['close']) | (self.dist2['ok'] | self.dist3['ok']), (self.speedL['stop'], self.speedR['stop']))
        ]

        # Initialize the control system with the list of rules
        self.steering_ctrl = ctrl.ControlSystem(rules)
        self.steering = ctrl.ControlSystemSimulation(self.steering_ctrl)

    def compute_action(self, diff, dist2, dist3):
        self.steering.input['diff'] = diff
        self.steering.input['dist2'] = dist2
        self.steering.input['dist3'] = dist3
        self.steering.compute()

        return self.steering.output['speedL'], self.steering.output['speedR']
    
    def show_plot(self):
        # Visualize these universes and membership functions
        fig, (ax1) = plt.subplots(nrows=1, figsize=(8, 4))

        ax1.plot(self.diff.universe, self.diff['negative'].mf, 'b', linewidth=1, label='Negative')
        ax1.plot(self.diff.universe, self.diff['zero'].mf, 'g', linewidth=1, label='Zero')
        ax1.plot(self.diff.universe, self.diff['positive'].mf, 'r', linewidth=1, label='Positive')
        ax1.set_title('Parallel difference')
        ax1.legend()

        # ax2.plot(self.speedR.universe, self.speedR['back'].mf, 'b', linewidth=1.5, label='Back')
        # ax2.plot(self.speedR.universe, self.speedR['stop'].mf, 'g', linewidth=1.5, label='Stop')
        # ax2.plot(self.speedR.universe, self.speedR['slow'].mf, 'r', linewidth=1.5, label='Slow')
        # ax2.plot(self.speedR.universe, self.speedR['fast'].mf, 'orange', linewidth=1.5, label='Fast')
        # ax2.set_title('SpeedR')
        # ax2.legend()

        # Turn off top/right axes
        # for ax in (ax1, ax2):
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.get_xaxis().tick_bottom()
        ax1.get_yaxis().tick_left()

        plt.tight_layout()
        plt.show()  # Display the plot

# Example usage:
# controller = FuzzyParallelLogicController()
# speedL, speedR = controller.compute_action(diff=0, dist2=40, dist3=40)
# print(f"speedL: {speedL}, speedR: {speedR}")


if __name__ == "__main__":
    fuzzy = FuzzyParallelLogicController()
