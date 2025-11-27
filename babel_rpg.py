"""
Babel: The Word Alchemist
A text-based RPG using tag-based deterministic logic (No LLM API)
"""

from enum import Enum
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field


class WordType(Enum):
    """Types of words in the spell system"""
    MODIFIER = "MODIFIER"
    CORE = "CORE"
    SHAPE = "SHAPE"


class StatusEffect(Enum):
    """Status effects that can be applied to entities"""
    BURNING = "BURNING"
    FROZEN = "FROZEN"
    ELECTROCUTED = "ELECTROCUTED"
    ARMOR_BROKEN = "ARMOR_BROKEN"
    POISONED = "POISONED"


@dataclass
class Word:
    """Represents a word in the spell system"""
    name: str
    word_type: WordType
    tags: List[str] = field(default_factory=list)
    values: Dict[str, float] = field(default_factory=dict)
    effect_hook: Optional[Callable] = None
    
    def __repr__(self):
        return f"Word({self.name}, {self.word_type.value})"


class WordDatabase:
    """Database containing all available words"""
    
    def __init__(self):
        self.words: Dict[str, Word] = {}
        self._initialize_words()
    
    def _initialize_words(self):
        """Initialize the word database with at least 15 words"""
        
        # MODIFIERS (5 words)
        self.words["Huge"] = Word(
            name="Huge",
            word_type=WordType.MODIFIER,
            tags=["SIZE", "AREA"],
            values={"area_multiplier": 2.0, "mana_cost_modifier": 1.5}
        )
        
        self.words["Fast"] = Word(
            name="Fast",
            word_type=WordType.MODIFIER,
            tags=["SPEED", "PRIORITY"],
            values={"speed_multiplier": 2.0, "priority": 10}
        )
        
        self.words["Vampiric"] = Word(
            name="Vampiric",
            word_type=WordType.MODIFIER,
            tags=["LIFESTEAL", "DARK"],
            values={"lifesteal_percent": 0.5, "mana_cost_modifier": 1.2}
        )
        
        self.words["Burning"] = Word(
            name="Burning",
            word_type=WordType.MODIFIER,
            tags=["HEAT", "FIRE"],
            values={"fire_damage_bonus": 5, "burn_chance": 0.8}
        )
        
        self.words["Heavy"] = Word(
            name="Heavy",
            word_type=WordType.MODIFIER,
            tags=["WEIGHT", "DEFENSE"],
            values={"defense_bonus": 15, "damage_multiplier": 1.3}
        )
        
        # Additional modifier for testing elemental interactions
        self.words["Electric"] = Word(
            name="Electric",
            word_type=WordType.MODIFIER,
            tags=["ELECTRIC", "SHOCK"],
            values={"damage_multiplier": 1.2, "shock_chance": 0.6}
        )
        
        # CORES (5 words)
        self.words["Fire"] = Word(
            name="Fire",
            word_type=WordType.CORE,
            tags=["HEAT", "ELEMENTAL", "DESTRUCTIVE"],
            values={"damage": 15, "mana_cost": 8, "element": "FIRE"}
        )
        
        self.words["Water"] = Word(
            name="Water",
            word_type=WordType.CORE,
            tags=["LIQUID", "ELEMENTAL", "COOLING"],
            values={"damage": 10, "mana_cost": 6, "element": "WATER"}
        )
        
        self.words["Sword"] = Word(
            name="Sword",
            word_type=WordType.CORE,
            tags=["METAL", "PHYSICAL", "SHARP"],
            values={"damage": 12, "mana_cost": 5, "element": "PHYSICAL"}
        )
        
        self.words["Stone"] = Word(
            name="Stone",
            word_type=WordType.CORE,
            tags=["EARTH", "SOLID", "DEFENSIVE"],
            values={"damage": 8, "mana_cost": 4, "defense": 10, "element": "EARTH"}
        )
        
        self.words["Lightning"] = Word(
            name="Lightning",
            word_type=WordType.CORE,
            tags=["ELECTRIC", "ELEMENTAL", "SHOCK"],
            values={"damage": 18, "mana_cost": 10, "element": "LIGHTNING"}
        )
        
        # SHAPES (5 words)
        self.words["Ball"] = Word(
            name="Ball",
            word_type=WordType.SHAPE,
            tags=["PROJECTILE", "SINGLE_TARGET"],
            values={"target_type": "SINGLE", "range": 1}
        )
        
        self.words["Rain"] = Word(
            name="Rain",
            word_type=WordType.SHAPE,
            tags=["AREA", "ALL_TARGETS"],
            values={"target_type": "ALL", "range": 0, "area_multiplier": 1.5}
        )
        
        self.words["Wall"] = Word(
            name="Wall",
            word_type=WordType.SHAPE,
            tags=["DEFENSIVE", "BARRIER"],
            values={"target_type": "SELF", "defense_bonus": 20, "duration": 3}
        )
        
        self.words["Ray"] = Word(
            name="Ray",
            word_type=WordType.SHAPE,
            tags=["PROJECTILE", "PIERCING"],
            values={"target_type": "SINGLE", "range": 2, "pierce": True}
        )
        
        self.words["Explosion"] = Word(
            name="Explosion",
            word_type=WordType.SHAPE,
            tags=["AREA", "DESTRUCTIVE"],
            values={"target_type": "ALL", "range": 1, "area_multiplier": 2.0}
        )
    
    def get_word(self, name: str) -> Optional[Word]:
        """Get a word by name"""
        return self.words.get(name)
    
    def get_words_by_type(self, word_type: WordType) -> List[Word]:
        """Get all words of a specific type"""
        return [word for word in self.words.values() if word.word_type == word_type]


