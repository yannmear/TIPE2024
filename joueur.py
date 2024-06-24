from plateau import Board
import math
import copy
import random

class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.territories = []
    
    def territories_id(self):
        return [self.territories[k].ID for k in range(len(self.territories))] 

    def add_territory(self, territory):
        self.territories.append(territory)
        territory.owner = self

    def remove_territory(self, territory):
        self.territories = [t for t in self.territories if t != territory]

    def reinforce(self, territory, armies):
        if territory in self.territories:
            territory.place_armies(armies, self)
        else:
            raise ValueError("Player does not own this territory")


class GameAgent(Player):
    def possible_attacks(self):
        '''Renvoie les attaques possibles pour l'agent de jeu à un état donné du jeu sous la forme d'une liste de couples '''
        actions = []
        current_player = self.player
        for territory in current_player.territories:
            if territory.armies > 1:  # Il faut au moins 2 armées pour attaquer
                for neighbor_id in territory.neighbors_ID:
                    neighbor = self.game.board.get_territory_with_id(neighbor_id)
                    if neighbor.owner != current_player:
                        actions.append((territory.ID, neighbor.ID))
        return actions

    def continent_control_bonus(self):
        bonus = 0
        player = self.player
        for continent in self.game.board.continents:
            if all(territory.owner == player for territory in continent.territories):
                bonus += continent.bonus_armies
        return bonus

    def calculate_armies_next_turn(self):
        # Calculer le nombre d'armées que le joueur obtiendra au prochain tour
        base_armies = max(3, len(player.territories) // 3)
        continent_bonus = self.continent_control_bonus(player)
        return base_armies + continent_bonus





class RandomAgent(GameAgent):
    def make_random_attack(self):
        # Exemple d'une attaque aléatoire
        possible_attacks = possible_attacks(game)
        
        attack = random.choice(possible_attacks)
        attacking_territory = self.game.board.get_territory_with_id(attack[0])
        target_territory = self.game.board.get_territory_with_id(attack[1])

        attacking_armies = attacking_territory.armies - 1
        self.game.stochastic_attack(attacking_territory.ID, target_territory.ID, attacking_armies)




class MinimaxAgent(GameAgent):
    def minimax(self, state, depth, maximizing_player):
        if depth == 0 or self.game.check_victory():
            return self.evaluate(state, self.player if maximizing_player else self.game.players[(self.game.players.index(self.player) + 1) % 2])
        
        if maximizing_player:
            max_eval = -math.inf
            best_action = None
            for action in self.possible_actions(state):
                new_state = self.result(state, action)
                eval = self.minimax(new_state, depth - 1, False)
                if eval > max_eval:
                    max_eval = eval
                    best_action = action
            return best_action if depth == 3 else max_eval
        else:
            min_eval = math.inf
            best_action = None
            for action in self.possible_actions(state):
                new_state = self.result(state, action)
                eval = self.minimax(new_state, depth - 1, True)
                if eval < min_eval:
                    min_eval = eval
                    best_action = action
            return best_action if depth == 3 else min_eval

    def result(self, state, action):
        new_state = copy.deepcopy(state)
        attacking_territory_id, target_territory_id = action
        attacking_territory = new_state.board.get_territory_with_id(attacking_territory_id)
        target_territory = new_state.board.get_territory_with_id(target_territory_id)

        # Logique simple pour appliquer l'action : attaque déterministe
        attacking_armies = attacking_territory.armies - 1
        new_state.deterministic_attack(attacking_territory_id, target_territory_id, attacking_armies)

        return new_state

    def min_max_attack(self):
        best_move = self.minimax(self.game, depth=3, maximizing_player=True)

        attacking_territory, target_territory = best_move
        attacking_territory_obj = self.game.board.get_territory_with_id(attacking_territory)

        attacking_armies = attacking_territory_obj.armies - 1
        
        self.game.deterministic_attack(attacking_territory, target_territory, attacking_armies)
