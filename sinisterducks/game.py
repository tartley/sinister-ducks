
from pyglet import clock

from .collision import Collision
from .enemy import Enemy
from .event import Event
from .stresstest import StressTest
from .feather import Feather
from .gameitem import GameItem
from .ground import Ground
from .hudgameover import HudGameOver
from .hudlives import HudLives
from .hudmessage import HudMessage
from .hudmultiplier import HudMultiplier
from .hudscore import HudScore
from .hudtitle import HudTitle
from .hudinstructions import HudInstructions
from .player import Player
from .sky import Sky
from .sounds import play
from .typebag import TypeBag
from .wavemessages import WAVE_MESSAGES
from .worlditem import WorldItem



class Game(object):

    def __init__(self, keystate, width, height):
        self.keystate = keystate
        self.width = width
        self.height = height
        self.wave = 0
        self._items = TypeBag()
        self.item_added = Event()
        self.item_removed = Event()
        self._to_be_added = []
        self.collision = Collision()
        GameItem.game = self


    def __iter__(self):
        return iter(self._items)


    def add(self, item):
        self._to_be_added.append(item)


    def _add(self, item):
        self._items.add(item)
        item.added()
        self.item_added(item)


    def remove(self, item=None, itemid=None):
        assert (item is None) ^ (itemid is None)
        if item is None:
            item = self._items[itemid]
        self._items.remove(item)

        item.removed()
        self.item_removed(item)


    def startup(self, win):
        self.add(Sky())
        self.add(Ground())
        self.add(StressTest())
        self.add(HudLives())
        self.add(HudScore())
        self.add(HudMultiplier())

        def update_and_refresh(win, dt):
            self.update(dt)
            win.invalid = True

        clock.schedule(lambda dt: update_and_refresh(win, dt))
        self.title()


    def title(self):
        self.add(HudTitle())


    def _remove_last_games_items(self):
        for itemtype in (Enemy, Feather):
            for item in self._items[itemtype]:
                item.remove_from_game = True


    def start(self):
        self._remove_last_games_items()

        self.wave = 0
        Player.start_game()
        self.add(HudInstructions())
        clock.schedule_once(lambda _: self.spawn_wave(), 2)


    def over(self):
        play('gameover')
        Player.multiplier = None
        self.add(HudGameOver())


    def spawn_wave(self):
        self.wave += 1
        self.add(HudMessage('Wave %d' % (self.wave,), remove_after=2))

        text = WAVE_MESSAGES[min(self.wave - 1, len(WAVE_MESSAGES) - 1)]
        hudmessage = HudMessage(
            text,
            y = self.height / 2 - 40,
            color = (255, 255, 255, 128),
            font_size = 16,
            remove_after=2)
        clock.schedule_once( lambda _: self.add( hudmessage ), 0.5)

        number = self.wave ** 2

        def _spawn(fast):
            clock.schedule_once(
                lambda _: Enemy.spawn(fast),
                1.5 + n * 0.25)

        for n in xrange(number):
            fast = n >= number + 2 - self.wave
            _spawn(fast)


    def wraparound(self, item):
        if item.x < -item.width / 2:
            item.x += self.width + item.width
        if item.x > self.width + item.width / 2:
            item.x -= self.width + item.width


    def update(self, dt):
        # scale dt such that 'standard' framerate of 60fps gives dt=1.0
        dt *= 60.0

        # don't attempt to compensate for framerate of less than 30fps. This
        # guards against huge explosion when game is paused for any reason
        # and then restarted
        dt = min(dt, 2)

        ids_to_remove = set()
        for item in self._items:
            item.update(dt)
            if item.remove_from_game:
                ids_to_remove.add(id(item))
            if isinstance(item, WorldItem):
                self.wraparound(item)

        for item in self._to_be_added:
            self._add(item)
        self._to_be_added = []
        for itemid in ids_to_remove:
            self.remove(itemid=itemid)

        self.collision.detect(self._items)

