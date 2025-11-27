"""
Babel: The Word Alchemist - Web Version
Flask backend for the web game
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from babel_rpg import (
    WordDatabase, SpellBuilder, Player, Enemy, cast_spell,
    WordType, StatusEffect
)
import json

app = Flask(__name__)
CORS(app)

# Global game state (in production, use session or database)
game_states = {}


class GameState:
    """Represents a game session"""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.word_db = WordDatabase()
        self.spell_builder = SpellBuilder(self.word_db)
        self.player = Player()
        self.enemy = Enemy("Goblin", 80, 20)
        self.player.draw_hand(self.word_db)
        self.turn = 1
        self.game_over = False
        self.log = []
    
    def to_dict(self):
        """Convert game state to dictionary for JSON response"""
        return {
            "player": {
                "name": self.player.name,
                "hp": self.player.hp,
                "max_hp": self.player.max_hp,
                "mana": self.player.mana,
                "max_mana": self.player.max_mana,
                "status_effects": [e.value for e in self.player.status_effects.keys()],
                "defense_bonus": self.player.defense_bonus
            },
            "enemy": {
                "name": self.enemy.name,
                "hp": self.enemy.hp,
                "max_hp": self.enemy.max_hp,
                "mana": self.enemy.mana,
                "max_mana": self.enemy.max_mana,
                "status_effects": [e.value for e in self.enemy.status_effects.keys()],
                "defense": self.enemy.defense
            },
            "hand": {
                "modifiers": [w for w in self.player.hand 
                             if self.word_db.get_word(w).word_type == WordType.MODIFIER],
                "cores": [w for w in self.player.hand 
                         if self.word_db.get_word(w).word_type == WordType.CORE],
                "shapes": [w for w in self.player.hand 
                          if self.word_db.get_word(w).word_type == WordType.SHAPE]
            },
            "turn": self.turn,
            "game_over": self.game_over,
            "log": self.log
        }


def get_game_state(session_id):
    """Get or create game state for session"""
    if session_id not in game_states:
        game_states[session_id] = GameState(session_id)
    return game_states[session_id]


@app.route('/')
def index():
    """Serve the main game page"""
    return render_template('index.html')


@app.route('/api/new_game', methods=['POST'])
def new_game():
    """Start a new game"""
    session_id = request.json.get('session_id', 'default')
    game_states[session_id] = GameState(session_id)
    state = game_states[session_id]
    state.log.append("=" * 60)
    state.log.append("Welcome to Babel: The Word Alchemist!")
    state.log.append("=" * 60)
    state.log.append("\nSelect a Modifier, Core, and Shape to cast a spell!")
    state.log.append("Example: Fast + Fire + Ball")
    state.log.append(f"\nYou are facing: {state.enemy.name} (HP: {state.enemy.hp}/{state.enemy.max_hp})")
    state.log.append("Good luck, Editor!\n")
    
    return jsonify({
        "success": True,
        "game_state": state.to_dict()
    })


@app.route('/api/game_state', methods=['GET'])
def get_state():
    """Get current game state"""
    session_id = request.args.get('session_id', 'default')
    state = get_game_state(session_id)
    return jsonify({
        "success": True,
        "game_state": state.to_dict()
    })


@app.route('/api/preview_spell', methods=['POST'])
def preview_spell():
    """Preview spell without casting"""
    session_id = request.json.get('session_id', 'default')
    modifier = request.json.get('modifier')
    core = request.json.get('core')
    shape = request.json.get('shape')
    
    state = get_game_state(session_id)
    
    if not all([modifier, core, shape]):
        return jsonify({"success": False, "error": "Missing words"})
    
    spell = state.spell_builder.build_spell(modifier, core, shape)
    
    if "error" in spell:
        return jsonify({"success": False, "error": spell["error"]})
    
    return jsonify({
        "success": True,
        "spell": {
            "description": spell["description"],
            "damage": spell["damage"],
            "mana_cost": spell["mana_cost"],
            "target_type": spell["target_type"],
            "status_effects": [e.value for e in spell["status_effects"]],
            "special_effects": spell["special_effects"]
        }
    })


@app.route('/api/cast_spell', methods=['POST'])
def cast_spell_api():
    """Cast a spell"""
    session_id = request.json.get('session_id', 'default')
    modifier = request.json.get('modifier')
    core = request.json.get('core')
    shape = request.json.get('shape')
    
    state = get_game_state(session_id)
    
    if state.game_over:
        return jsonify({"success": False, "error": "Game is over"})
    
    if not all([modifier, core, shape]):
        return jsonify({"success": False, "error": "Please select all three words"})
    
    # Validate words are in hand
    if modifier not in state.player.hand or core not in state.player.hand or shape not in state.player.hand:
        return jsonify({"success": False, "error": "All words must be in your hand"})
    
    # Cast spell
    result = cast_spell(
        state.spell_builder,
        modifier,
        core,
        shape,
        state.player,
        [state.enemy]
    )
    
    state.log.append(f"\n=== Turn {state.turn} ===")
    state.log.append(result)
    
    # Check if enemy is defeated
    if not state.enemy.is_alive():
        state.log.append("\n🎉 VICTORY! You have defeated the enemy!")
        state.game_over = True
        return jsonify({
            "success": True,
            "game_state": state.to_dict(),
            "victory": True
        })
    
    # Enemy turn
    state.enemy.process_status_effects()
    state.player.process_status_effects()
    
    if state.enemy.is_alive():
        enemy_damage = 8
        actual_damage = state.player.take_damage(enemy_damage)
        state.log.append(f"\n{state.enemy.name} attacks for {actual_damage} damage!")
    
    # Regenerate mana
    state.player.mana = min(state.player.max_mana, state.player.mana + 3)
    state.enemy.mana = min(state.enemy.max_mana, state.enemy.mana + 2)
    
    # Check if player is defeated
    if not state.player.is_alive():
        state.log.append("\n💀 DEFEAT! You have been defeated!")
        state.game_over = True
        return jsonify({
            "success": True,
            "game_state": state.to_dict(),
            "defeat": True
        })
    
    state.turn += 1
    
    return jsonify({
        "success": True,
        "game_state": state.to_dict()
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
