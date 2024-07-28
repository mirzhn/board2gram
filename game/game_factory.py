class GameFactory:
    def __init__(self):
        self._creators = {}
        self._aliases = {}

    def register_game(self, game_name, creator, alias):
        self._creators[game_name] = creator
        self._aliases[game_name] = alias

    def get_game(self, game_name, *args, **kwargs):
        creator = self._creators.get(game_name)
        if not creator:
            raise ValueError(f"Game '{game_name}' is not registered.")
        return creator(*args, **kwargs)

    def get_available_game_types(self):
        return self._aliases