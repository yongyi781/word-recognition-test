import argparse
import asyncio
import os
import os.path
import random
from datetime import datetime

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Speaker:
    volume = 0.35

    def __init__(self):
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
        self.voice = ""

    def speak(self, text):
        from gtts import gTTS

        if not os.path.exists("audio/gtts"):
            os.makedirs("audio/gtts")
        filename = f"audio/gtts/{text}.mp3"
        if not os.path.exists(filename):
            gTTS(text).save(filename)
        self.speak_from_file(filename)


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

    def speak(self, text):
        import edge_tts

        if not os.path.exists(f"audio/edge/{self.voice}"):
            os.makedirs(f"audio/edge/{self.voice}")
        filename = f"audio/edge/{self.voice}/{text}.mp3"
        if not os.path.exists(filename):
            # Create an instance of Communicate with text and voice parameters
            communicate = edge_tts.Communicate(text, voice=self.voice)

            # Generate speech and save to a file
            asyncio.run(communicate.save(filename))
        self.speak_from_file(filename)


def run_word_recognition_test(speaker, list_file, log_file=None):
    word_list = []
    with open(list_file, "r", encoding="utf-8") as inFile:
        word_list = [
            line.split("/")
            for line in inFile.read().splitlines()
            if len(line) > 0 and not line.startswith("#")
        ]
    random.shuffle(word_list)

    print(
        f"Welcome to the word recognition test. The word list has {len(word_list)} words. At any time, press Ctrl+C to stop."
    )
    total = 0
    totalCorrect = 0

    log = None
    incorrect_words = []
    user_stopped = False
    if log_file is not None:
        log = open(log_file, "a", encoding="utf-8")
    try:
        if log is not None:
            log.write(
                f"# Word list: {list_file}\n# TTS: {speaker.name}\n# Voice: {speaker.voice}\n# Volume: {speaker.volume}\n"
            )
        for word_spellings in word_list:
            if isinstance(word_spellings, str):
                word_spellings = [word_spellings]
            word = word_spellings[0]
            guess = ""
            while guess == "":
                speaker.speak(word)
                guess = input("What was the word? ")
                if guess == "":
                    continue
                correct = any(guess.lower() == w.lower() for w in word_spellings)
                if correct:
                    print(bcolors.OKGREEN + "  Correct!" + bcolors.ENDC)
                else:
                    message = (
                        bcolors.FAIL
                        + "  Incorrect."
                        + bcolors.ENDC
                        + f" The word was {word}"
                    )
                    if not any(guess in ls for ls in word_list):
                        message += " (your guess is not in the word list)"
                    print(message)
                    incorrect_words.append("/".join(word_spellings))
                if log is not None:
                    log.write(f"{'/'.join(word_spellings):24} {int(correct)} {guess}\n")
                    log.flush()
                total += 1
                totalCorrect += correct
    except KeyboardInterrupt:
        print(bcolors.WARNING + "[Interrupt]" + bcolors.ENDC)
        user_stopped = True
    except Exception as e:
        print(e)
    finally:
        if user_stopped:
            print(f"  Ending. The word was {word}")
        if total > 0:
            message = (
                f"Score: {totalCorrect}/{total} = {100 * totalCorrect / total:.2f}%"
            )
            print(message + f"\nIncorrect words: {incorrect_words}")
            if log is not None:
                log.write(f"# {message}\n# Timestamp: {datetime.now()}\n\n")
        return incorrect_words


def main():
    default_list_file = "./data/one_syllable_words.txt"

    parser = argparse.ArgumentParser(description="Word recognition test.")
    parser.add_argument(
        "condition_name",
        type=str,
        help="Name of the condition",
    )
    parser.add_argument(
        "-l",
        "--list",
        type=str,
        help="Word list to use",
        default=default_list_file,
    )
    parser.add_argument(
        "-t",
        "--tts",
        choices=["gtts", "pyttsx3", "edge"],
        help="Text-to-speech engine to use",
        default="edge",
    )
    parser.add_argument("-v", "--voice", type=str, help="Voice to use")
    parser.add_argument("-V", "--volume", type=float, help="Volume")

    args = parser.parse_args()

    log_file = (
        f"wrt_{args.condition_name}.log"
        if args.list == default_list_file
        else f"wrt_{args.condition_name}_custom.log"
    )

    speaker = {
        "gtts": GTTSSpeaker,
        "pyttsx3": Pyttsx3Speaker,
        "edge": EdgeSpeaker,
    }[args.tts]()

    if args.voice is not None:
        speaker.set_voice(args.voice)

    if args.volume is not None:
        speaker.set_volume(args.volume)

    incorrect_words = run_word_recognition_test(speaker, args.list, log_file)
    with open("./incorrect_words.txt", "w+", encoding="utf-8") as outFile:
        outFile.writelines(w + "\n" for w in incorrect_words)


if __name__ == "__main__":
    main()
