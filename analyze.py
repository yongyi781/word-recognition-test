import sys


def main():
    with open("wrt_df.log" if len(sys.argv) <= 1 else sys.argv[1]) as f:
        lines = [line.split() for line in f if not line.startswith("#")]

    d = {}
    for line in lines:
        word = line[0].split("/")[0]
        d[word] = (
            (d[word][0] + 1, d[word][1] + int(line[1]))
            if word in d
            else (1, int(line[1]))
        )

    d_sorted = sorted(d.items(), key=lambda x: (x[1][1] / x[1][0], -x[1][0]))
    print("Words in order of difficulty:")
    for word, (a, b) in d_sorted:
        if a > 1:
            score = b / a
            str = f"{b}/{a}"
            print(f"{word:10}{str:7}{score * 100:8.2f}%")


if __name__ == "__main__":
    main()
