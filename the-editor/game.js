// 게임 상태
const GAME_STATES = {
    START_SCREEN: 'START_SCREEN',
    INTRO_NARRATIVE: 'INTRO_NARRATIVE',
    CHAPTER_EXPLORE: 'CHAPTER_EXPLORE',
    CHAPTER_COMBAT: 'CHAPTER_COMBAT',
    CHAPTER_PUZZLE: 'CHAPTER_PUZZLE',
    ENDING_CRAFTING: 'ENDING_CRAFTING',
    GAME_OVER: 'GAME_OVER',
    SUCCESS: 'SUCCESS'
};

// 챕터 데이터
const CHAPTERS = [
    {
        id: 1,
        title: '명사의 숲',
        subtitle: 'The Forest of Nouns',
        situation: '희미한 [안개] 숲. 이름 없는 [나무]가 길을 막고 있다. [돌]이 발밑에 굴러다닌다. [나]는 길을 잃었다.',
        mineableWords: ['안개', '나무', '돌', '나'],
        enemy: {
            name: '형체 없는 그림자',
            hp: 30,
            maxHp: 30,
            attack: 5,
            description: '텍스트의 의미를 잃어버린 존재'
        },
        type: 'explore'
    },
    {
        id: 2,
        title: '동사의 탑',
        subtitle: 'The Tower of Verbs',
        situation: '거대한 탑이 하늘을 [찌르다]. 적들이 우리를 [추격하다]. [막다]로 방어하고, [부수다]로 공격하라. [달리다]로 도망칠 수도 있다.',
        mineableWords: ['찌르다', '추격하다', '막다', '부수다', '달리다'],
        enemy: {
            name: '검열관',
            hp: 50,
            maxHp: 50,
            attack: 8,
            description: '모든 동사를 통제하려는 자'
        },
        type: 'combat'
    },
    {
        id: 3,
        title: '형용사의 바다',
        subtitle: 'The Sea of Adjectives',
        situation: '[우울한] 파도가 친다. 바다는 [끝없는] 깊이를 가졌다. [차가운] 바람이 불어온다. [거대한] 고래가 나타났다. [신성한] 빛이 내려온다.',
        mineableWords: ['우울한', '끝없는', '차가운', '거대한', '신성한'],
        puzzle: {
            text: '파도가 [거칠게] 몰아친다',
            target: '거칠게',
            solutions: [
                { word: '잠잠하게', type: 'peaceful' },
                { word: '얼어붙은', type: 'frozen' },
                { word: '따뜻하게', type: 'warm' }
            ]
        },
        type: 'puzzle'
    }
];

// 단어 태그 시스템
const WORD_TAGS = {
    // 명사
    '나': { type: 'noun', element: 'self', cost: 2, category: 'subject' },
    '안개': { type: 'noun', element: 'mist', cost: 3, category: 'subject' },
    '나무': { type: 'noun', element: 'wood', cost: 3, category: 'subject' },
    '돌': { type: 'noun', element: 'earth', cost: 2, category: 'subject' },
    
    // 동사
    '찌르다': { type: 'verb', action: 'attack', power: 8, cost: 5, category: 'verb' },
    '추격하다': { type: 'verb', action: 'chase', power: 3, cost: 4, category: 'verb' },
    '막다': { type: 'verb', action: 'defend', shield: 10, cost: 4, category: 'verb' },
    '부수다': { type: 'verb', action: 'attack', power: 12, cost: 6, category: 'verb' },
    '달리다': { type: 'verb', action: 'dodge', shield: 5, cost: 3, category: 'verb' },
    '던지다': { type: 'verb', action: 'attack', power: 6, cost: 4, category: 'verb' },
    
    // 형용사
    '우울한': { type: 'adjective', mood: 'sad', value: -1, cost: 2, category: 'modifier' },
    '끝없는': { type: 'adjective', mood: 'abstract', value: 0, cost: 3, category: 'modifier' },
    '차가운': { type: 'adjective', element: 'ice', value: 0, cost: 2, category: 'modifier' },
    '거대한': { type: 'adjective', size: 'large', value: 1, cost: 3, category: 'modifier' },
    '신성한': { type: 'adjective', mood: 'holy', value: 2, cost: 4, category: 'modifier' },
    '거칠게': { type: 'adjective', mood: 'chaos', value: -1, cost: 2, category: 'modifier' },
    '잠잠하게': { type: 'adjective', mood: 'peaceful', value: 1, cost: 2, category: 'modifier' },
    '얼어붙은': { type: 'adjective', element: 'ice', value: 0, cost: 3, category: 'modifier' },
    '따뜻하게': { type: 'adjective', mood: 'warm', value: 1, cost: 2, category: 'modifier' }
};

