# { "Depends": "py-genlayer:test" }

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
        self.battle_log = DynArray[str]()

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

        result = gl.exec_prompt(
            f"A fighter named {attacker} uses the move '{move}' in a battle. "
            f"Based on the move name and creativity, calculate a damage value between 5 and 30. "
            f"Respond with only a number between 5 and 30."
        )

        damage = u256(int(result.strip()))

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
        self.battle_log = DynArray[str]()


pwd


