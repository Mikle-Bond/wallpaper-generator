from random import sample
from pathlib import Path

palette_providers = dict()
def palette(name):
    """Palette decorator"""
    def wrapper(cls):
        palette_providers[name] = cls
        return cls
    return wrapper

class Palettes(object):
    """Base class for palettes extractors"""
    def __init__(self):
        pass
    def get_color_palette(self):
        pass
    def get_color_pair(self):
        pass

@palette('wal')
class WalPalette(Palettes):
    """Extract color palette from wal cache"""

    def __init__(self, yaml_file=None):
        """Open yaml description in wal cache

        :yaml_file: yaml description of colorscheme

        """
        Palettes.__init__(self)

        if not yaml_file:
            from pywal.settings import CACHE_DIR
            yaml_file = Path(CACHE_DIR) / 'colors.yml'

        from yaml import load

        with open(yaml_file) as y:
            self._dict = load(y)

        self._colors = self._dict['colors']
        self._palette = list(self._colors.values())

        self._spec = self._dict['special']
        self._bg = self._spec['background']
        self._fg = self._spec['foreground']

        # NB: palette[0] == bg, palette[7] == palette [15] == fg,
        #     palette[n] ~= palette[n+8]

    @staticmethod
    def h2t(s): 
        return tuple(map(int, bytes.fromhex(s[1:])))

    @staticmethod
    def h2t_list(l):
        return list(map(WalPalette.h2t, l))

    def get_color_palette(self, throttle=5):
        return self.h2t_list(self._palette[:throttle])

    def get_color_pair(self, throttle=4, force_background=True, force_foreground=False):
        # Get all colors in palette
        colors = self._palette[1:throttle]
        # Expand it with colors we don't force
        if not force_background:
            colors.append(self._bg)
        if not force_foreground:
            colors.append(self._fg)
        # Pick 2 colors
        choice = sample(colors, 2)
        # and replace with forced colors
        if force_background:
            choice[0] = self._bg
        if force_foreground:
            choice[1] = self._fg

        return self.h2t_list(choice)

@palette('terminalsexy')
class TerminalSexyPalettes(Palettes):

    def __init__(self):
        Palettes.__init__(self)

    def get_color_palette(self):
        pass

    def get_color_pair(self):
        pass

@palette('pastel')
class PastelPalettes(Palettes):

    def __init__(self):
        Palettes.__init__(self)
        from colors import palettes
        self._palettes = palettes

    def get_color_palette(self, name='forest'):
        return self._palettes['pastel_'+name]

    def get_color_pair(self, name='forest'):
        return sample(self.get_color_palette(name), 2)