// 엔딩 템플릿
const ENDING_TEMPLATES = {
    happy: {
        title: '희망의 결말',
        text: '세상은 {word1} 하고, 사람들은 {word2} 하며, 이야기는 {word3} 끝났다. 모든 것이 평화롭게 이어졌다.',
        threshold: 3
    },
    sad: {
        title: '슬픈 결말',
        text: '세상은 {word1} 하고, 사람들은 {word2} 하며, 이야기는 {word3} 끝났다. 하지만 희망은 남아있었다.',
        threshold: -2
    },
    abstract: {
        title: '모호한 결말',
        text: '세상은 {word1} 하고, 사람들은 {word2} 하며, 이야기는 {word3} 끝났다. 의미는 각자에게 달려있었다.',
        threshold: -1
    }
};

// 게임 상태 관리
class GameState {
    constructor() {
        this.currentState = GAME_STATES.START_SCREEN;
        this.currentChapter = 0;
        this.playerDeck = [];
        this.playerHand = [];
        this.playerHp = 100;
        this.playerMaxHp = 100;
        this.ink = 20;
        this.maxInk = 20;
        this.enemyHp = 0;
        this.enemyMaxHp = 0;
        this.combatSlots = { subject: null, verb: null, modifier: null };
        this.endingWords = [];
        this.endingScore = 0;
        this.endingType = 'abstract';
        this.puzzleSolved = false;
    }

    changeState(newState) {
        this.currentState = newState;
        this.updateScreen();
    }

    updateScreen() {
        // 모든 화면 숨기기
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });

        // 현재 화면 표시
        const screenMap = {
            [GAME_STATES.START_SCREEN]: 'start-screen',
            [GAME_STATES.INTRO_NARRATIVE]: 'intro-screen',
            [GAME_STATES.CHAPTER_EXPLORE]: 'explore-screen',
            [GAME_STATES.CHAPTER_COMBAT]: 'combat-screen',
            [GAME_STATES.CHAPTER_PUZZLE]: 'puzzle-screen',
            [GAME_STATES.ENDING_CRAFTING]: 'ending-screen',
            [GAME_STATES.SUCCESS]: 'success-screen',
            [GAME_STATES.GAME_OVER]: 'gameover-screen'
        };

        const screenId = screenMap[this.currentState];
        if (screenId) {
            document.getElementById(screenId).classList.add('active');
        }
    }

    drawHand() {
        // 덱에서 무작위로 5-7개를 손패로 가져오기
        const handSize = Math.min(7, this.playerDeck.length);
        const shuffled = [...this.playerDeck].sort(() => Math.random() - 0.5);
        this.playerHand = shuffled.slice(0, handSize);
    }

    reset() {
        this.currentState = GAME_STATES.START_SCREEN;
        this.currentChapter = 0;
        this.playerDeck = [];
        this.playerHand = [];
        this.playerHp = 100;
        this.playerMaxHp = 100;
        this.ink = 20;
        this.maxInk = 20;
        this.enemyHp = 0;
        this.enemyMaxHp = 0;
        this.combatSlots = { subject: null, verb: null, modifier: null };
        this.endingWords = [];
        this.endingScore = 0;
        this.endingType = 'abstract';
        this.puzzleSolved = false;
    }
}

// 게임 인스턴스
const game = new GameState();

// 유틸리티 함수
function typewriterEffect(element, text, speed = 50, callback) {
    let index = 0;
    element.textContent = '';
    
    function type() {
        if (index < text.length) {
            element.textContent += text[index];
            index++;
            setTimeout(type, speed);
        } else if (callback) {
            callback();
        }
    }
    
    type();
}

function parseSituationText(text) {
    const parts = [];
    const regex = /\[([^\]]+)\]/g;
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(text)) !== null) {
        if (match.index > lastIndex) {
            parts.push({
                type: 'text',
                content: text.substring(lastIndex, match.index)
            });
        }
        parts.push({
            type: 'word',
            content: match[1],
            fullMatch: match[0]
        });
        lastIndex = regex.lastIndex;
    }

    if (lastIndex < text.length) {
        parts.push({
            type: 'text',
            content: text.substring(lastIndex)
        });
    }

    return parts;
}

