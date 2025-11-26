"""
Babel: The Word Alchemist - GUI Version
A text-based RPG with graphical interface using Tkinter
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from babel_rpg import (
    WordDatabase, SpellBuilder, Player, Enemy, cast_spell,
    WordType, StatusEffect
)
import threading
import time


class HealthBar(ttk.Frame):
    """Custom health/mana bar widget"""
    
    def __init__(self, parent, label_text, max_value, bar_color="#4CAF50"):
        super().__init__(parent)
        self.max_value = max_value
        self.current_value = max_value
        self.bar_color = bar_color
        
        # Label
        self.label = tk.Label(self, text=label_text, font=("Arial", 10, "bold"))
        self.label.pack(anchor="w")
        
        # Frame for bar
        self.bar_frame = tk.Frame(self, bg="#2c2c2c", relief=tk.SUNKEN, bd=2)
        self.bar_frame.pack(fill=tk.X, pady=2)
        
        # Bar canvas
        self.canvas = tk.Canvas(self.bar_frame, height=20, bg="#2c2c2c", 
                               highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Text overlay
        self.text_label = tk.Label(self.bar_frame, text="", 
                                  font=("Arial", 9), bg="#2c2c2c", fg="white")
        self.text_label.pack()
        
        self.update_display()
    
    def set_value(self, value):
        """Update the bar value"""
        self.current_value = max(0, min(value, self.max_value))
        self.update_display()
    
    def update_display(self):
        """Update the visual display"""
        percentage = self.current_value / self.max_value if self.max_value > 0 else 0
        
        # Update text first
        self.text_label.config(
            text=f"{int(self.current_value)}/{int(self.max_value)}"
        )
        
        # Schedule canvas update after widget is rendered
        try:
            self.master.after_idle(self._draw_bar, percentage)
        except:
            # Fallback: try to draw immediately
            self._draw_bar(percentage)
    
    def _draw_bar(self, percentage):
        """Draw the bar on the canvas"""
        try:
            self.canvas.update_idletasks()
            width = self.bar_frame.winfo_width()
            if width > 1:
                bar_width = int(width * percentage)
                
                # Clear canvas
                self.canvas.delete("all")
                
                # Draw background
                self.canvas.create_rectangle(0, 0, width, 20, fill="#1a1a1a", outline="")
                
                # Draw bar
                if bar_width > 0:
                    self.canvas.create_rectangle(0, 0, bar_width, 20, 
                                                fill=self.bar_color, outline="")
        except (tk.TclError, AttributeError):
            # Widget might be destroyed, ignore
            pass


class WordButton(tk.Button):
    """Custom button for word selection"""
    
    def __init__(self, parent, word_name, word_type, command, **kwargs):
        # Color scheme based on word type
        colors = {
            WordType.MODIFIER: {"bg": "#6c5ce7", "activebg": "#5f4fd6", "fg": "white"},
            WordType.CORE: {"bg": "#e74c3c", "activebg": "#c0392b", "fg": "white"},
            WordType.SHAPE: {"bg": "#3498db", "activebg": "#2980b9", "fg": "white"}
        }
        
        color = colors.get(word_type, {"bg": "#95a5a6", "activebg": "#7f8c8d", "fg": "white"})
        
        super().__init__(
            parent,
            text=word_name,
            font=("Arial", 11, "bold"),
            command=command,
            relief=tk.RAISED,
            bd=2,
            padx=10,
            pady=5,
            cursor="hand2",
            **color,
            **kwargs
        )


class BabelGameGUI:
    """Main GUI application for Babel: The Word Alchemist"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Babel: The Word Alchemist")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1e1e1e")
        
        # Initialize game systems
        self.word_db = WordDatabase()
        self.spell_builder = SpellBuilder(self.word_db)
        self.player = Player()
        self.enemy = Enemy("Goblin", 80, 20)
        
        # Selected words
        self.selected_modifier = None
        self.selected_core = None
        self.selected_shape = None
        
        # Draw initial hand
        self.player.draw_hand(self.word_db)
        
        # Game state
        self.turn = 1
        self.game_over = False
        
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Main container
        main_frame = tk.Frame(self.root, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame - Title
        title_frame = tk.Frame(main_frame, bg="#1e1e1e")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(
            title_frame,
            text="Babel: The Word Alchemist",
            font=("Arial", 20, "bold"),
            bg="#1e1e1e",
            fg="#ecf0f1"
        )
        title_label.pack()
        
        # Middle frame - Stats and word selection
        middle_frame = tk.Frame(main_frame, bg="#1e1e1e")
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Player stats
        left_panel = tk.Frame(middle_frame, bg="#2c2c2c", relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        player_title = tk.Label(
            left_panel,
            text="Editor (You)",
            font=("Arial", 14, "bold"),
            bg="#2c2c2c",
            fg="#ecf0f1"
        )
        player_title.pack(pady=10)
        
        # Player HP bar
        self.player_hp_bar = HealthBar(left_panel, "Health", self.player.max_hp, "#e74c3c")
        self.player_hp_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # Player Mana bar
        self.player_mana_bar = HealthBar(left_panel, "Mana", self.player.max_mana, "#3498db")
        self.player_mana_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # Player status effects
        self.player_status_label = tk.Label(
            left_panel,
            text="Status: None",
            font=("Arial", 10),
            bg="#2c2c2c",
            fg="#ecf0f1",
            wraplength=200
        )
        self.player_status_label.pack(pady=10)
        
        # Right panel - Enemy stats
        right_panel = tk.Frame(middle_frame, bg="#2c2c2c", relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        enemy_title = tk.Label(
            right_panel,
            text=f"{self.enemy.name}",
            font=("Arial", 14, "bold"),
            bg="#2c2c2c",
            fg="#e74c3c"
        )
        enemy_title.pack(pady=10)
        
        # Enemy HP bar
        self.enemy_hp_bar = HealthBar(right_panel, "Health", self.enemy.max_hp, "#e74c3c")
        self.enemy_hp_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # Enemy Mana bar
        self.enemy_mana_bar = HealthBar(right_panel, "Mana", self.enemy.max_mana, "#3498db")
        self.enemy_mana_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # Enemy status effects
        self.enemy_status_label = tk.Label(
            right_panel,
            text="Status: None",
            font=("Arial", 10),
            bg="#2c2c2c",
            fg="#ecf0f1",
            wraplength=200
        )
        self.enemy_status_label.pack(pady=10)
        
        # Center panel - Word selection
        center_panel = tk.Frame(middle_frame, bg="#1e1e1e")
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Selected spell display
        spell_frame = tk.Frame(center_panel, bg="#34495e", relief=tk.RAISED, bd=2)
        spell_frame.pack(fill=tk.X, pady=(0, 10))
        
        spell_title = tk.Label(
            spell_frame,
            text="Selected Spell",
            font=("Arial", 12, "bold"),
            bg="#34495e",
            fg="#ecf0f1"
        )
        spell_title.pack(pady=5)
        
        self.spell_display = tk.Label(
            spell_frame,
            text="[Modifier] + [Core] + [Shape]",
            font=("Arial", 14, "bold"),
            bg="#34495e",
            fg="#f39c12",
            height=2
        )
        self.spell_display.pack(pady=5)
        
        # Spell info display
        self.spell_info = tk.Label(
            spell_frame,
            text="",
            font=("Arial", 9),
            bg="#34495e",
            fg="#ecf0f1",
            wraplength=300
        )
        self.spell_info.pack(pady=5)
        
        # Word selection sections
        word_selection_frame = tk.Frame(center_panel, bg="#1e1e1e")
        word_selection_frame.pack(fill=tk.BOTH, expand=True)
        
        # Modifiers section
        modifier_frame = tk.LabelFrame(
            word_selection_frame,
            text="Modifiers",
            font=("Arial", 11, "bold"),
            bg="#1e1e1e",
            fg="#6c5ce7",
            bd=2
        )
        modifier_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.modifier_buttons_frame = tk.Frame(modifier_frame, bg="#1e1e1e")
        self.modifier_buttons_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Cores section
        core_frame = tk.LabelFrame(
            word_selection_frame,
            text="Cores",
            font=("Arial", 11, "bold"),
            bg="#1e1e1e",
            fg="#e74c3c",
            bd=2
        )
        core_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.core_buttons_frame = tk.Frame(core_frame, bg="#1e1e1e")
        self.core_buttons_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Shapes section
        shape_frame = tk.LabelFrame(
            word_selection_frame,
            text="Shapes",
            font=("Arial", 11, "bold"),
            bg="#1e1e1e",
            fg="#3498db",
            bd=2
        )
        shape_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.shape_buttons_frame = tk.Frame(shape_frame, bg="#1e1e1e")
        self.shape_buttons_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Cast spell button
        self.cast_button = tk.Button(
            center_panel,
            text="CAST SPELL",
            font=("Arial", 16, "bold"),
            bg="#27ae60",
            fg="white",
            activebackground="#229954",
            activeforeground="white",
            relief=tk.RAISED,
            bd=3,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.cast_spell_action
        )
        self.cast_button.pack(pady=10)
        
        # Bottom frame - Combat log
        log_frame = tk.LabelFrame(
            main_frame,
            text="Combat Log",
            font=("Arial", 11, "bold"),
            bg="#1e1e1e",
            fg="#ecf0f1",
            bd=2
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            font=("Consolas", 10),
            bg="#2c2c2c",
            fg="#ecf0f1",
            insertbackground="#ecf0f1",
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create word buttons
        self.create_word_buttons()
        
        # Initial log message
        self.log_message("=" * 60, "#f39c12")
        self.log_message("Welcome to Babel: The Word Alchemist!", "#f39c12")
        self.log_message("=" * 60, "#f39c12")
        self.log_message("\nSelect a Modifier, Core, and Shape to cast a spell!")
        self.log_message("Example: Fast + Fire + Ball")
        self.log_message(f"\nYou are facing: {self.enemy.name} (HP: {self.enemy.hp}/{self.enemy.max_hp})")
        self.log_message("Good luck, Editor!\n")
    
    def create_word_buttons(self):
        """Create buttons for available words"""
        
        # Clear existing buttons
        for widget in self.modifier_buttons_frame.winfo_children():
            widget.destroy()
        for widget in self.core_buttons_frame.winfo_children():
            widget.destroy()
        for widget in self.shape_buttons_frame.winfo_children():
            widget.destroy()
        
        # Get words by type
        modifiers = [w for w in self.player.hand 
                    if self.word_db.get_word(w).word_type == WordType.MODIFIER]
        cores = [w for w in self.player.hand 
                if self.word_db.get_word(w).word_type == WordType.CORE]
        shapes = [w for w in self.player.hand 
                 if self.word_db.get_word(w).word_type == WordType.SHAPE]
        
        # Create modifier buttons
        for word_name in modifiers:
            word = self.word_db.get_word(word_name)
            btn = WordButton(
                self.modifier_buttons_frame,
                word_name,
                WordType.MODIFIER,
                lambda w=word_name: self.select_word(w, WordType.MODIFIER)
            )
            btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Create core buttons
        for word_name in cores:
            word = self.word_db.get_word(word_name)
            btn = WordButton(
                self.core_buttons_frame,
                word_name,
                WordType.CORE,
                lambda w=word_name: self.select_word(w, WordType.CORE)
            )
            btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Create shape buttons
        for word_name in shapes:
            word = self.word_db.get_word(word_name)
            btn = WordButton(
                self.shape_buttons_frame,
                word_name,
                WordType.SHAPE,
                lambda w=word_name: self.select_word(w, WordType.SHAPE)
            )
            btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
    
    def select_word(self, word_name, word_type):
        """Handle word selection"""
        if word_type == WordType.MODIFIER:
            self.selected_modifier = word_name
        elif word_type == WordType.CORE:
            self.selected_core = word_name
        elif word_type == WordType.SHAPE:
            self.selected_shape = word_name
        
        self.update_spell_display()
        self.highlight_selected_words()
    
    def highlight_selected_words(self):
        """Highlight selected word buttons"""
        # Reset all buttons
        for widget in self.modifier_buttons_frame.winfo_children():
            widget.config(relief=tk.RAISED)
        for widget in self.core_buttons_frame.winfo_children():
            widget.config(relief=tk.RAISED)
        for widget in self.shape_buttons_frame.winfo_children():
            widget.config(relief=tk.RAISED)
        
        # Highlight selected
        for widget in self.modifier_buttons_frame.winfo_children():
            if widget.cget("text") == self.selected_modifier:
                widget.config(relief=tk.SUNKEN, bd=3)
        
        for widget in self.core_buttons_frame.winfo_children():
            if widget.cget("text") == self.selected_core:
                widget.config(relief=tk.SUNKEN, bd=3)
        
        for widget in self.shape_buttons_frame.winfo_children():
            if widget.cget("text") == self.selected_shape:
                widget.config(relief=tk.SUNKEN, bd=3)
    
    def update_spell_display(self):
        """Update the spell display"""
        modifier = self.selected_modifier or "[Modifier]"
        core = self.selected_core or "[Core]"
        shape = self.selected_shape or "[Shape]"
        
        self.spell_display.config(text=f"{modifier} + {core} + {shape}")
        
        # Update spell info if all words are selected
        if all([self.selected_modifier, self.selected_core, self.selected_shape]):
            try:
                spell = self.spell_builder.build_spell(
                    self.selected_modifier,
                    self.selected_core,
                    self.selected_shape
                )
                if "error" not in spell:
                    info_text = f"Damage: {spell['damage']} | Mana: {spell['mana_cost']} | Target: {spell['target_type']}"
                    if spell['status_effects']:
                        effects = ", ".join([e.value for e in spell['status_effects']])
                        info_text += f"\nEffects: {effects}"
                    self.spell_info.config(text=info_text)
                else:
                    self.spell_info.config(text="")
            except:
                self.spell_info.config(text="")
        else:
            self.spell_info.config(text="")
    
    def log_message(self, message, color="#ecf0f1"):
        """Add a message to the combat log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def update_display(self):
        """Update all displays"""
        # Update health bars
        self.player_hp_bar.set_value(self.player.hp)
        self.player_mana_bar.set_value(self.player.mana)
        self.enemy_hp_bar.set_value(self.enemy.hp)
        self.enemy_mana_bar.set_value(self.enemy.mana)
        
        # Update status effects
        player_status = ", ".join([e.value for e in self.player.status_effects.keys()])
        if not player_status:
            player_status = "None"
        self.player_status_label.config(text=f"Status: {player_status}")
        
        enemy_status = ", ".join([e.value for e in self.enemy.status_effects.keys()])
        if not enemy_status:
            enemy_status = "None"
        self.enemy_status_label.config(text=f"Status: {enemy_status}")
        
        # Force update of health bars after a short delay to ensure proper rendering
        self.root.after(10, self._update_bars)
    
    def _update_bars(self):
        """Internal method to update bar displays"""
        self.player_hp_bar.update_display()
        self.player_mana_bar.update_display()
        self.enemy_hp_bar.update_display()
        self.enemy_mana_bar.update_display()
    
    def cast_spell_action(self):
        """Handle spell casting"""
        if self.game_over:
            return
        
        if not all([self.selected_modifier, self.selected_core, self.selected_shape]):
            messagebox.showwarning(
                "Incomplete Spell",
                "Please select a Modifier, Core, and Shape!"
            )
            return
        
        # Cast the spell
        result = cast_spell(
            self.spell_builder,
            self.selected_modifier,
            self.selected_core,
            self.selected_shape,
            self.player,
            [self.enemy]
        )
        
        self.log_message(f"\n=== Turn {self.turn} ===", "#f39c12")
        self.log_message(result)
        
        # Update display
        self.update_display()
        
        # Check if enemy is defeated
        if not self.enemy.is_alive():
            self.log_message("\n🎉 VICTORY! You have defeated the enemy!", "#27ae60")
            self.game_over = True
            messagebox.showinfo("Victory!", "You have defeated the enemy!")
            return
        
        # Reset selections
        self.selected_modifier = None
        self.selected_core = None
        self.selected_shape = None
        self.update_spell_display()
        self.highlight_selected_words()
        
        # Enemy turn (delayed)
        self.root.after(1000, self.enemy_turn)
    
    def enemy_turn(self):
        """Handle enemy's turn"""
        if self.game_over:
            return
        
        # Process status effects
        self.enemy.process_status_effects()
        self.player.process_status_effects()
        
        # Simple enemy attack
        if self.enemy.is_alive():
            enemy_damage = 8
            actual_damage = self.player.take_damage(enemy_damage)
            self.log_message(
                f"\n{self.enemy.name} attacks for {actual_damage} damage!",
                "#e74c3c"
            )
        
        # Regenerate mana
        self.player.mana = min(self.player.max_mana, self.player.mana + 3)
        self.enemy.mana = min(self.enemy.max_mana, self.enemy.mana + 2)
        
        # Update display
        self.update_display()
        
        # Check if player is defeated
        if not self.player.is_alive():
            self.log_message("\n💀 DEFEAT! You have been defeated!", "#e74c3c")
            self.game_over = True
            messagebox.showerror("Defeat", "You have been defeated!")
            return
        
        self.turn += 1


def main():
    """Main entry point"""
    root = tk.Tk()
    app = BabelGameGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
