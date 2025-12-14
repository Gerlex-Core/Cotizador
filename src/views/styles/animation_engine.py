"""
Animation Engine - Centralized animation definitions with theme override support.
Provides base animations for all component types that can be customized by themes.
"""

from typing import Dict, Any, Optional, Callable
from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
    QSequentialAnimationGroup, QAbstractAnimation, QObject, QPoint, QRect
)
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect


# Easing curve mappings
EASING_CURVES = {
    'Linear': QEasingCurve.Type.Linear,
    'InQuad': QEasingCurve.Type.InQuad,
    'OutQuad': QEasingCurve.Type.OutQuad,
    'InOutQuad': QEasingCurve.Type.InOutQuad,
    'InCubic': QEasingCurve.Type.InCubic,
    'OutCubic': QEasingCurve.Type.OutCubic,
    'InOutCubic': QEasingCurve.Type.InOutCubic,
    'InQuart': QEasingCurve.Type.InQuart,
    'OutQuart': QEasingCurve.Type.OutQuart,
    'InOutQuart': QEasingCurve.Type.InOutQuart,
    'InBack': QEasingCurve.Type.InBack,
    'OutBack': QEasingCurve.Type.OutBack,
    'InOutBack': QEasingCurve.Type.InOutBack,
    'InBounce': QEasingCurve.Type.InBounce,
    'OutBounce': QEasingCurve.Type.OutBounce,
    'InOutBounce': QEasingCurve.Type.InOutBounce,
    'InElastic': QEasingCurve.Type.InElastic,
    'OutElastic': QEasingCurve.Type.OutElastic,
    'InOutElastic': QEasingCurve.Type.InOutElastic,
}


