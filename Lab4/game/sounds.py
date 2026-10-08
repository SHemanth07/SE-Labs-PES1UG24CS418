import array
import math
import pygame

SAMPLE_RATE = 44100


def _tone(freqs, ms, volume=0.4, square=False):
    """Build a pygame Sound from a sequence of frequencies (one per equal slice).

    Sounds are synthesised in code, so no audio asset files are needed.
    """
    # pygame.init() may already have opened the mixer (often in stereo), so
    # build the buffer to match whatever format is actually in use.
    rate, _fmt, channels = pygame.mixer.get_init()
    samples = array.array("h")
    per_note = int(rate * ms / 1000 / len(freqs))
    for f in freqs:
        for i in range(per_note):
            wave = math.sin(2 * math.pi * f * i / rate)
            if square:
                wave = 1.0 if wave >= 0 else -1.0
            fade = 1.0 - i / per_note  # fade out to avoid clicks
            value = int(32767 * volume * fade * wave)
            samples.extend([value] * channels)  # same sample on every channel
    return pygame.mixer.Sound(buffer=samples.tobytes())


class SoundManager:
    """Plays hit / miss / game-over effects. Fails silently if no audio device."""

    def __init__(self):
        self.enabled = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(SAMPLE_RATE, -16, 1, 512)
            self.hit = _tone([880, 1320], 120)                     # bright rising "ding"
            self.miss = _tone([180], 180, volume=0.35, square=True)  # low buzz
            self.game_over = _tone([660, 520, 400, 260], 700)       # descending jingle
            self.enabled = True
        except pygame.error:
            pass  # no audio device: game still runs, just silently

    def play(self, name):
        if self.enabled:
            getattr(self, name).play()
