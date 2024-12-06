import argparse
import os

from speaker import EdgeSpeaker


def main():
    parser = argparse.ArgumentParser(description="TTS speaker (using Edge).")
    parser.add_argument(
        "text",
        type=str,
        help="The text to speak",
    )
    parser.add_argument("-v", "--voice", type=str, help="Voice to use")
    parser.add_argument("-V", "--volume", type=float, help="Volume")

    args = parser.parse_args()
    speaker = EdgeSpeaker()

    if args.voice is not None:
        speaker.set_voice(args.voice)

    if args.volume is not None:
        speaker.set_volume(args.volume)

    path = "temp.mp3"
    if os.path.exists(path):
        os.remove(path)
    speaker.speak(args.text, path)


if __name__ == "__main__":
    main()
