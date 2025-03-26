from feast_and_forage_env import config


class Player:
    def __init__(self, player_id, x, y, agent, conf_dict=None):
        self.player_id = player_id
        self.x = x
        self.y = y
        self.agent = agent()

        self.stats = PlayerStats(conf_dict)
        self.health = self.stats.max_health
        self.water = self.stats.max_water
        self.food = self.stats.max_food
        self.collected_food = 0
        self.collected_water = 0

    def __str__(self):
        return (f"Player {self.player_id} ({self.y}, {self.x}): Collected: {self.collected_food}, "
                f"Health: {self.health}, Food: {self.food}, Water: {self.water}")

    def move(self, level):
        return self.agent(level, self.x, self.y)


class PlayerStats:
    def __init__(self, conf_dict=None):
        self.max_health = config.MAX_HEALTH
        self.max_food = config.MAX_FOOD
        self.max_water = config.MAX_WATER
        self.health_drop = config.HEALTH_DROP
        self.food_drop = config.FOOD_DROP
        self.water_drop = config.WATER_DROP
        self.health_regain = config.HEALTH_REGAIN
        self.food_regain = config.FOOD_REGAIN
        self.water_regain = config.WATER_REGAIN
        self.collect_num_food = config.COLLECT_NUM_FOOD
        if conf_dict is not None:
            self.set_conf(conf_dict)

    def set_conf(self, conf_dict):
        self.max_health = conf_dict["max_health"]
        self.max_food = conf_dict["max_food"]
        self.max_water = conf_dict["max_water"]
        self.health_drop = conf_dict["health_drop"]
        self.food_drop = conf_dict["food_drop"]
        self.water_drop = conf_dict["water_drop"]
        self.health_regain = conf_dict["health_regain"]
        self.food_regain = conf_dict["food_regain"]
        self.water_regain = conf_dict["water_regain"]
        self.collect_num_food = conf_dict["collect_num_food"]

    def get_conf_dict(self):
        return {"max_health": self.max_health, "max_food": self.max_food, "max_water": self.max_water,
                "health_drop": self.health_drop, "food_drop": self.health_drop, "water_drop": self.water_drop,
                "health_regain": self.health_regain, "food_regain": self.food_regain, "water_regain": self.water_regain,
                "collect_num_food": self.collect_num_food}
