from .base_game import Game

class BumkerGame(Game):
    def play(self):
        self.round += 1
        messages = []
    
        if self.round == 1:
            reason_card = self.get_random_card('reason')
            messages.append((self.captain_id, '<b>Причина конца света: </b>' + reason_card['value']))
            for player in self.players:
                messages.append((player['user_id'], self.get_player_info()))
        else:
            bunker_card = self.get_random_card('bunker')
            messages.append((self.captain_id, '<b>Факт о бункере: </b>' +  bunker_card['value'])) 
            self.round_info.append({'round_id': self.round, 'key': 'bunker', 'value': bunker_card['id']})

        return messages
    

    def get_player_info(self):
        player_info = f"""
<b>хобби</b>: {self.get_random_card('hobby')['value']}
<b>здоровье</b>: {self.get_random_card('health')['value']}
<b>биология</b>: {self.get_random_card('biology')['value']}
<b>багаж</b>: {self.get_random_card('baggage')['value']}
<b>факт</b>: {self.get_random_card('fact')['value']}
<b>профессия</b>: {self.get_random_card('career')['value']}
"""
        return player_info
    
    def get_rules(self):
        return f"""
Игра БУНКЕР. 
Целью игры является определить кто из игроков попадёт в бункер и спасётся от конца света.
В первом раунде капитан получает и рассказывает игрокам информацию о том, какой конец света ожидает мир.
Так же в первом раунде каждый игрок получает набор из 6 характеристик.
В начале каждого раунда капитан получает карточку с дополнительной информацией о бункере.
В каждом раунде каждый игрок должен раскрыть одну из своих характеристик на свой выбор.
В конце раунда голосованием игроков определяется один человек, которого не берут в бункер. 
Игра заканчивается когда определено нужное количество игроков для бункера.
"""
