import pygame
import os
import random

class MusicManager:
    def __init__(self):
        self.current_track = None
        self.music_directory = "assets/music"
        self.tracks = {}  # All tracks stored in one dict
        self.load_music()
    
    def load_music(self):
        """Load all music tracks from the assets/music directory"""
        try:
            for filename in os.listdir(self.music_directory):
                if filename.endswith('.mp3'):
                    # Remove .mp3 and use as track name
                    track_name = filename[:-4]
                    self.tracks[track_name] = os.path.join(self.music_directory, filename)
        except Exception as e:
            print(f"Warning: Could not load music files: {e}")
    
    def play_menu_music(self):
        """Play a random track from all available tracks"""
        try:
            if self.tracks:
                # Get a random track that's different from the current one
                available_tracks = [track for track in self.tracks.values() 
                                 if track != self.current_track]
                if available_tracks:
                    track = random.choice(available_tracks)
                    pygame.mixer.music.load(track)
                    pygame.mixer.music.play(-1)
                    self.current_track = track
        except Exception as e:
            print(f"Warning: Could not play menu music: {e}")
    
    def play_game_music(self, biome, is_night):
        """Play appropriate music for the biome and time of day"""
        try:
            # Determine which track to play
            time = "night" if is_night else "day"
            track_name = f"{biome}_{time}"
            
            if track_name in self.tracks:
                track = self.tracks[track_name]
                if self.current_track != track:
                    pygame.mixer.music.load(track)
                    pygame.mixer.music.play(-1)
                    self.current_track = track
        except Exception as e:
            print(f"Warning: Could not play game track: {e}")
    
    def stop_music(self):
        """Stop the currently playing music"""
        try:
            pygame.mixer.music.stop()
            self.current_track = None
        except:
            pass 