function updateBars() {
    // HP 바
    const hpPercent = (game.playerHp / game.playerMaxHp) * 100;
    document.getElementById('hp-bar').style.width = hpPercent + '%';
    document.getElementById('hp-text').textContent = `${game.playerHp}/${game.playerMaxHp}`;
    document.getElementById('combat-hp-bar').style.width = hpPercent + '%';
    document.getElementById('combat-hp-text').textContent = `${game.playerHp}/${game.playerMaxHp}`;

    // 잉크 바
    const inkPercent = (game.ink / game.maxInk) * 100;
    document.getElementById('ink-bar').style.width = inkPercent + '%';
    document.getElementById('ink-text').textContent = `${game.ink}/${game.maxInk}`;
    document.getElementById('combat-ink-bar').style.width = inkPercent + '%';
    document.getElementById('combat-ink-text').textContent = `${game.ink}/${game.maxInk}`;

    // 적 HP 바
    if (game.enemyMaxHp > 0) {
        const enemyPercent = (game.enemyHp / game.enemyMaxHp) * 100;
        document.getElementById('enemy-hp-bar').style.width = enemyPercent + '%';
        document.getElementById('enemy-hp-text').textContent = `${game.enemyHp}/${game.enemyMaxHp}`;
    }
}

function updateDeckDisplay() {
    const deckDisplay = document.getElementById('deck-display');
    deckDisplay.innerHTML = '';
    
    if (game.playerDeck.length === 0) {
        deckDisplay.innerHTML = '<p style="color: #999;">아직 수집한 단어가 없습니다</p>';
    } else {
        game.playerDeck.forEach(word => {
            const tag = document.createElement('span');
            tag.className = 'word-tag';
            tag.textContent = word;
            deckDisplay.appendChild(tag);
        });
    }
}

// 화면 렌더링 함수들
function renderStartScreen() {
    // 이미 HTML에 있음
}

function renderIntroScreen() {
    const introText = document.getElementById('intro-text');
    const continueBtn = document.getElementById('intro-continue-btn');
    
    const narrative = `모든 것이 백지화되었다...

당신은 에디터(Editor)입니다. 텍스트를 수정하고, 단어를 조합하여 이야기를 바꿀 수 있는 존재입니다.

하지만 세상이 백지화되었습니다. 모든 의미가 사라지고, 단어들이 흩어졌습니다.

당신의 임무는 세 개의 챕터를 통과하여 단어를 모으고, 마지막에 이야기의 결말을 짓는 것입니다.

게임 방법:
• 대괄호 [ ] 안의 단어를 클릭하여 수집하세요
• 전투에서는 주어, 동사, 수식어를 조합하여 공격하세요
• 퍼즐에서는 적절한 단어로 문맥을 수정하세요
• 마지막에 모은 단어로 결말을 완성하세요`;

    typewriterEffect(introText, narrative, 30, () => {
        continueBtn.style.display = 'block';
    });
}

function renderExploreScreen() {
    const chapter = CHAPTERS[game.currentChapter];
    
    document.getElementById('chapter-title').textContent = chapter.title;
    document.getElementById('chapter-subtitle').textContent = chapter.subtitle;
    
    const situationText = document.getElementById('situation-text');
    situationText.innerHTML = '';
    
    const parts = parseSituationText(chapter.situation);
    parts.forEach(part => {
        if (part.type === 'word') {
            const btn = document.createElement('button');
            btn.className = 'word-button';
            btn.textContent = part.fullMatch;
            btn.onclick = () => mineWord(part.content);
            situationText.appendChild(btn);
        } else {
            const span = document.createElement('span');
            span.textContent = part.content;
            situationText.appendChild(span);
        }
    });
    
    updateDeckDisplay();
    updateBars();
}

function mineWord(word) {
    if (game.playerDeck.includes(word)) {
        return; // 이미 수집함
    }
    
    // 애니메이션 효과
    const buttons = document.querySelectorAll('.word-button');
    buttons.forEach(btn => {
        if (btn.textContent.includes(word)) {
            btn.classList.add('extracting');
            setTimeout(() => {
                btn.remove();
            }, 500);
        }
    });
    
    game.playerDeck.push(word);
    updateDeckDisplay();
}

