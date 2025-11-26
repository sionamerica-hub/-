# Babel: The Word Alchemist

A text-based RPG using tag-based deterministic logic (No LLM API required).

## Overview

In this game, you play as an "Editor" who casts spells by combining words. The spell formula is:

**[Modifier] + [Core] + [Shape]**

- **Modifier**: Adjectives that alter properties (e.g., Huge, Burning, Fast, Vampiric)
- **Core**: The element or substance (e.g., Fire, Stone, Sword, Water)
- **Shape**: How the spell manifests (e.g., Ball, Wall, Rain, Ray)

## Features

- **Tag-Based System**: Words have tags that interact with each other to create unique spell effects
- **Elemental Interactions**: Similar to Divinity: Original Sin, elements combine in creative ways
  - Water + Lightning = Electrocuted (Stun)
  - Fire + Oil = Explosion (High Damage)
  - Heavy + Water + Wall = High Defense Barrier
- **Status Effects**: Burning, Frozen, Electrocuted, Armor Broken, Poisoned
- **Creative Combinations**: Over 15 words with multiple interaction possibilities

## How to Run

```bash
python3 babel_rpg.py
```

## Example Spell Combinations

1. **Fast + Fire + Ball**: Deals Fire damage with high priority speed
2. **Vampiric + Sword + Rain**: Deals Physical damage to all enemies and heals the player
3. **Heavy + Water + Wall**: Creates a high-defense barrier
4. **Electric + Water + Ball**: Electrocutes the target (Water + Lightning interaction)

## Gameplay

- You start with a hand of 9 words (3 modifiers, 3 cores, 3 shapes)
- Each turn, combine 3 words to cast a spell
- Defeat enemies by reducing their HP to 0
- Manage your mana carefully - spells cost mana to cast
- Status effects persist across turns

## Architecture

The game uses a deterministic tag-based system:
- Each word is an object with `name`, `word_type`, `tags`, `values`, and optional `effect_hook`
- The `SpellBuilder` class processes word combinations and calculates results
- Tag interactions are checked systematically to create synergies
- No external APIs required - all logic is deterministic

## Adding New Words

See the documentation at the end of `babel_rpg.py` for detailed instructions on adding new words to expand the game.
