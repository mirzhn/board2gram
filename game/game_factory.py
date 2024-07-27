class GameFactory:
    def __init__(self):
        self._creators = {}

    def register_game(self, game_name, creator):
        self._creators[game_name] = creator

    def get_game(self, game_name, *args, **kwargs):
        creator = self._creators.get(game_name)
        if not creator:
            raise ValueError(f"Game '{game_name}' is not registered.")
        return creator(*args, **kwargs)