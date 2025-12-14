# Styles package - Theme and animation management
from .theme_manager import ThemeManager, THEMES, Theme, load_themes
from .theme_base import ThemeConfig, get_luminance, is_dark_theme, get_contrast_color
from .animations import AnimationFactory, DURATIONS, EASINGS

# New theme engine
from .theme_engine import ThemeEngine, ThemeData, get_theme_engine
from .animation_engine import AnimationEngine, get_animation_engine, EASING_CURVES
from .sound_manager import SoundManager, get_sound_manager
from .effects_engine import EffectsEngine, get_effects_engine
from .themeable import IThemeable, ComponentRegistry, get_component_registry
from .layout_engine import LayoutEngine, LayoutConfig, get_layout_engine
from .icon_manager import IconManager
from .themeable_mixin import ThemeableMixin, make_themeable

__all__ = [
    # Legacy
    'ThemeManager', 'THEMES', 'Theme', 'load_themes',
    'ThemeConfig', 'get_luminance', 'is_dark_theme', 'get_contrast_color',
    'AnimationFactory', 'DURATIONS', 'EASINGS',
    # New system
    'ThemeEngine', 'ThemeData', 'get_theme_engine',
    'AnimationEngine', 'get_animation_engine', 'EASING_CURVES',
    'SoundManager', 'get_sound_manager',
    'EffectsEngine', 'get_effects_engine',
    'IThemeable', 'ComponentRegistry', 'get_component_registry',
    'LayoutEngine', 'LayoutConfig', 'get_layout_engine',
    'IconManager',
    'ThemeableMixin', 'make_themeable',
]

