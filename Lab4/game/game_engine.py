import pygame
import random
from .target import Target
from .sounds import SoundManager

# Game Engine

WHITE = (255, 255, 255)
RED = (220, 60, 60)
GRAY = (150, 150, 160)
PANEL = (60, 60, 70)

# Difficulty presets: (base_radius, min_radius, lifespan_frames at 60 FPS)
DIFFICULTIES = {
    "Easy":   {"base_radius": 50, "min_radius": 18, "lifespan_frames": 120},
    "Medium": {"base_radius": 40, "min_radius": 12, "lifespan_frames": 90},
    "Hard":   {"base_radius": 28, "min_radius": 8,  "lifespan_frames": 60},
}

# Game states
PLAYING = "playing"
GAME_OVER = "game_over"
MENU = "menu"


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.margin = 60
        self.hud_height = 60
        self.round_seconds = 30

        self.font = pygame.font.SysFont("Arial", 26)
        self.big_font = pygame.font.SysFont("Arial", 56, bold=True)
        self.quit_requested = False
        self.sounds = SoundManager()

        self.difficulty = "Medium"
        self.menu_buttons = {}
        self.start_round(self.difficulty)

    # ---------- round lifecycle ----------
    def start_round(self, difficulty):
        """Reset all round state and begin a new round at the given difficulty."""
        self.difficulty = difficulty
        self.state = PLAYING
        self.time_left_frames = self.round_seconds * 60
        self.hits = 0
        self.misses = 0
        self.score = 0
        self.target = self._spawn_target()

    @property
    def game_over(self):
        return self.state == GAME_OVER

    def _spawn_target(self):
        x = random.randint(self.margin, self.width - self.margin)
        y = random.randint(self.margin + self.hud_height, self.height - self.margin)
        return Target(x, y, **DIFFICULTIES[self.difficulty])

    # ---------- input ----------
    def handle_event(self, event):
        if self.state == PLAYING:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(event.pos)

        elif self.state == GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                    self.state = MENU
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.quit_requested = True

        elif self.state == MENU:
            if event.type == pygame.KEYDOWN:
                keys = {pygame.K_1: "Easy", pygame.K_2: "Medium", pygame.K_3: "Hard"}
                if event.key in keys:
                    self.start_round(keys[event.key])
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.quit_requested = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for name, rect in self.menu_buttons.items():
                    if rect.collidepoint(event.pos):
                        if name == "Exit":
                            self.quit_requested = True
                        else:
                            self.start_round(name)

    def _handle_click(self, pos):
        x, y = pos
        if self.target.contains_point(x, y):
            self.hits += 1
            self.score += 1
            self.sounds.play("hit")
            self.target = self._spawn_target()
        else:
            self.misses += 1
            self.sounds.play("miss")

    def handle_input(self):
        # Reserved for continuously-held-key input; this game is
        # entirely mouse-driven, so there's nothing to poll here.
        pass

    # ---------- update ----------
    def update(self):
        if self.state != PLAYING:
            return

        self.time_left_frames -= 1
        if self.time_left_frames <= 0:
            self.state = GAME_OVER
            self.sounds.play("game_over")
            return

        self.target.update()
        if self.target.expired():
            self.misses += 1  # letting a target time out counts as a miss too
            self.sounds.play("miss")
            self.target = self._spawn_target()

    def accuracy(self):
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return round(100 * self.hits / total, 1)

    # ---------- rendering ----------
    def render(self, screen):
        if self.state == MENU:
            self._render_menu(screen)
            return

        r = int(self.target.visual_radius())
        pygame.draw.circle(screen, RED, (self.target.x, self.target.y), r)
        pygame.draw.circle(screen, WHITE, (self.target.x, self.target.y), r, 2)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        seconds_left = max(0, self.time_left_frames // 60)
        timer_text = self.font.render(f"Time: {seconds_left}s", True, WHITE)
        screen.blit(timer_text, (self.width - 140, 10))

        acc_text = self.font.render(f"Accuracy: {self.accuracy()}%", True, WHITE)
        screen.blit(acc_text, (self.width // 2 - 90, 10))

        if self.state == GAME_OVER:
            self._render_game_over(screen)

    def _centered(self, screen, font, text, y, color=WHITE):
        surf = font.render(text, True, color)
        screen.blit(surf, surf.get_rect(center=(self.width // 2, y)))

    def _render_game_over(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        cy = self.height // 2
        self._centered(screen, self.big_font, "GAME OVER", cy - 130)
        self._centered(screen, self.font, f"Final Score: {self.score}", cy - 60)
        self._centered(screen, self.font, f"Accuracy: {self.accuracy()}%", cy - 20)
        self._centered(screen, self.font,
                       f"Hits: {self.hits}   Misses: {self.misses}", cy + 20)
        self._centered(screen, self.font, "Press R to play again", cy + 80)
        self._centered(screen, self.font, "Press ESC or Q to quit", cy + 115, GRAY)

    def _render_menu(self, screen):
        self._centered(screen, self.big_font, "Select Difficulty", 90)

        self.menu_buttons = {}
        labels = [("Easy", "1"), ("Medium", "2"), ("Hard", "3"), ("Exit", "Esc")]
        bw, bh, gap = 300, 52, 18
        top = 170
        mouse = pygame.mouse.get_pos()
        for i, (name, key) in enumerate(labels):
            rect = pygame.Rect(0, 0, bw, bh)
            rect.centerx = self.width // 2
            rect.y = top + i * (bh + gap)
            self.menu_buttons[name] = rect
            color = (90, 90, 105) if rect.collidepoint(mouse) else PANEL
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
            self._centered(screen, self.font, f"{name}  [{key}]", rect.centery)