class SpellBuilder:
    """Parses and calculates spell results from word combinations"""
    
    def __init__(self, word_db: WordDatabase):
        self.word_db = word_db
    
    def build_spell(self, modifier_name: str, core_name: str, shape_name: str) -> Dict:
        """
        Build a spell from three words and return its properties
        
        Returns a dictionary with:
        - damage: Final damage value
        - mana_cost: Final mana cost
        - target_type: Who/what the spell targets
        - description: Text description of the spell
        - status_effects: List of status effects to apply
        - special_effects: Any special effects (lifesteal, etc.)
        """
        modifier = self.word_db.get_word(modifier_name)
        core = self.word_db.get_word(core_name)
        shape = self.word_db.get_word(shape_name)
        
        if not all([modifier, core, shape]):
            return {"error": "Invalid word combination"}
        
        # Base stats from core
        base_damage = core.values.get("damage", 0)
        base_mana_cost = core.values.get("mana_cost", 0)
        element = core.values.get("element", "NONE")
        
        # Apply modifier effects
        final_damage = base_damage
        final_mana_cost = base_mana_cost
        
        # Modifier multipliers
        if "damage_multiplier" in modifier.values:
            final_damage *= modifier.values["damage_multiplier"]
        
        if "mana_cost_modifier" in modifier.values:
            final_mana_cost *= modifier.values["mana_cost_modifier"]
        
        # Modifier bonuses
        if "fire_damage_bonus" in modifier.values:
            final_damage += modifier.values["fire_damage_bonus"]
        
        # Shape determines targeting
        target_type = shape.values.get("target_type", "SINGLE")
        
        # Tag interactions (synergy system)
        status_effects = []
        special_effects = {}
        description_parts = []
        
        # Check for tag synergies
        core_tags = set(core.tags)
        modifier_tags = set(modifier.tags)
        shape_tags = set(shape.tags)
        
        # LIQUID + COLD = Ice (Freeze)
        if "LIQUID" in core_tags and "COLD" in modifier_tags:
            status_effects.append(StatusEffect.FROZEN)
            description_parts.append("freezing")
            final_damage *= 0.8  # Ice does less damage but freezes
        
        # HEAT + LIQUID = Steam (if water, creates steam effect)
        if "HEAT" in modifier_tags and "LIQUID" in core_tags:
            description_parts.append("steaming")
            final_damage *= 1.2
        
        # FIRE + OIL (if we had oil) = Explosion
        # For now, Fire + Explosion shape = extra damage
        if "FIRE" in modifier_tags and "DESTRUCTIVE" in shape_tags:
            final_damage *= 1.5
            description_parts.append("explosive")
        
        # VAMPIRIC + any damage = lifesteal
        if "LIFESTEAL" in modifier_tags:
            lifesteal_percent = modifier.values.get("lifesteal_percent", 0.5)
            special_effects["lifesteal"] = final_damage * lifesteal_percent
        
        # HEAVY + WALL = High defense barrier
        if "WEIGHT" in modifier_tags and "BARRIER" in shape_tags:
            defense_bonus = modifier.values.get("defense_bonus", 0) + shape.values.get("defense_bonus", 0)
            special_effects["defense_bonus"] = defense_bonus
            description_parts.append("massive defensive")
        
        # FAST + any = high priority
        if "SPEED" in modifier_tags:
            special_effects["priority"] = modifier.values.get("priority", 10)
            description_parts.append("swift")
        
        # BURNING modifier adds burn status
        if "BURN" in modifier_tags or "FIRE" in modifier_tags:
            if modifier.values.get("burn_chance", 0) > 0.5:
                status_effects.append(StatusEffect.BURNING)
        
        # WATER + LIGHTNING = Electrocuted
        # Check if spell involves both LIQUID and ELECTRIC tags (from any word)
        all_tags = core_tags | modifier_tags | shape_tags
        if "LIQUID" in all_tags and "ELECTRIC" in all_tags:
            status_effects.append(StatusEffect.ELECTROCUTED)
            description_parts.append("electrifying")
            final_damage *= 1.3  # Electrocution does extra damage
        
        # Build description
        if not description_parts:
            description_parts.append(modifier.name.lower())
        
        description = f"{' '.join(description_parts)} {core.name.lower()} {shape.name.lower()}"
        
        return {
            "damage": int(final_damage),
            "mana_cost": int(final_mana_cost),
            "target_type": target_type,
            "description": description,
            "status_effects": status_effects,
            "special_effects": special_effects,
            "element": element
        }


