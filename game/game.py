class Game:
    def __init__(self, deck, captain_id, code, game_type_name, players=None, round=0):
        self.deck = deck
        self.captain_id = captain_id
        self.code = code
        self.game_type_name = game_type_name
        self.players = players if players is not None else []
        self.round = round

    def join(self, user_id):
        self.players.append({'user_id': user_id, 'role': 'player'})

    def play(self):
        self.round += 1
        messages = []
        chameleon = self.assign_roles()
        card = self.select_random_card()
        for player in self.players:
            messages.append((player['user_id'], f"Round {self.round} started. Chameleon assigned."))
        return messages

    def assign_roles(self):
        import random
        for player in self.players:
            player['role'] = 'player'
        chameleon = random.choice(self.players)
        chameleon['role'] = 'chameleon'
        return chameleon

    def select_random_card(self):
        import random
        return random.choice(self.deck)
