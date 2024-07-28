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
        card_topic = json.loads(card['value'])["topic"]
        selected_word = random.choice(card_words)

        self.round_info.append({'round_id': self.round, 'key': 'chameleon', 'value': chameleon['user_id']})
        self.round_info.append({'round_id': self.round, 'key': 'card', 'value': card['id']})
        self.round_info.append({'round_id': self.round, 'key': 'selected_word', 'value': selected_word})
   
        message =  f"\nРаунд {self.round}. \n<b>Тема: {card_topic}</b> \nСлова темы: {self.get_format_table(card_words)}"
        for player in self.players:
            if player['role'] == 'chameleon':
                messages.append((player['user_id'], message + "\n<b>Вы заяц :)</b>"))
            else:
                messages.append((player['user_id'], message + f"\n<b>Секретное слово: {selected_word}</b>"))
        return messages
    
    def assign_roles(self):
        for player in self.players:
            player['role'] = 'player'
        chameleon = random.choice(self.players)
        chameleon['role'] = 'chameleon'
        return chameleon
    
    def get_format_table(self, words: list) -> str:
        table_rows = []
        table_html = "<pre>\n"

        # Определим фиксированную ширину столбцов
        column_width = 20

        # Создание строк для таблицы 2x8
        for i in range(0, len(words), 2):
            row = words[i:i + 2]
            table_rows.append(row)

        for row in table_rows:
            table_html += "| " + " | ".join(f"{word:<{column_width}}" for word in row) + " |\n"

        table_html += "</pre>"
        return table_html
    
    def get_rules(self):
        return f"""
Игра ЗАЯЦ состоит из раундов. 
Кнопка старта следующего раунда доступна капитану.
В каждом раунде игроку назначается роль - игрок или заяц. 
Игроки получают карточку с темами и секретное слово. 
Заяц получает только карточку с темами.
Каждый игрок по очереди называет свою ассоциацию на секретное слово, стараясь не подсказать зайцу.
Заяц придумывает ассоциацию стараясь не выдать себя. 
Коллективным голосованием игроки угадывают заяца. 
Заяц выигрывает раунд если его не угадали.
В конце раунда капитан стартует новый раунд или завершает игру
"""
