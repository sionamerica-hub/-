"""
Test script for Babel: The Word Alchemist
Tests the specific scenarios mentioned in the requirements
"""

from babel_rpg import WordDatabase, SpellBuilder, Player, Enemy, cast_spell

def test_scenario_1():
    """Test Case 1: Fast + Fire + Ball -> Deals Fire damage with high priority speed"""
    print("=" * 60)
    print("Test Case 1: Fast + Fire + Ball")
    print("=" * 60)
    
    word_db = WordDatabase()
    spell_builder = SpellBuilder(word_db)
    player = Player()
    enemy = Enemy("Test Enemy", 100, 50)
    
    spell = spell_builder.build_spell("Fast", "Fire", "Ball")
    print(f"Spell Description: {spell['description']}")
    print(f"Damage: {spell['damage']}")
    print(f"Mana Cost: {spell['mana_cost']}")
    print(f"Target Type: {spell['target_type']}")
    print(f"Special Effects: {spell['special_effects']}")
    print()
    
    result = cast_spell(spell_builder, "Fast", "Fire", "Ball", player, [enemy])
    print(result)
    print()
    print(f"Enemy HP after spell: {enemy.hp}")
    print(f"Player Mana after spell: {player.mana}")
    print()


def test_scenario_2():
    """Test Case 2: Vampiric + Sword + Rain -> Deals Physical damage to all enemies and heals the player"""
    print("=" * 60)
    print("Test Case 2: Vampiric + Sword + Rain")
    print("=" * 60)
    
    word_db = WordDatabase()
    spell_builder = SpellBuilder(word_db)
    player = Player()
    enemy1 = Enemy("Enemy 1", 100, 50)
    enemy2 = Enemy("Enemy 2", 100, 50)
    
    spell = spell_builder.build_spell("Vampiric", "Sword", "Rain")
    print(f"Spell Description: {spell['description']}")
    print(f"Damage: {spell['damage']}")
    print(f"Mana Cost: {spell['mana_cost']}")
    print(f"Target Type: {spell['target_type']}")
    print(f"Special Effects: {spell['special_effects']}")
    print()
    
    initial_hp = player.hp
    result = cast_spell(spell_builder, "Vampiric", "Sword", "Rain", player, [enemy1, enemy2])
    print(result)
    print()
    print(f"Enemy 1 HP: {enemy1.hp}, Enemy 2 HP: {enemy2.hp}")
    print(f"Player HP: {player.hp} (was {initial_hp}, healed {player.hp - initial_hp})")
    print()


def test_scenario_3():
    """Test Case 3: Heavy + Water + Wall -> Creates a high-defense barrier"""
    print("=" * 60)
    print("Test Case 3: Heavy + Water + Wall")
    print("=" * 60)
    
    word_db = WordDatabase()
    spell_builder = SpellBuilder(word_db)
    player = Player()
    enemy = Enemy("Test Enemy", 100, 50)
    
    spell = spell_builder.build_spell("Heavy", "Water", "Wall")
    print(f"Spell Description: {spell['description']}")
    print(f"Damage: {spell['damage']}")
    print(f"Mana Cost: {spell['mana_cost']}")
    print(f"Target Type: {spell['target_type']}")
    print(f"Special Effects: {spell['special_effects']}")
    print()
    
    initial_defense = player.defense_bonus
    result = cast_spell(spell_builder, "Heavy", "Water", "Wall", player, [enemy])
    print(result)
    print()
    print(f"Player Defense Bonus: {player.defense_bonus} (was {initial_defense})")
    print()


if __name__ == "__main__":
    test_scenario_1()
    test_scenario_2()
    test_scenario_3()
