from jeu import RiskGame, Plot, Player, GameAgent, MinimaxAgent, RandomAgent

# Créer les joueurs


# Créer le jeu avec les deux joueurs

# Créer des agents pour chaque joueur
agentMax = MinimaxAgent(game, joueurMax)
agentMin = RandomAgent(game, joueurMin)

joueurMax = Player("rouge", "#ff0000")
joueurMin = Player("bleu", "#0091ff")
game = RiskGame([joueurMax, joueurMin])

plotter = Plot(game)
a = plotter.representation_territoires_controles()

# Démarrer le jeu


'''
# Exemple d'utilisation des agents pour jouer des tours
while not game.check_victory():
    current_player = game.players[game.current_player_index]
    if current_player == joueurMax:
        agentMax.make_move()
    else:
        agentMin.make_move()
    
    game.next_turn()
'''