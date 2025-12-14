"""
Sound Manager - Theme sound effects and music playback.
Official themes use Windows system sounds, custom themes can use custom audio files.
"""

import os
import platform
from typing import Dict, Optional
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput


class SoundManager:
    """
    Manages theme sound effects and background music.
    
    Official themes use Windows system sounds.
    Custom themes can provide their own audio files.
    """
    
    _instance = None
    
    # Windows system sounds mapping
    WINDOWS_SOUNDS = {
        'click': 'SystemDefault',
        'hover': None,  # No system sound for hover by default
        'success': 'SystemExclamation',
        'error': 'SystemHand',
        'warning': 'SystemAsterisk',
        'notification': 'SystemNotification',
        'open': 'WindowsLogon',
        'close': 'WindowsLogoff',
    }
    
    # Sound event types
    SOUND_EVENTS = [
        'click',
        'hover', 
        'success',
        'error',
        'warning',
        'notification',
        'open',
        'close',
        'transition',
    ]
    
    def __init__(self):
        self._sounds: Dict[str, QSoundEffect] = {}
        self._music_player: Optional[QMediaPlayer] = None
        self._audio_output: Optional[QAudioOutput] = None
        self._enabled = True
        self._volume = 0.5
        self._use_system_sounds = True
        self._custom_sounds_path: Optional[str] = None
        self._is_windows = platform.system() == 'Windows'
    
    @classmethod
    def get_instance(cls) -> 'SoundManager':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = SoundManager()
        return cls._instance
    
    @property
    def enabled(self) -> bool:
        return self._enabled
    
    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value
        if not value and self._music_player:
            self._music_player.stop()
    
    @property
    def volume(self) -> float:
        return self._volume
    
    @volume.setter
    def volume(self, value: float):
        self._volume = max(0.0, min(1.0, value))
        for sound in self._sounds.values():
            sound.setVolume(self._volume)
        if self._audio_output:
            self._audio_output.setVolume(self._volume)
    
    def configure_for_official_theme(self):
        """Configure to use Windows system sounds (for official themes)."""
        self._use_system_sounds = True
        self._custom_sounds_path = None
        self._sounds.clear()
    
    def configure_for_custom_theme(self, theme_path: str, sound_config: Dict):
        """
        Configure custom sounds from theme folder.
        
        Args:
            theme_path: Base path to theme folder
            sound_config: Sound configuration from theme JSON
        """
        self._use_system_sounds = False
        self._custom_sounds_path = theme_path
        self._sounds.clear()
        
        # Set volume from config
        if 'volume' in sound_config:
            self.volume = sound_config['volume']
        
        # Set enabled state
        if 'enabled' in sound_config:
            self.enabled = sound_config['enabled']
        
        # Load custom sound effects
        effects = sound_config.get('effects', {})
        for event_name, relative_path in effects.items():
            if relative_path:
                full_path = os.path.join(theme_path, relative_path)
                if os.path.exists(full_path):
                    self._load_sound(event_name, full_path)
    
    def _load_sound(self, name: str, path: str):
        """Load a sound effect from file."""
        try:
            sound = QSoundEffect()
            sound.setSource(QUrl.fromLocalFile(path))
            sound.setVolume(self._volume)
            sound.setLoopCount(1)
            self._sounds[name] = sound
        except Exception as e:
            print(f"Error loading sound '{name}' from {path}: {e}")
    
    def play(self, sound_name: str):
        """
        Play a named sound effect.
        
        Args:
            sound_name: Name of the sound event (click, hover, success, etc.)
        """
        if not self._enabled:
            return
        
        if self._use_system_sounds:
            self._play_system_sound(sound_name)
        else:
            self._play_custom_sound(sound_name)
    
    def _play_system_sound(self, sound_name: str):
        """Play a Windows system sound."""
        if not self._is_windows:
            return
        
        try:
            import winsound
            
            # Map sound name to Windows sound
            system_sound = self.WINDOWS_SOUNDS.get(sound_name)
            
            if system_sound == 'SystemDefault':
                winsound.MessageBeep(winsound.MB_OK)
            elif system_sound == 'SystemExclamation':
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            elif system_sound == 'SystemHand':
                winsound.MessageBeep(winsound.MB_ICONHAND)
            elif system_sound == 'SystemAsterisk':
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            elif system_sound:
                # Try to play named system sound
                try:
                    winsound.PlaySound(system_sound, winsound.SND_ALIAS | winsound.SND_ASYNC)
                except:
                    pass
        except ImportError:
            pass  # winsound not available
    
    def _play_custom_sound(self, sound_name: str):
        """Play a custom theme sound."""
        sound = self._sounds.get(sound_name)
        if sound and sound.isLoaded():
            sound.play()
    
    def play_music(self, file_path: str, loop: bool = True):
        """
        Play background music (for custom themes).
        
        Args:
            file_path: Path to music file
            loop: Whether to loop the music
        """
        if not self._enabled:
            return
        
        if not os.path.exists(file_path):
            return
        
        try:
            if self._music_player is None:
                self._music_player = QMediaPlayer()
                self._audio_output = QAudioOutput()
                self._music_player.setAudioOutput(self._audio_output)
            
            self._audio_output.setVolume(self._volume * 0.5)  # Music at half volume
            
            self._music_player.setSource(QUrl.fromLocalFile(file_path))
            
            if loop:
                self._music_player.setLoops(QMediaPlayer.Loops.Infinite)
            
            self._music_player.play()
        except Exception as e:
            print(f"Error playing music: {e}")
    
    def stop_music(self):
        """Stop background music."""
        if self._music_player:
            self._music_player.stop()
    
    def pause_music(self):
        """Pause background music."""
        if self._music_player:
            self._music_player.pause()
    
    def resume_music(self):
        """Resume background music."""
        if self._music_player and self._enabled:
            self._music_player.play()


# Global instance
def get_sound_manager() -> SoundManager:
    """Get the global sound manager instance."""
    return SoundManager.get_instance()
