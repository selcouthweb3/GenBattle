# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import re
from genlayer import *


class GenBattle(gl.Contract):
    player1: str
    player2: str
    player1_health: u256
    player2_health: u256
    current_turn: str
    winner: str
    battle_log: DynArray[str]

    def __init__(self, player1: str, player2: str):
        self.player1 = player1
        self.player2 = player2
        self.player1_health = u256(100)
        self.player2_health = u256(100)
        self.current_turn = player1
        self.winner = ""

    @gl.public.view
    def get_battle_status(self) -> str:
        if self.winner != "":
            return f"Battle Over! Winner: {self.winner}"
        return (
            f"{self.player1} HP: {self.player1_health} | "
            f"{self.player2} HP: {self.player2_health} | "
            f"Current Turn: {self.current_turn}"
        )

    @gl.public.view
    def get_battle_log(self) -> str:
        return " | ".join(self.battle_log)

    @gl.public.write
    def attack(self, attacker: str, move: str):
        assert self.winner == "", "Battle is already over"
        assert attacker == self.current_turn, "It's not your turn"

        def compute_damage() -> int:
            response = gl.nondet.exec_prompt(
                f"A fighter named {attacker} uses the move '{move}' in a battle. "
                f"Based on the move's name and creativity, decide how much damage it deals. "
                f"Reply with only a single integer between 5 and 30. No words, no punctuation, no explanation."
            )
            match = re.search(r"\d+", response)
            if match is None:
                return 15
            value = int(match.group())
            if value < 5:
                return 5
            if value > 30:
                return 30
            return value

        raw_damage = gl.eq_principle.prompt_comparative(
            compute_damage,
            principle=(
                "Both answers must be integers between 5 and 30. "
                "They are equivalent if their absolute difference is 5 or less."
            ),
        )

        damage = u256(raw_damage)

        if attacker == self.player1:
            if damage >= self.player2_health:
                self.player2_health = u256(0)
                self.winner = self.player1
            else:
                self.player2_health = self.player2_health - damage
            self.current_turn = self.player2
        else:
            if damage >= self.player1_health:
                self.player1_health = u256(0)
                self.winner = self.player2
            else:
                self.player1_health = self.player1_health - damage
            self.current_turn = self.player1

        log_entry = f"{attacker} used '{move}' and dealt {damage} damage"
        self.battle_log.append(log_entry)

    @gl.public.write
    def reset_battle(self, player1: str, player2: str):
        self.player1 = player1
        self.player2 = player2
        self.player1_health = u256(100)
        self.player2_health = u256(100)
        self.current_turn = player1
        self.winner = ""
        while len(self.battle_log) > 0:
            self.battle_log.pop()
