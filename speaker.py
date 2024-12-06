import asyncio
import os


class Speaker:
    volume = 0.35

    def __init__(self):
        os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

        from pygame import mixer

        mixer.init()
        mixer.music.set_volume(self.volume)
        self.mixer = mixer

    def speak_from_file(self, filename):
        self.mixer.music.load(filename)
        self.mixer.music.play()
        while self.mixer.music.get_busy():
            pass
        self.mixer.music.unload()

    def set_volume(self, volume):
        self.volume = volume
        self.mixer.music.set_volume(volume)

    def set_voice(self, voice): ...
    def speak(self, text): ...


class GTTSSpeaker(Speaker):
    name = "gTTS"
    voice = ""

    def set_voice(self, voice):
        self.voice = voice

    def speak(self, text, filepath=None):
        from gtts import gTTS

        if filepath is None:
            filepath = f"audio/gtts/{self.voice}/{text}.mp3"

        if not os.path.exists(f"audio/gtts/{self.voice}"):
            os.makedirs(f"audio/gtts/{self.voice}")
        if not os.path.exists(filepath):
            gTTS(text).save(filepath)
        self.speak_from_file(filepath)
        return filepath


class Pyttsx3Speaker(Speaker):
    name = "pyttsx3"

    def __init__(self):
        import pyttsx3

        super().__init__()
        self.engine = pyttsx3.init(driverName="sapi5")
        self.engine.setProperty("rate", 120)
        self.voices = self.engine.getProperty("voices")

        self.set_voice("Zira")
        self.set_volume(0.5)

    def set_volume(self, volume):
        self.volume = volume
        self.engine.setProperty("volume", volume)

    def set_voice(self, voice):
        voiceIndex = next(
            (i for i, v in enumerate(self.voices) if voice in v.name), None
        )
        if voiceIndex is None:
            print(
                f"Voice not found, so using default voice: {self.voice}. Available voices:\n  {"\n  ".join(v.name for v in self.voices)}"
            )
        else:
            self.voice = voice
            self.engine.setProperty("voice", self.voices[voiceIndex].id)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()


class EdgeSpeaker(Speaker):
    name = "edge"
    voice = "en-US-AriaNeural"

    def set_voice(self, voice):
        import edge_tts

        voices = [v["ShortName"] for v in asyncio.run(edge_tts.list_voices())]
        if voice in voices:
            self.voice = voice
        else:
            print(
                f"Voice {voice} not found, so using default voice. Available voices:\n  {"\n  ".join(voices)}"
            )

    def speak(self, text, filepath=None):
        import edge_tts

        if filepath is None:
            filepath = f"audio/edge/{self.voice}/{text}.mp3"

        if not os.path.exists(f"audio/edge/{self.voice}"):
            os.makedirs(f"audio/edge/{self.voice}")
        if not os.path.exists(filepath):
            # Create an instance of Communicate with text and voice parameters
            communicate = edge_tts.Communicate(text, voice=self.voice)

            # Generate speech and save to a file
            asyncio.run(communicate.save(filepath))
        self.speak_from_file(filepath)
        return filepath
