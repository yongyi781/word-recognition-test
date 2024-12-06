import argparse
import random
from datetime import datetime

from speaker import EdgeSpeaker, GTTSSpeaker, Pyttsx3Speaker


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
