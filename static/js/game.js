// Babel: The Word Alchemist - Game Logic
class BabelGame {
    constructor() {
        this.sessionId = 'game_' + Date.now();
        this.selectedModifier = null;
        this.selectedCore = null;
        this.selectedShape = null;
        this.gameState = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.newGame();
    }
    
    setupEventListeners() {
        document.getElementById('newGameBtn').addEventListener('click', () => this.newGame());
        document.getElementById('castBtn').addEventListener('click', () => this.castSpell());
    }
    
    async newGame() {
        try {
            const response = await fetch('/api/new_game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId
                })
            });
            
            const data = await response.json();
            if (data.success) {
                this.gameState = data.game_state;
                this.updateDisplay();
                this.resetSelections();
            }
        } catch (error) {
            console.error('Error starting new game:', error);
            alert('Error starting game. Please refresh the page.');
        }
    }
    
    async updateGameState() {
        try {
            const response = await fetch(`/api/game_state?session_id=${this.sessionId}`);
            const data = await response.json();
            if (data.success) {
                this.gameState = data.game_state;
                this.updateDisplay();
            }
        } catch (error) {
            console.error('Error updating game state:', error);
        }
    }
    
    async previewSpell() {
        if (!this.selectedModifier || !this.selectedCore || !this.selectedShape) {
            document.getElementById('spellInfo').textContent = '';
            return;
        }
        
        try {
            const response = await fetch('/api/preview_spell', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    modifier: this.selectedModifier,
                    core: this.selectedCore,
                    shape: this.selectedShape
                })
            });
            
            const data = await response.json();
            if (data.success) {
                const spell = data.spell;
                let infoText = `Damage: ${spell.damage} | Mana: ${spell.mana_cost} | Target: ${spell.target_type}`;
                if (spell.status_effects && spell.status_effects.length > 0) {
                    infoText += `\nEffects: ${spell.status_effects.join(', ')}`;
                }
                document.getElementById('spellInfo').textContent = infoText;
            }
        } catch (error) {
            console.error('Error previewing spell:', error);
        }
    }
    
    async castSpell() {
        if (!this.selectedModifier || !this.selectedCore || !this.selectedShape) {
            alert('Please select a Modifier, Core, and Shape!');
            return;
        }
        
        if (this.gameState && this.gameState.game_over) {
            alert('Game is over! Start a new game.');
            return;
        }
        
        try {
            const response = await fetch('/api/cast_spell', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    modifier: this.selectedModifier,
                    core: this.selectedCore,
                    shape: this.selectedShape
                })
            });
            
            const data = await response.json();
            if (data.success) {
                this.gameState = data.game_state;
                this.updateDisplay();
                this.resetSelections();
                
                if (data.victory) {
                    setTimeout(() => {
                        alert('🎉 Victory! You have defeated the enemy!');
                    }, 500);
                } else if (data.defeat) {
                    setTimeout(() => {
                        alert('💀 Defeat! You have been defeated!');
                    }, 500);
                }
            } else {
                alert(data.error || 'Error casting spell');
            }
        } catch (error) {
            console.error('Error casting spell:', error);
            alert('Error casting spell. Please try again.');
        }
    }
    
    selectWord(word, type) {
        if (type === 'modifier') {
            this.selectedModifier = this.selectedModifier === word ? null : word;
        } else if (type === 'core') {
            this.selectedCore = this.selectedCore === word ? null : word;
        } else if (type === 'shape') {
            this.selectedShape = this.selectedShape === word ? null : word;
        }
        
        this.updateSpellDisplay();
        this.updateWordButtons();
        this.previewSpell();
    }
    
    updateSpellDisplay() {
        const modifier = this.selectedModifier || '[Modifier]';
        const core = this.selectedCore || '[Core]';
        const shape = this.selectedShape || '[Shape]';
        
        document.getElementById('spellDisplay').textContent = `${modifier} + ${core} + ${shape}`;
    }
    
    updateWordButtons() {
        // Update modifier buttons
        document.querySelectorAll('#modifierButtons .word-btn').forEach(btn => {
            if (btn.textContent === this.selectedModifier) {
                btn.classList.add('selected');
            } else {
                btn.classList.remove('selected');
            }
        });
        
        // Update core buttons
        document.querySelectorAll('#coreButtons .word-btn').forEach(btn => {
            if (btn.textContent === this.selectedCore) {
                btn.classList.add('selected');
            } else {
                btn.classList.remove('selected');
            }
        });
        
        // Update shape buttons
        document.querySelectorAll('#shapeButtons .word-btn').forEach(btn => {
            if (btn.textContent === this.selectedShape) {
                btn.classList.add('selected');
            } else {
                btn.classList.remove('selected');
            }
        });
    }
    
    resetSelections() {
        this.selectedModifier = null;
        this.selectedCore = null;
        this.selectedShape = null;
        this.updateSpellDisplay();
        this.updateWordButtons();
    }
    
    updateDisplay() {
        if (!this.gameState) return;
        
        const player = this.gameState.player;
        const enemy = this.gameState.enemy;
        
        // Update player stats
        this.updateBar('playerHpBar', 'playerHpText', player.hp, player.max_hp);
        this.updateBar('playerManaBar', 'playerManaText', player.mana, player.max_mana);
        this.updateStatus('playerStatus', player.status_effects);
        
        // Update enemy stats
        document.getElementById('enemyName').textContent = enemy.name;
        this.updateBar('enemyHpBar', 'enemyHpText', enemy.hp, enemy.max_hp);
        this.updateBar('enemyManaBar', 'enemyManaText', enemy.mana, enemy.max_mana);
        this.updateStatus('enemyStatus', enemy.status_effects);
        
        // Update word buttons
        this.createWordButtons();
        
        // Update log
        this.updateLog();
        
        // Update cast button
        const castBtn = document.getElementById('castBtn');
        if (this.gameState.game_over) {
            castBtn.disabled = true;
            castBtn.textContent = 'GAME OVER';
        } else {
            castBtn.disabled = false;
            castBtn.textContent = 'CAST SPELL';
        }
    }
    
    updateBar(barId, textId, current, max) {
        const bar = document.getElementById(barId);
        const text = document.getElementById(textId);
        const percentage = (current / max) * 100;
        
        bar.style.width = percentage + '%';
        text.textContent = `${Math.floor(current)}/${Math.floor(max)}`;
    }
    
    updateStatus(statusId, effects) {
        const statusEl = document.getElementById(statusId);
        const statusText = effects && effects.length > 0 ? effects.join(', ') : 'None';
        statusEl.innerHTML = `<strong>Status:</strong> <span>${statusText}</span>`;
    }
    
    createWordButtons() {
        if (!this.gameState) return;
        
        const hand = this.gameState.hand;
        
        // Create modifier buttons
        const modifierContainer = document.getElementById('modifierButtons');
        modifierContainer.innerHTML = '';
        hand.modifiers.forEach(word => {
            const btn = document.createElement('button');
            btn.className = 'word-btn modifier';
            btn.textContent = word;
            btn.addEventListener('click', () => this.selectWord(word, 'modifier'));
            modifierContainer.appendChild(btn);
        });
        
        // Create core buttons
        const coreContainer = document.getElementById('coreButtons');
        coreContainer.innerHTML = '';
        hand.cores.forEach(word => {
            const btn = document.createElement('button');
            btn.className = 'word-btn core';
            btn.textContent = word;
            btn.addEventListener('click', () => this.selectWord(word, 'core'));
            coreContainer.appendChild(btn);
        });
        
        // Create shape buttons
        const shapeContainer = document.getElementById('shapeButtons');
        shapeContainer.innerHTML = '';
        hand.shapes.forEach(word => {
            const btn = document.createElement('button');
            btn.className = 'word-btn shape';
            btn.textContent = word;
            btn.addEventListener('click', () => this.selectWord(word, 'shape'));
            shapeContainer.appendChild(btn);
        });
        
        this.updateWordButtons();
    }
    
    updateLog() {
        if (!this.gameState || !this.gameState.log) return;
        
        const logContent = document.getElementById('logContent');
        logContent.innerHTML = '';
        
        this.gameState.log.forEach(message => {
            const logMsg = document.createElement('div');
            logMsg.className = 'log-message';
            
            if (message.includes('Turn')) {
                logMsg.classList.add('log-turn');
            } else if (message.includes('VICTORY')) {
                logMsg.classList.add('log-victory');
            } else if (message.includes('DEFEAT')) {
                logMsg.classList.add('log-defeat');
            }
            
            logMsg.textContent = message;
            logContent.appendChild(logMsg);
        });
        
        // Scroll to bottom
        logContent.scrollTop = logContent.scrollHeight;
    }
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.game = new BabelGame();
});
