# game/chameleon_game.py
import random
import json
from .base_game import Game

class ChameleonGame(Game):
    def play(self):
        self.round += 1
        messages = []
        chameleon = self.assign_roles()
        card = self.get_random_card()
        card_words = json.loads(card['value'])["words"]
        selected_word = random.choice(card_words)

        self.round_info.append({'round_id': self.round, 'key': 'chameleon', 'value': chameleon['user_id']})
        self.round_info.append({'round_id': self.round, 'key': 'card', 'value': card['id']})
        self.round_info.append({'round_id': self.round, 'key': 'selected_word', 'value': selected_word})

        for player in self.players:
            if player['role'] == 'chameleon':
                messages.append((player['user_id'], f"Раунд {self.round}. Вы хамелеон. Ваши темы: {', '.join(card_words)}"))
            else:
                messages.append((player['user_id'], f"Раунд {self.round}. Вы игрок. Ваши темы: {', '.join(card_words)}. Слово: {selected_word}"))
        return messages
    
    def assign_roles(self):
        for player in self.players:
            player['role'] = 'player'
        chameleon = random.choice(self.players)
        chameleon['role'] = 'chameleon'
        return chameleon
    
    
