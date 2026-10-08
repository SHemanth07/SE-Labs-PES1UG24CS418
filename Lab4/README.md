# 🎯 Target Aim Trainer

A fast-paced aim trainer built with **Python and Pygame**. Click the targets before they shrink away, keep your accuracy high, and beat your score in a 30-second round across three difficulty levels.

> Lab 4 (VibeCoding) submission, Repo #47
> **Student:** S. Hemanth Kumar Reddy &nbsp;|&nbsp; **SRN:** PES1UG24CS418 &nbsp;|&nbsp; **Section:** 5G
> Built on the starter project from [SETAPESU26/47_target-aim-trainer](https://github.com/SETAPESU26/47_target-aim-trainer)

---

## 🎮 How to Play

- A red target appears at a random spot and **shrinks** the longer it stays on screen.
- **Click the target** to score a hit; a new one spawns immediately.
- **Click anywhere else**, or let a target shrink away completely, and it counts as a **miss**.
- You have **30 seconds**. Your score, accuracy and remaining time are always shown at the top.
- When time runs out, the Game Over screen shows your results.

### Controls

| Screen | Input | Action |
|---|---|---|
| Playing | Left mouse click | Shoot |
| Game Over | `R` (or Enter / Space) | Open the difficulty menu |
| Game Over | `Esc` or `Q` | Quit |
| Difficulty menu | Click a button, or `1` / `2` / `3` | Start Easy / Medium / Hard |
| Difficulty menu | Exit button or `Esc` | Quit |

### Difficulty Levels

| Level | Target size | Smallest size | Time before it expires |
|---|---|---|---|
| Easy | 50 px | 18 px | 2.0 s |
| Medium (default) | 40 px | 12 px | 1.5 s |
| Hard | 28 px | 8 px | 1.0 s |

---

## ⚙️ Installation and Running

Requires **Python 3.10+**.

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>/Lab-4
pip install -r requirements.txt
python main.py
```

Sound is optional. If no audio device is found, the game runs silently.

---

## ✨ What Was Fixed and Added

Each change is its own commit in the repository history.

### 1. Bug fix: collision detection
**Problem:** The target visibly shrinks, but `Target.contains_point()` always tested against the original `base_radius`. A late click well outside the small drawn circle still counted as a hit.
**Fix:** Hit-testing now uses `visual_radius()`, so the clickable area is exactly what is drawn on screen.

### 2. Game Over screen
The console `print` was replaced with an on-screen panel over a dimmed playfield. It shows the final score, accuracy, hits and misses, ignores stray clicks, and waits for the player's input.

### 3. Replay with difficulty selection
After Game Over, pressing `R` opens a menu with **Easy, Medium, Hard** and **Exit**. Difficulty changes the target's size and lifespan. Every new round fully resets the score, hits, misses and timer. The game is organised as a small state machine: `PLAYING → GAME_OVER → MENU → PLAYING`.

### 4. Sound feedback
Three effects are synthesised in code, so no audio files are needed:
- **Hit:** a bright, rising "ding"
- **Miss:** a low buzz, for both a wrong click and a timed-out target
- **Round end:** a descending jingle

The generator reads the mixer's actual channel count, so it works whether pygame opens stereo or mono.

---

## 🧠 How It Works

- **`Target`** stores its position and age. `visual_radius()` linearly shrinks the radius from `base_radius` to `min_radius` over its lifespan, and both drawing and hit-testing use this one value.
- **`GameEngine`** owns the round state (score, hits, misses, timer) and a `state` field that decides what `handle_event`, `update` and `render` do on each frame.
- **`SoundManager`** builds short waveforms with Python's `array` and `math` modules and plays them with `pygame.mixer`.
- **Accuracy** is `hits / (hits + misses) × 100`, where a timed-out target counts as a miss.

---

## 🛠️ Built With

- Python 3
- [Pygame](https://www.pygame.org/)
- An LLM pair-programming assistant ([Claude / ChatGPT / Gemini], whichever you used), with prompts and full history in `chat_history.pdf`

---
## 🐞 Bug Fixed and ✨ Features Added (Code Snippets)

### 🐞 Bug Fix: Collision detection (`game/target.py`)

The target shrinks on screen, but hit-testing still used the original full-size radius, so late clicks far from the small circle counted as hits.

**Before (buggy):**
```python
def contains_point(self, x, y):
    return math.hypot(self.x - x, self.y - y) <= self.base_radius
```

**After (fixed):**
```python
def contains_point(self, x, y):
    # Hit-testing uses the radius that is actually drawn on screen
    return math.hypot(self.x - x, self.y - y) <= self.visual_radius()
```

---

### ✨ Feature 1: Game Over screen (`game/game_engine.py`)

Replaces the console print with an on-screen panel showing the final score and accuracy.

```python
def _render_game_over(self, screen):
    overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))          # dim the playfield
    screen.blit(overlay, (0, 0))

    cy = self.height // 2
    self._centered(screen, self.big_font, "GAME OVER", cy - 130)
    self._centered(screen, self.font, f"Final Score: {self.score}", cy - 60)
    self._centered(screen, self.font, f"Accuracy: {self.accuracy()}%", cy - 20)
    self._centered(screen, self.font, f"Hits: {self.hits}   Misses: {self.misses}", cy + 20)
```

---

### ✨ Feature 2: Replay with difficulty selection (`game/game_engine.py`)

A state machine (`PLAYING → GAME_OVER → MENU → PLAYING`) with three difficulty presets and a full round reset.

```python
DIFFICULTIES = {
    "Easy":   {"base_radius": 50, "min_radius": 18, "lifespan_frames": 120},
    "Medium": {"base_radius": 40, "min_radius": 12, "lifespan_frames": 90},
    "Hard":   {"base_radius": 28, "min_radius": 8,  "lifespan_frames": 60},
}

def start_round(self, difficulty):
    self.difficulty = difficulty
    self.state = PLAYING
    self.time_left_frames = self.round_seconds * 60
    self.hits = self.misses = self.score = 0
    self.target = self._spawn_target()
```

```python
elif self.state == GAME_OVER:
    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
            self.state = MENU                      # open difficulty menu
        elif event.key in (pygame.K_ESCAPE, pygame.K_q):
            self.quit_requested = True
```

---

### ✨ Feature 3: Sound effects (`game/sounds.py` and `game/game_engine.py`)

Tones are generated in code, so no audio files are needed. The buffer matches the mixer's real channel count.

```python
rate, _fmt, channels = pygame.mixer.get_init()
...
value = int(32767 * volume * fade * wave)
samples.extend([value] * channels)       # same sample on every channel
```

```python
self.hit = _tone([880, 1320], 120)                       # bright rising ding
self.miss = _tone([180], 180, volume=0.35, square=True)  # low buzz
self.game_over = _tone([660, 520, 400, 260], 700)        # descending jingle
```

Playing the sounds from the game engine:
```python
if self.target.contains_point(x, y):
    self.hits += 1
    self.score += 1
    self.sounds.play("hit")
else:
    self.misses += 1
    self.sounds.play("miss")
```
