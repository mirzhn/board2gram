from sqlalchemy.orm import Session
from .game_service import GameService
import random
import json

class Game:
    def __init__(self, db: Session, game_type_name: str):
        self.db = db
        self.game_service = GameService(db)
        self.game_type_name = game_type_name
        self.game_state = None
        self.game_cards = []
        self.players = []
        self.round = 0

    def create(self):
        self.game_state = self.game_service.create_game(self.game_type_name)
        self.game_cards = self.game_service.get_game_type_cards(self.game_type_name)
        return self.game_state.code

    def join(self, user_id: int, is_captain: bool):
        self.game_service.join_game(user_id, is_captain, self.game_state.id)

    def play(self):
        # Получаем текущих игроков
        self.players = self.game_service.get_players_in_game(self.game_state.id)
        # Создаем новый раунд
        messages = self.start_new_round()
        return messages

    def assign_roles(self):
        for player in self.players:
            player.role = 'player'  # Сбрасываем текущие роли
        chameleon = random.choice(self.players)
        chameleon.role = 'chameleon'
        return chameleon

    def select_random_unused_card(self):
        used_card_ids = self.game_service.get_used_card_ids(self.game_state.id)
        unused_cards = [card for card in self.game_cards if card.id not in used_card_ids]
        if not unused_cards:
            raise Exception("No unused cards available")
        selected_card = random.choice(unused_cards)
        return selected_card

    def start_new_round(self):
        self.round += 1
        new_round = self.game_service.start_round(self.game_state.id, self.round)
        
        # Распределяем роли
        chameleon = self.assign_roles()
        
        # Выбираем случайную несыгранную карточку
        selected_card = self.select_random_unused_card()

        # Сохраняем информацию о хамелеоне и выбранной карточке в round_info
        self.game_service.add_round_info(new_round.id, 'chameleon', str(chameleon.user_id))
        self.game_service.add_round_info(new_round.id, 'used_card', str(selected_card.id))

        # Формируем сообщения для игроков на новый раунд
        messages = self.form_round_messages(selected_card)
        return messages

    def form_round_messages(self, selected_card):
        messages = []
        card_words = json.loads(selected_card.value)["words"]
        selected_word = random.choice(card_words)
        for player in self.players:
            if player.role == 'chameleon':
                messages.append((player.user_id, f"Раунд {self.round}. Вы хамелеон. Ваши темы: {', '.join(card_words)}"))
            else:
                messages.append((player.user_id, f"Раунд {self.round}. Вы игрок. Ваши темы: {', '.join(card_words)}. Слово: {selected_word}"))
        return messages

    def stop(self):
        self.game_service.stop_game(self.game_state.id)