function renderCombatScreen() {
    const chapter = CHAPTERS[game.currentChapter];
    
    document.getElementById('combat-chapter-title').textContent = `${chapter.title} - 전투`;
    document.getElementById('enemy-name').textContent = chapter.enemy.name;
    document.getElementById('enemy-desc').textContent = chapter.enemy.description;
    
    game.enemyHp = chapter.enemy.maxHp;
    game.enemyMaxHp = chapter.enemy.maxHp;
    game.drawHand();
    
    updateCombatDisplay();
    updateBars();
}

function updateCombatDisplay() {
    // 슬롯 업데이트
    document.getElementById('slot-subject').textContent = game.combatSlots.subject || '비어있음';
    document.getElementById('slot-subject').className = game.combatSlots.subject ? 'slot-content filled' : 'slot-content';
    
    document.getElementById('slot-verb').textContent = game.combatSlots.verb || '비어있음';
    document.getElementById('slot-verb').className = game.combatSlots.verb ? 'slot-content filled' : 'slot-content';
    
    document.getElementById('slot-modifier').textContent = game.combatSlots.modifier || '선택사항';
    document.getElementById('slot-modifier').className = game.combatSlots.modifier ? 'slot-content filled' : 'slot-content';
    
    // 손패 표시
    const handDisplay = document.getElementById('hand-display');
    handDisplay.innerHTML = '';
    
    game.playerHand.forEach(word => {
        const tag = WORD_TAGS[word];
        if (!tag) return;
        
        const btn = document.createElement('button');
        btn.className = `hand-word ${tag.type}`;
        btn.textContent = word;
        
        // 선택 상태 확인
        const isSelected = 
            (tag.category === 'subject' && game.combatSlots.subject === word) ||
            (tag.category === 'verb' && game.combatSlots.verb === word) ||
            (tag.category === 'modifier' && game.combatSlots.modifier === word);
        
        if (isSelected) {
            btn.classList.add('selected');
        }
        
        btn.onclick = () => selectCombatWord(word, tag);
        handDisplay.appendChild(btn);
    });
    
    // 액션 미리보기
    const action = calculateCombatAction();
    const preview = document.getElementById('action-preview');
    const executeBtn = document.getElementById('execute-btn');
    
    if (action && game.combatSlots.subject && game.combatSlots.verb) {
        preview.innerHTML = `
            <p><strong>예상 효과:</strong></p>
            <p>${action.description}</p>
            ${action.damage > 0 ? `<p style="color: #c0392b;">데미지: ${action.damage}</p>` : ''}
            ${action.shield > 0 ? `<p style="color: #2980b9;">방어: ${action.shield}</p>` : ''}
            <p style="color: #666;">잉크 소모: ${action.cost}</p>
        `;
        preview.classList.add('show');
        executeBtn.disabled = game.ink < action.cost || game.enemyHp <= 0;
    } else {
        preview.classList.remove('show');
        executeBtn.disabled = true;
    }
}

function selectCombatWord(word, tag) {
    if (tag.category === 'subject') {
        if (game.combatSlots.subject === word) {
            game.combatSlots.subject = null;
        } else {
            game.combatSlots.subject = word;
        }
    } else if (tag.category === 'verb') {
        if (game.combatSlots.verb === word) {
            game.combatSlots.verb = null;
        } else {
            game.combatSlots.verb = word;
        }
    } else if (tag.category === 'modifier') {
        if (game.combatSlots.modifier === word) {
            game.combatSlots.modifier = null;
        } else {
            game.combatSlots.modifier = word;
        }
    }
    
    updateCombatDisplay();
}

