import argparse
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum

class HiddenMarkovChain:

    class RPS(Enum):
        ROCK = 0
        PAPER = 1
        SCISSORS = 2
    
    lose_round_rules = {
        RPS.SCISSORS: RPS.ROCK,
        RPS.ROCK: RPS.PAPER,
        RPS.PAPER: RPS.SCISSORS
    }
    
    def __init__(self, target_score):
        self.target_score = target_score
    
    def start_new_game(self):
        self.match_count = 0
        self.current_score = 0
        self.initial_matrix = self.init_markov_model()
        self.round_results = [['[Round]', '[User-Computer]', '[Total Score]']]
        self.play_game()

    def init_markov_model(self):
        markov_model = self.read_markov_model()
        if not markov_model:
            return {
                self.RPS.ROCK.name: [1,1,1],
                self.RPS.SCISSORS.name: [1,1,1],
                self.RPS.PAPER.name: [1,1,1]
            }
        return markov_model

    def play_game(self):
        previous_user_input = None
        while  -self.target_score < self.current_score < self.target_score:
            previous_user_input = self.play_round(previous_user_input)
        final_result_message = f'\n[Your Score / Your Target]: {self.current_score}/{self.target_score}\nYou ' + ('Win' if self.target_score == self.current_score else 'Lose')
        print(final_result_message)
        self.save_results_into_file(self.round_results, final_result_message)
        self.save_markov_model(self.initial_matrix)

    def play_round(self, previous_user_input):
        self.match_count += 1
        computer_input = self.handle_computer_input(previous_user_input)
        user_input = self.handle_player_input()

        self.current_score += self.check_round_results(user_input, computer_input)
        self.learn(previous_user_input, user_input)

        self.round_results.append( [f'{self.match_count}', f"{user_input.name}-{computer_input.name}", f'{self.current_score}'])
        print(f"[You/Comp]: [{user_input.name}-{computer_input.name}]\n[Score]: {self.current_score}")
        
        previous_user_input = user_input
        return previous_user_input

    def predict_next_user_input(self, user_input):
        pred_sum = sum(self.initial_matrix[user_input.name])
        probability = [el / pred_sum for el in self.initial_matrix[user_input.name]]
        return np.random.choice(list(self.RPS), replace = True, p = probability)

    def learn(self, previous_user_input, user_input):
        if previous_user_input is None: return
        self.initial_matrix.get(previous_user_input.name)[user_input.value] += 1
    
    def check_round_results(self, user_input, computer_input):
        if self.lose_round_rules.get(user_input) == computer_input: return -1
        if user_input == computer_input: return 0
        return 1
    
    def save_markov_model(self, matrix):
        with open('s20880_markov_model.json', 'w', encoding='utf-8') as outfile:
            json.dump(matrix, outfile, ensure_ascii=False, indent=4)

    def read_markov_model(self):
        markov_model = {}
        path = 's20880_markov_model.json'
        if not os.path.exists(path): return None
        with open(path) as inputfile:
            data = json.load(inputfile)
        for option in self.RPS:
            markov_model[option.name] = data[option.name]
        return markov_model

    def handle_player_input(self):
        user_input = input(f'{self.match_count}) Your turn [Rock,Paper,Scissors]: ').upper()
        while user_input not in self.RPS._member_names_:
            print("Please, enter a valid value: 'Rock' / 'Paper' / 'Scissors'")
            user_input = input('Enter your choice: ').upper()
        return self.RPS[user_input]

    def handle_computer_input(self, user_input):
        if self.match_count < 1 or user_input is None:
            return np.random.choice(list(self.RPS))
        prediction = self.predict_next_user_input(user_input)
        computer_input = self.lose_round_rules[prediction]
        return computer_input

    def save_results_into_file(self, content, final_result):
        str_result = ''
        for row in content:
            str_result += "{: >7} {: >20} {: >15}".format(*row) + '\n'
        str_result += final_result
        file = open('s20880_markov_result.txt', 'w')
        file.write(str_result)
        file.close()

def check_positive_integer_input(input_value):
    try:
        int_value = int(input_value)
    except ValueError:
        raise argparse.ArgumentTypeError('Must be an integer number')
    if int_value <= 0:
        raise argparse.ArgumentTypeError(f"Must be a positive integer number")
    return int_value

def parse_arguments():
    parser = argparse.ArgumentParser(description='Enter an integer value of target game score')
    parser.add_argument('target_score', type=check_positive_integer_input, help='An integer value of target game score')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    hiddenMarkovChain = HiddenMarkovChain(args.target_score)
    hiddenMarkovChain.start_new_game()