class Entity:
    """Base class for Player and Enemy"""
    
    def __init__(self, name: str, max_hp: int, max_mana: int):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.max_mana = max_mana
        self.mana = max_mana
        self.status_effects: Dict[StatusEffect, int] = {}  # Effect -> turns remaining
        self.defense = 0
        self.defense_bonus = 0  # Temporary defense from spells
    
    def take_damage(self, damage: int, element: str = "PHYSICAL"):
        """Apply damage to the entity"""
        total_defense = self.defense + self.defense_bonus
        actual_damage = max(1, damage - total_defense)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage
    
    def heal(self, amount: int):
        """Heal the entity"""
        self.hp = min(self.max_hp, self.hp + amount)
        return amount
    
    def add_status_effect(self, effect: StatusEffect, duration: int = 3):
        """Add a status effect"""
        self.status_effects[effect] = duration
    
    def process_status_effects(self):
        """Process status effects at the end of turn"""
        effects_to_remove = []
        for effect, turns in self.status_effects.items():
            if effect == StatusEffect.BURNING:
                self.take_damage(3, "FIRE")
            elif effect == StatusEffect.POISONED:
                self.take_damage(2, "POISON")
            
            self.status_effects[effect] = turns - 1
            if self.status_effects[effect] <= 0:
                effects_to_remove.append(effect)
        
        for effect in effects_to_remove:
            del self.status_effects[effect]
    
    def is_alive(self) -> bool:
        """Check if entity is alive"""
        return self.hp > 0
    
    def get_status_string(self) -> str:
        """Get a string representation of current status"""
        status_str = f"{self.name}: HP={self.hp}/{self.max_hp}, Mana={self.mana}/{self.max_mana}"
        if self.status_effects:
            effects = [e.value for e in self.status_effects.keys()]
            status_str += f" [{', '.join(effects)}]"
        return status_str


