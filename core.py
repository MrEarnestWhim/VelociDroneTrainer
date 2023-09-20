import json

import pyautogui
from time import sleep

from pynput.keyboard import Controller

keyboard: Controller = Controller()


class Trainer:
    color_damage: tuple[int, int]
    color_crush: tuple[int, int]
    image_patch: str
    restart_key: str = "a"
    pixel_map = None
    pos_damage: tuple[int, int] = None
    pos_crush: tuple[int, int] = None
    __counter: int = 0
    __screen_size: tuple
    is_damage: bool = True
    is_crush: bool = True

    __percent_w_damage = 2.421875
    __percent_h_damage = 7.638889

    __percent_w_damage_h = 8.359375

    __percent_w_crush = 47.65625
    __percent_h_crush = 16.94444

    __interface = 12.65625
    interface_is_big = False

    def __init__(
            self,
            is_damage: bool = True,
            is_crush: bool = True,
            color_damage: tuple[int, int] = (231, 22, 22),
            color_crush: tuple[int, int] = (223, 53, 53),
            restart_key: str = "a",
    ):
        self.is_damage = is_damage
        self.is_crush = is_crush
        self.color_damage = color_damage
        self.color_crush = color_crush
        self.restart_key = restart_key

    def start(self):
        self._config_load()

        # interface_is_big = self.scanner("interface")

        if not self.pos_damage:
            self.pos_damage = self.scanner("damage")

        if not self.pos_crush:
            self.pos_crush = self.scanner("crush")

        try:
            print("Program start")
            while 1:
                self._screenshot()
                if self.is_damage:
                    self.checker(self.color_damage, self.pos_damage)

                if self.is_crush:
                    self.checker(self.color_crush, self.pos_crush)

        except KeyboardInterrupt:
            self._config_create()
            print("Program stop")
            print("I'm save a clicks:", self.get_counter())

    def get_counter(self) -> int:
        return self.__counter

    def set_counter(self, count) -> None:
        self.__counter = count

    def add_counter(self) -> None:
        self.__counter += 2

    def _config_load(self):
        try:
            with open("config.json", "r") as f:
                data = f.read()
        except FileNotFoundError:
            print("Don't config.")
            return

        if data:
            config = json.loads(data)
            self.pos_damage = config.get("pos_damage", None)
            self.pos_crush = config.get("pos_crush", None)
            self.set_counter(config.get("counter", 0))

        print("Config is load!")

    def _config_create(self):
        config = dict(
            pos_damage=self.pos_damage,
            pos_crush=self.pos_crush,
            counter=self.get_counter(),
        )
        with open("config.json", "w") as f:
            f.write(json.dumps(config))

    def _restart(self) -> None:
        keyboard.press(self.restart_key)
        keyboard.release(self.restart_key)
        sleep(0.5)
        keyboard.press(self.restart_key)
        keyboard.release(self.restart_key)
        self.add_counter()
        sleep(2)

    def scanner(self, _type: str) -> tuple[int, int]:
        print("Scanner is start!")
        while 1:
            self._screenshot()
            w, h = self._sh.size
            if _type == "crush":
                temp_pos_crash = (round(w / 100 * self.__percent_w_crush), round(h / 100 * self.__percent_h_crush))
                if self.checker(self.color_crush, self.pos_crush, temp_pos_crash):
                    print("Crush pixel is find!")
                    return temp_pos_crash

            if _type == "damage":
                temp_pos_damage = (round(w / 100 * self.__percent_w_damage), round(h / 100 * self.__percent_h_damage))
                if self.checker(self.color_damage, self.pos_damage, temp_pos_damage):
                    print("Damage pixel is find!")
                    return temp_pos_damage

                temp_pos_damage = (round(h / 100 * self.__percent_h_damage), round(w / 100 * self.__percent_w_damage_h))
                if self.checker(self.color_damage, self.pos_damage, temp_pos_damage):
                    print("Damage pixel 'H' is find!")
                    return temp_pos_damage

    def checker(
            self,
            color: tuple[int, int],
            pos: tuple[int, int],
            temp: tuple[int, int] = None
    ) -> bool:
        _pos = temp or pos

        if self.pixel_map[_pos[0], _pos[1]] == color:
            self._restart()
            return True
        return False

    def _screenshot(self, is_save: bool = False) -> None:
        self._sh = pyautogui.screenshot()
        self.pixel_map = self._sh.load()
        if is_save:
            self._sh.save("images/temp_file.png")
