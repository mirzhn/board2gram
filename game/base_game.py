import random
import json

class Game:
    def __init__(self, deck, user, code, game_type, players=None, round=0):
        self.deck = deck
        self.used_deck = []
        self.code = code
        self.game_type = game_type
        self.players = players if players is not None else []
        self.round = round
        self.round_info = []
        self.join(user, True)
        self.captain_id = user['chat_id']
        self.rules=''

    def join(self, user, is_captain=False):
        self.players.append({'user_id': user['chat_id'], 'name': user['name'], 'role': 'player', 'is_captain': is_captain})

    def leave(self, user):
        self.players = [player for player in self.players if player['user_id'] != user['chat_id']]

    def play(self):
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_random_card(self):
        self.deck = [card for card in self.deck if card not in self.used_deck]
        if not self.deck:
            raise Exception("No unused cards available")
        selected_card =  random.choice(self.deck)
        self.used_deck.append(selected_card)
        return selected_card
    
    def get_rules(self):
        return self.rules

    