function calculateCombatAction() {
    const { subject, verb, modifier } = game.combatSlots;
    if (!subject || !verb) return null;

    const subjectTag = WORD_TAGS[subject] || {};
    const verbTag = WORD_TAGS[verb] || {};
    const modifierTag = modifier ? (WORD_TAGS[modifier] || {}) : {};

    let damage = 0;
    let shield = 0;
    let description = '';
    let cost = (subjectTag.cost || 0) + (verbTag.cost || 0) + (modifierTag.cost || 0);

    if (verbTag.action === 'attack') {
        damage = verbTag.power || 5;
        if (subjectTag.element === 'wood' && modifierTag.element === 'ice') {
            damage += 3;
            description = `${subject}에서 ${verb}하는 얼음 공격!`;
        } else if (subjectTag.element === 'earth') {
            damage += 2;
            description = `${subject}로 ${verb}하는 대지의 힘!`;
        } else if (modifierTag.size === 'large') {
            damage += 5;
            description = `${modifier} ${subject}로 ${verb}!`;
        } else {
            description = `${subject}로 ${verb}!`;
        }
    } else if (verbTag.action === 'defend') {
        shield = verbTag.shield || 10;
        if (modifierTag.size === 'large') shield += 5;
        description = `${subject}로 ${verb}하는 방어!`;
    } else if (verbTag.action === 'dodge') {
        shield = 5;
        description = `${verb}로 회피!`;
    }

    return { damage, shield, description, cost };
}

function executeCombat() {
    const action = calculateCombatAction();
    if (!action) return;

    if (game.ink < action.cost) {
        alert('잉크가 부족합니다!');
        return;
    }

    game.ink -= action.cost;

    if (action.damage > 0) {
        game.enemyHp = Math.max(0, game.enemyHp - action.damage);
    }

    // 적 공격
    if (game.enemyHp > 0) {
        const chapter = CHAPTERS[game.currentChapter];
        const enemyAttack = chapter.enemy.attack;
        game.playerHp = Math.max(0, game.playerHp - enemyAttack);
        
        // 백지화 효과
        document.body.classList.add('whiteout');
        setTimeout(() => {
            document.body.classList.remove('whiteout');
        }, 300);
    }

    updateBars();
    updateCombatDisplay();

    // 전투 승리 체크
    if (game.enemyHp <= 0) {
        setTimeout(() => {
            if (game.currentChapter < CHAPTERS.length - 1) {
                game.currentChapter++;
                game.ink = game.maxInk;
                game.combatSlots = { subject: null, verb: null, modifier: null };
                game.changeState(GAME_STATES.CHAPTER_EXPLORE);
            } else {
                game.changeState(GAME_STATES.ENDING_CRAFTING);
            }
        }, 1500);
    }

    // 게임 오버 체크
    if (game.playerHp <= 0) {
        setTimeout(() => {
            game.changeState(GAME_STATES.GAME_OVER);
        }, 1000);
    }
}

function renderPuzzleScreen() {
    const chapter = CHAPTERS[game.currentChapter];
    
    document.getElementById('puzzle-chapter-title').textContent = `${chapter.title} - 퍼즐`;
    
    const puzzleText = document.getElementById('puzzle-text');
    const puzzle = chapter.puzzle;
    
    puzzleText.innerHTML = puzzle.text.split('[').map((part, idx) => {
        if (part.includes(']')) {
            const [word, rest] = part.split(']');
            if (game.puzzleSolved) {
                return `<span style="padding: 5px 10px; background: #c8e6c9; border-radius: 3px;">${word}</span>${rest}`;
            } else {
                return `<span style="padding: 5px 10px; background: #FFD700; border-radius: 3px;">[${word}]</span>${rest}`;
            }
        }
        return part;
    }).join('');
    
    const solutionsDiv = document.getElementById('puzzle-solutions');
    solutionsDiv.innerHTML = '';
    
    if (!game.puzzleSolved) {
        puzzle.solutions.forEach(solution => {
            const div = document.createElement('div');
            div.className = 'puzzle-solution';
            if (!game.playerDeck.includes(solution.word)) {
                div.classList.add('disabled');
            }
            div.innerHTML = `
                <strong>${solution.word}</strong>
                ${!game.playerDeck.includes(solution.word) ? '<span style="color: #999;"> (수집 필요)</span>' : ''}
            `;
            div.onclick = () => {
                if (game.playerDeck.includes(solution.word)) {
                    solvePuzzle(solution.word);
                }
            };
            solutionsDiv.appendChild(div);
        });
    } else {
        const resultDiv = document.getElementById('puzzle-result');
        resultDiv.style.display = 'block';
        resultDiv.textContent = '퍼즐 해결! 문맥이 바뀌었습니다.';
        
        setTimeout(() => {
            game.changeState(GAME_STATES.ENDING_CRAFTING);
        }, 2000);
    }
}

function solvePuzzle(solutionWord) {
    if (game.playerDeck.includes(solutionWord)) {
        game.puzzleSolved = true;
        renderPuzzleScreen();
    }
}

