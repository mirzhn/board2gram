import random
import json

class Game:
    def __init__(self, deck, captain_id, code, game_type_name, players=None, round=0):
        self.deck = deck
        self.used_deck = []
        self.code = code
        self.game_type_name = game_type_name
        self.players = players if players is not None else []
        self.round = round
        self.round_info = []
        self.join(captain_id, True)

    def join(self, user_id, is_captain=False):
        self.players.append({'user_id': user_id, 'role': 'player', 'is_captain': is_captain})

    def play(self):
        self.round += 1
        messages = []
        chameleon = self.assign_roles()
        card = self.get_next_card()
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

    def get_next_card(self):
        self.deck = [card for card in self.deck if card not in self.used_deck]
        if not self.deck:
            raise Exception("No unused cards available")
        selected_card =  random.choice(self.deck)
        self.used_deck.append(selected_card)
        return selected_card