class Player(Entity):
    """The player character"""
    
    def __init__(self):
        super().__init__("Editor", 100, 50)
        self.hand: List[str] = []  # Available words to use
    
    def draw_hand(self, word_db: WordDatabase, hand_size: int = 9):
        """Draw a hand of words from the database"""
        all_words = list(word_db.words.keys())
        # Simple hand: 3 modifiers, 3 cores, 3 shapes
        modifiers = [w for w in all_words if word_db.get_word(w).word_type == WordType.MODIFIER]
        cores = [w for w in all_words if word_db.get_word(w).word_type == WordType.CORE]
        shapes = [w for w in all_words if word_db.get_word(w).word_type == WordType.SHAPE]
        
        self.hand = modifiers[:3] + cores[:3] + shapes[:3]


class Enemy(Entity):
    """Enemy entity"""
    
    def __init__(self, name: str, max_hp: int, max_mana: int):
        super().__init__(name, max_hp, max_mana)
        self.defense = 5


def cast_spell(spell_builder: SpellBuilder, modifier: str, core: str, shape: str, 
               caster: Entity, targets: List[Entity]) -> str:
    """
    Cast a spell and apply its effects
    
    Returns a text log describing what happened
    """
    spell = spell_builder.build_spell(modifier, core, shape)
    
    if "error" in spell:
        return f"Error: {spell['error']}"
    
    # Check mana
    if caster.mana < spell["mana_cost"]:
        return f"{caster.name} doesn't have enough mana! (Need {spell['mana_cost']}, have {caster.mana})"
    
    # Consume mana
    caster.mana -= spell["mana_cost"]
    
    # Determine targets
    if spell["target_type"] == "SINGLE":
        actual_targets = [targets[0]] if targets else []
    elif spell["target_type"] == "ALL":
        actual_targets = targets
    elif spell["target_type"] == "SELF":
        actual_targets = [caster]
    else:
        actual_targets = targets[:1]
    
    log_lines = [f"{caster.name} casts: {spell['description']}!"]
    
    # Apply effects to targets
    for target in actual_targets:
        if not target.is_alive():
            continue
        
        # Defensive spells (SELF target with defense_bonus) don't deal damage
        is_defensive = (spell["target_type"] == "SELF" and 
                       "defense_bonus" in spell["special_effects"] and 
                       target == caster)
        
        if not is_defensive and spell["damage"] > 0:
            damage_dealt = target.take_damage(spell["damage"], spell["element"])
            log_lines.append(f"  → {target.name} takes {damage_dealt} {spell['element']} damage! (HP: {target.hp}/{target.max_hp})")
        
        # Apply status effects
        for effect in spell["status_effects"]:
            target.add_status_effect(effect)
            log_lines.append(f"  → {target.name} is now {effect.value.lower()}!")
        
        # Apply special effects
        if "lifesteal" in spell["special_effects"] and target != caster:
            heal_amount = caster.heal(int(spell["special_effects"]["lifesteal"]))
            log_lines.append(f"  → {caster.name} heals {heal_amount} HP from lifesteal!")
        
        if "defense_bonus" in spell["special_effects"] and target == caster:
            target.defense_bonus = spell["special_effects"]["defense_bonus"]
            log_lines.append(f"  → {caster.name} gains {target.defense_bonus} defense!")
    
    return "\n".join(log_lines)