function renderEndingScreen() {
    const endingSentence = document.getElementById('ending-sentence');
    endingSentence.innerHTML = `
        <p>세상은 <span class="ending-word-slot ${game.endingWords[0] ? '' : 'empty'}">${game.endingWords[0] || '____'}</span> 하고,</p>
        <p>사람들은 <span class="ending-word-slot ${game.endingWords[1] ? '' : 'empty'}">${game.endingWords[1] || '____'}</span> 하며,</p>
        <p>이야기는 <span class="ending-word-slot ${game.endingWords[2] ? '' : 'empty'}">${game.endingWords[2] || '____'}</span> 끝났다.</p>
    `;
    
    const wordsDiv = document.getElementById('ending-words');
    wordsDiv.innerHTML = '';
    
    const availableWords = game.playerDeck.filter(word => {
        const tag = WORD_TAGS[word];
        return tag && tag.type === 'adjective';
    });
    
    availableWords.forEach(word => {
        const btn = document.createElement('button');
        btn.className = 'ending-word-btn';
        if (game.endingWords.includes(word)) {
            btn.classList.add('selected');
        }
        btn.textContent = word;
        btn.onclick = () => {
            if (game.endingWords.includes(word)) {
                game.endingWords = game.endingWords.filter(w => w !== word);
            } else if (game.endingWords.length < 3) {
                game.endingWords.push(word);
            }
            renderEndingScreen();
        };
        wordsDiv.appendChild(btn);
    });
    
    const craftBtn = document.getElementById('craft-ending-btn');
    craftBtn.disabled = game.endingWords.length < 3;
}

function craftEnding() {
    if (game.endingWords.length < 3) return;
    
    // 점수 계산
    let score = 0;
    game.endingWords.forEach(word => {
        const tag = WORD_TAGS[word];
        if (tag) {
            score += tag.value || 0;
        }
    });
    
    game.endingScore = score;
    
    // 엔딩 타입 결정
    if (score >= ENDING_TEMPLATES.happy.threshold) {
        game.endingType = 'happy';
    } else if (score <= ENDING_TEMPLATES.sad.threshold) {
        game.endingType = 'sad';
    } else {
        game.endingType = 'abstract';
    }
    
    game.changeState(GAME_STATES.SUCCESS);
    renderSuccessScreen();
}

function renderSuccessScreen() {
    const ending = ENDING_TEMPLATES[game.endingType];
    const finalText = ending.text
        .replace('{word1}', game.endingWords[0] || '')
        .replace('{word2}', game.endingWords[1] || '')
        .replace('{word3}', game.endingWords[2] || '');
    
    document.getElementById('ending-title').textContent = ending.title;
    document.getElementById('ending-text').textContent = finalText;
    document.getElementById('ending-score').textContent = `점수: ${game.endingScore}`;
}

function renderGameOverScreen() {
    // 이미 HTML에 있음
}

// 이벤트 리스너
document.addEventListener('DOMContentLoaded', () => {
    // 시작 버튼
    document.getElementById('start-btn').onclick = () => {
        game.changeState(GAME_STATES.INTRO_NARRATIVE);
        renderIntroScreen();
    };
    
    // 인트로 계속하기
    document.getElementById('intro-continue-btn').onclick = () => {
        game.currentChapter = 0;
        game.changeState(GAME_STATES.CHAPTER_EXPLORE);
        renderExploreScreen();
    };
    
    // 탐험 계속하기
    document.getElementById('explore-continue-btn').onclick = () => {
        const chapter = CHAPTERS[game.currentChapter];
        if (chapter.type === 'puzzle') {
            game.changeState(GAME_STATES.CHAPTER_PUZZLE);
            renderPuzzleScreen();
        } else {
            game.changeState(GAME_STATES.CHAPTER_COMBAT);
            renderCombatScreen();
        }
    };
    
    // 전투 실행
    document.getElementById('execute-btn').onclick = executeCombat;
    
    // 엔딩 완성
    document.getElementById('craft-ending-btn').onclick = craftEnding;
    
    // 재시작 버튼들
    document.getElementById('restart-btn').onclick = () => {
        game.reset();
        game.updateScreen();
    };
    
    document.getElementById('restart-gameover-btn').onclick = () => {
        game.reset();
        game.updateScreen();
    };
    
    // 초기 화면 표시
    game.updateScreen();
});
