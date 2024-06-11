import random
from config import character_sets

class PasswordGenerator:
    def generate_password(self, length, complexity):
        if complexity == "Low":
            character_set = character_sets[0]
        elif complexity == "Medium":
            character_set = character_sets[0] + character_sets[1]
        else:  # High complexity
            character_set = "".join(character_sets)

        password = "".join(random.choice(character_set) for _ in range(length))
        return password