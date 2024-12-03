# Word Recognition Test

## Description

This project is a word recognition test tool. It allows users to test their ability to recognize and spell words, and provides a score based on their performance.

## Installation

### Step 1: Clone the repository

Clone the repository to your local machine.

### Step 2: Install dependencies

Install the required dependencies by running the following command:
```bash
pip install -r requirements.txt
```

### Step 3: Run the program

You can now run the program using the following command:
```bash
python wrt.py
```

## Usage

To use the program, simply run `python wrt.py` and follow the prompts. You can specify the name of the condition, the word list file, and the text-to-speech engine to use. The program will then prompt you to spell each word in the word list, and provide feedback on whether your answer was correct or not. At the end, it will display your score.

### Command Line Options

* `-l` or `--list`: Specify the word list file to use
* `-t` or `--tts`: Specify the text-to-speech engine to use (gtts, pyttsx3, or edge)
* `-v` or `--voice`: Specify the voice parameter for the text-to-speech engine.
* `condition_name`: Specify the name of the condition

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