def combat_loop():
    """Main combat loop"""
    print("=" * 60)
    print("Babel: The Word Alchemist")
    print("=" * 60)
    print()
    
    # Initialize game systems
    word_db = WordDatabase()
    spell_builder = SpellBuilder(word_db)
    player = Player()
    enemy = Enemy("Goblin", 80, 20)
    
    # Draw initial hand
    player.draw_hand(word_db)
    
    turn = 1
    
    while player.is_alive() and enemy.is_alive():
        print(f"\n{'='*60}")
        print(f"Turn {turn}")
        print(f"{'='*60}")
        print(player.get_status_string())
        print(enemy.get_status_string())
        print()
        
        # Show available words
        print("Your Hand:")
        modifiers = [w for w in player.hand if word_db.get_word(w).word_type == WordType.MODIFIER]
        cores = [w for w in player.hand if word_db.get_word(w).word_type == WordType.CORE]
        shapes = [w for w in player.hand if word_db.get_word(w).word_type == WordType.SHAPE]
        
        print(f"  Modifiers: {', '.join(modifiers)}")
        print(f"  Cores: {', '.join(cores)}")
        print(f"  Shapes: {', '.join(shapes)}")
        print()
        
        # Player input
        print("Cast a spell! (Format: Modifier Core Shape)")
        print("Example: Fast Fire Ball")
        user_input = input("> ").strip().split()
        
        if len(user_input) != 3:
            print("Invalid input! Please provide exactly 3 words.")
            continue
        
        modifier, core, shape = user_input[0].capitalize(), user_input[1].capitalize(), user_input[2].capitalize()
        
        # Validate words are in hand
        if modifier not in player.hand or core not in player.hand or shape not in player.hand:
            print("Error: All words must be in your hand!")
            continue
        
        # Cast spell
        result = cast_spell(spell_builder, modifier, core, shape, player, [enemy])
        print(result)
        
        # Check if enemy is defeated
        if not enemy.is_alive():
            print(f"\n🎉 Victory! {enemy.name} has been defeated!")
            break
        
        # Enemy turn (simple AI)
        print(f"\n{enemy.name}'s turn...")
        enemy.process_status_effects()
        if enemy.is_alive():
            # Simple enemy attack
            enemy_damage = 8
            player.take_damage(enemy_damage)
            print(f"{enemy.name} attacks for {enemy_damage} damage!")
        
        # Process player status effects
        player.process_status_effects()
        
        # Regenerate some mana
        player.mana = min(player.max_mana, player.mana + 3)
        enemy.mana = min(enemy.max_mana, enemy.mana + 2)
        
        # Check if player is defeated
        if not player.is_alive():
            print(f"\n💀 Defeat! {player.name} has been defeated!")
            break
        
        turn += 1
    
    print("\n" + "=" * 60)
    print("Game Over")
    print("=" * 60)


if __name__ == "__main__":
    combat_loop()


"""
================================================================================
HOW TO ADD NEW WORDS TO THE DATABASE
================================================================================

To expand the game with new words, add entries to the WordDatabase._initialize_words() method.

1. MODIFIER Words (Adjectives):
   - Add tags that describe properties (e.g., "COLD", "HEAT", "SIZE", "SPEED")
   - Set values that modify spell properties (e.g., "damage_multiplier", "area_multiplier")
   
   Example:
   self.words["Cold"] = Word(
       name="Cold",
       word_type=WordType.MODIFIER,
       tags=["COLD", "ELEMENTAL"],
       values={"damage_multiplier": 0.9, "freeze_chance": 0.7}
   )

2. CORE Words (Elements/Substances):
   - Add tags that define the element's nature (e.g., "LIQUID", "METAL", "ELEMENTAL")
   - Set base damage and mana_cost values
   - Define the element type in values["element"]
   
   Example:
   self.words["Oil"] = Word(
       name="Oil",
       word_type=WordType.CORE,
       tags=["LIQUID", "FLAMMABLE"],
       values={"damage": 5, "mana_cost": 4, "element": "PHYSICAL"}
   )

3. SHAPE Words (Manifestations):
   - Add tags that define targeting (e.g., "SINGLE_TARGET", "ALL_TARGETS", "BARRIER")
   - Set target_type in values ("SINGLE", "ALL", "SELF")
   - Add special properties like "area_multiplier" or "defense_bonus"
   
   Example:
   self.words["Shield"] = Word(
       name="Shield",
       word_type=WordType.SHAPE,
       tags=["DEFENSIVE", "BARRIER"],
       values={"target_type": "SELF", "defense_bonus": 15, "duration": 2}
   )

4. Adding Tag Interactions:
   To create new synergies, add checks in SpellBuilder.build_spell() method:
   
   Example (Oil + Fire = Explosion):
   if "FLAMMABLE" in core_tags and "HEAT" in modifier_tags:
       final_damage *= 2.0
       description_parts.append("explosive")
       status_effects.append(StatusEffect.BURNING)

5. Adding Status Effects:
   - Add new effects to the StatusEffect enum
   - Handle them in Entity.process_status_effects()
   - Apply them in SpellBuilder.build_spell() based on tag combinations

The tag system is flexible - any combination of tags can trigger interactions,
making the game highly expandable without changing core logic!
"""