class AnimationEngine:
    """
    Manages base and custom animations per component type.
    Provides factory methods for creating Qt animations from theme configs.
    """
    
    _instance = None
    
    # Base animation definitions by component type
    BASE_ANIMATIONS = {
        'button': {
            'hover': {
                'type': 'scale',
                'from': 1.0,
                'to': 1.03,
                'duration': 150,
                'easing': 'OutCubic'
            },
            'press': {
                'type': 'scale',
                'from': 1.0,
                'to': 0.97,
                'duration': 100,
                'easing': 'OutCubic'
            },
            'ripple': {
                'type': 'ripple',
                'duration': 400,
                'easing': 'OutCubic',
                'enabled': True
            },
            'glow': {
                'type': 'opacity',
                'from': 0.0,
                'to': 0.4,
                'duration': 250,
                'easing': 'OutCubic'
            }
        },
        'panel': {
            'show': {
                'type': 'fade',
                'from': 0.0,
                'to': 1.0,
                'duration': 250,
                'easing': 'OutCubic'
            },
            'hide': {
                'type': 'fade',
                'from': 1.0,
                'to': 0.0,
                'duration': 150,
                'easing': 'InCubic'
            },
            'glow_pulse': {
                'type': 'opacity',
                'from': 0.1,
                'to': 0.3,
                'duration': 1000,
                'easing': 'InOutCubic',
                'loop': True
            }
        },
        'table': {
            'row_insert': {
                'type': 'slide_fade',
                'direction': 'top',
                'duration': 200,
                'easing': 'OutCubic'
            },
            'row_remove': {
                'type': 'fade',
                'from': 1.0,
                'to': 0.0,
                'duration': 150,
                'easing': 'OutCubic'
            },
            'row_highlight': {
                'type': 'color_flash',
                'duration': 300,
                'easing': 'OutCubic'
            }
        },
        'input': {
            'focus': {
                'type': 'border_glow',
                'duration': 200,
                'easing': 'OutCubic'
            },
            'error_shake': {
                'type': 'shake',
                'amplitude': 10,
                'duration': 400,
                'easing': 'OutElastic'
            }
        },
        'dialog': {
            'open': {
                'type': 'scale_fade',
                'from_scale': 0.9,
                'to_scale': 1.0,
                'from_opacity': 0.0,
                'to_opacity': 1.0,
                'duration': 200,
                'easing': 'OutCubic'
            },
            'close': {
                'type': 'scale_fade',
                'from_scale': 1.0,
                'to_scale': 0.9,
                'from_opacity': 1.0,
                'to_opacity': 0.0,
                'duration': 150,
                'easing': 'InCubic'
            }
        },
        'toast': {
            'show': {
                'type': 'slide',
                'direction': 'bottom',
                'distance': 100,
                'duration': 300,
                'easing': 'OutBack'
            },
            'hide': {
                'type': 'fade',
                'from': 1.0,
                'to': 0.0,
                'duration': 200,
                'easing': 'OutCubic'
            }
        },
        'menu': {
            'open': {
                'type': 'scale_fade',
                'from_scale': 0.95,
                'to_scale': 1.0,
                'from_opacity': 0.0,
                'to_opacity': 1.0,
                'duration': 150,
                'easing': 'OutCubic'
            }
        }
    }
    
    def __init__(self):
        self._custom_overrides: Dict[str, Dict] = {}
        self._global_speed: float = 1.0
    
    @classmethod
    def get_instance(cls) -> 'AnimationEngine':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = AnimationEngine()
        return cls._instance
    
    def set_global_speed(self, speed: float):
        """Set global animation speed multiplier (1.0 = normal, 2.0 = 2x faster)."""
        self._global_speed = max(0.1, min(5.0, speed))
    
    def set_custom_overrides(self, overrides: Dict[str, Dict]):
        """Set custom animation overrides from theme config."""
        self._custom_overrides = overrides or {}
    
    def get_animation_config(self, component_type: str, animation_name: str) -> Dict[str, Any]:
        """
        Get animation config for a component, with theme overrides applied.
        
        Args:
            component_type: Type of component (button, panel, table, etc.)
            animation_name: Name of animation (hover, press, show, etc.)
        
        Returns:
            Animation configuration dict
        """
        # Get base animation
        base = self.BASE_ANIMATIONS.get(component_type, {}).get(animation_name, {})
        if not base:
            return {}
        
        # Apply custom overrides if present
        custom = self._custom_overrides.get(component_type, {}).get(animation_name, {})
        
        # Merge configs (custom overrides base)
        config = {**base, **custom}
        
        # Apply global speed
        if 'duration' in config:
            config['duration'] = int(config['duration'] / self._global_speed)
        
        return config
    
    def create_fade_animation(
        self,
        widget: QWidget,
        from_opacity: float = 0.0,
        to_opacity: float = 1.0,
        duration: int = 250,
        easing: str = 'OutCubic'
    ) -> QPropertyAnimation:
        """Create a fade in/out animation."""
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
        
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(int(duration / self._global_speed))
        anim.setStartValue(from_opacity)
        anim.setEndValue(to_opacity)
        anim.setEasingCurve(EASING_CURVES.get(easing, QEasingCurve.Type.OutCubic))
        
        return anim
    
    def create_slide_animation(
        self,
        widget: QWidget,
        direction: str = 'left',
        distance: int = 100,
        duration: int = 250,
        easing: str = 'OutCubic',
        reverse: bool = False
    ) -> QPropertyAnimation:
        """Create a slide animation."""
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(int(duration / self._global_speed))
        anim.setEasingCurve(EASING_CURVES.get(easing, QEasingCurve.Type.OutCubic))
        
        current_pos = widget.pos()
        
        if direction == 'left':
            offset = QPoint(-distance, 0)
        elif direction == 'right':
            offset = QPoint(distance, 0)
        elif direction == 'top':
            offset = QPoint(0, -distance)
        elif direction == 'bottom':
            offset = QPoint(0, distance)
        else:
            offset = QPoint(0, 0)
        
        if reverse:
            anim.setStartValue(current_pos)
            anim.setEndValue(current_pos + offset)
        else:
            anim.setStartValue(current_pos + offset)
            anim.setEndValue(current_pos)
        
        return anim
    
    def create_geometry_animation(
        self,
        widget: QWidget,
        target_geometry: QRect,
        duration: int = 250,
        easing: str = 'OutCubic'
    ) -> QPropertyAnimation:
        """Create a geometry change animation."""
        anim = QPropertyAnimation(widget, b"geometry")
        anim.setDuration(int(duration / self._global_speed))
        anim.setStartValue(widget.geometry())
        anim.setEndValue(target_geometry)
        anim.setEasingCurve(EASING_CURVES.get(easing, QEasingCurve.Type.OutCubic))
        
        return anim
    
    def create_animation_group(
        self,
        animations: list,
        parallel: bool = True
    ) -> QAbstractAnimation:
        """Create a group of animations."""
        if parallel:
            group = QParallelAnimationGroup()
        else:
            group = QSequentialAnimationGroup()
        
        for anim in animations:
            group.addAnimation(anim)
        
        return group
    
    def create_from_config(
        self,
        widget: QWidget,
        config: Dict[str, Any]
    ) -> Optional[QAbstractAnimation]:
        """
        Create animation from a configuration dict.
        
        Args:
            widget: Target widget
            config: Animation configuration
        
        Returns:
            QAbstractAnimation or None if config is invalid
        """
        anim_type = config.get('type')
        duration = config.get('duration', 250)
        easing = config.get('easing', 'OutCubic')
        
        if anim_type == 'fade':
            return self.create_fade_animation(
                widget,
                config.get('from', 0.0),
                config.get('to', 1.0),
                duration,
                easing
            )
        elif anim_type == 'slide':
            return self.create_slide_animation(
                widget,
                config.get('direction', 'left'),
                config.get('distance', 100),
                duration,
                easing,
                config.get('reverse', False)
            )
        elif anim_type == 'scale_fade':
            # Combined scale and fade
            fade_anim = self.create_fade_animation(
                widget,
                config.get('from_opacity', 0.0),
                config.get('to_opacity', 1.0),
                duration,
                easing
            )
            return fade_anim  # Scale handled in paintEvent
        
        return None


# Global instance
def get_animation_engine() -> AnimationEngine:
    """Get the global animation engine instance."""
    return AnimationEngine.get_instance()
