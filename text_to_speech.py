import os
import elevenlabs
from elevenlabs.client import ElevenLabs
import subprocess
import platform

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")


def text_to_speech_with_elevenlabs(input_text, output_filepath):
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio = client.text_to_speech.convert(
        text=input_text,
        voice_id="SZfY4K69FwXus87eayHK",  # "JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        output_format="mp3_22050_32",
    )
    elevenlabs.save(audio, output_filepath)
    
    # Fixed audio playback for different operating systems
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(['afplay', output_filepath])
        elif os_name == "Windows":  # Windows
            # Fixed: Use proper MP3 player for Windows
            subprocess.run(['powershell', '-c', f'Add-Type -AssemblyName presentationCore; $mediaPlayer = New-Object System.Windows.Media.MediaPlayer; $mediaPlayer.Open([System.Uri]::new((Resolve-Path "{output_filepath}").Path)); $mediaPlayer.Play(); Start-Sleep -Seconds 10'])
        elif os_name == "Linux":  # Linux
            # Use mpg123 for MP3 files on Linux
            subprocess.run(['mpg123', output_filepath])
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"An error occurred while trying to play the audio: {e}")


from gtts import gTTS

def text_to_speech_with_gtts(input_text, output_filepath):
    language = "en"

    audioobj = gTTS(
        text=input_text,
        lang=language,
        slow=False
    )
    audioobj.save(output_filepath)
    
    # Fixed audio playback for different operating systems
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(['afplay', output_filepath])
        elif os_name == "Windows":  # Windows
            # Fixed: Use proper MP3 player for Windows
            subprocess.run(['powershell', '-c', f'Add-Type -AssemblyName presentationCore; $mediaPlayer = New-Object System.Windows.Media.MediaPlayer; $mediaPlayer.Open([System.Uri]::new((Resolve-Path "{output_filepath}").Path)); $mediaPlayer.Play(); Start-Sleep -Seconds 10'])
        elif os_name == "Linux":  # Linux
            # Use mpg123 for MP3 files on Linux
            subprocess.run(['mpg123', output_filepath])
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"An error occurred while trying to play the audio: {e}")


# Alternative simpler solution using pygame (recommended)
def play_audio_with_pygame(output_filepath):
    """Alternative audio player using pygame - more reliable"""
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(output_filepath)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
    except ImportError:
        print("Pygame not installed. Install with: uv add pygame")
    except Exception as e:
        print(f"Error playing audio with pygame: {e}")
    finally:
        try:
            pygame.mixer.quit()
        except:
            pass


# Enhanced versions with pygame fallback
def text_to_speech_with_elevenlabs_enhanced(input_text, output_filepath):
    """Enhanced version with pygame fallback"""
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio = client.text_to_speech.convert(
        text=input_text,
        voice_id="SZfY4K69FwXus87eayHK",
        model_id="eleven_multilingual_v2",
        output_format="mp3_22050_32",
    )
    elevenlabs.save(audio, output_filepath)
    
    # Try pygame first, then fallback to system player
    try:
        play_audio_with_pygame(output_filepath)
    except:
        # Fallback to system player
        os_name = platform.system()
        if os_name == "Windows":
            subprocess.run(['powershell', '-c', f'Add-Type -AssemblyName presentationCore; $mediaPlayer = New-Object System.Windows.Media.MediaPlayer; $mediaPlayer.Open([System.Uri]::new((Resolve-Path "{output_filepath}").Path)); $mediaPlayer.Play(); Start-Sleep -Seconds 10'])


def text_to_speech_with_gtts_enhanced(input_text, output_filepath):
    """Enhanced version with pygame fallback"""
    language = "en"
    audioobj = gTTS(text=input_text, lang=language, slow=False)
    audioobj.save(output_filepath)
    
    # Try pygame first, then fallback to system player
    try:
        play_audio_with_pygame(output_filepath)
    except:
        # Fallback to system player
        os_name = platform.system()
        if os_name == "Windows":
            subprocess.run(['powershell', '-c', f'Add-Type -AssemblyName presentationCore; $mediaPlayer = New-Object System.Windows.Media.MediaPlayer; $mediaPlayer.Open([System.Uri]::new((Resolve-Path "{output_filepath}").Path)); $mediaPlayer.Play(); Start-Sleep -Seconds 10'])


# Test code (uncomment to test)
# input_text = "Hi, I am doing fine, how are you? This is a test for AI with Hassan"
# output_filepath = "test_text_to_speech.mp3"
# text_to_speech_with_elevenlabs_enhanced(input_text, output_filepath)
# text_to_speech_with_gtts_enhanced(input_text, output_filepath)