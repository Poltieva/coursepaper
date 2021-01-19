from ukr_nums import nums
import re
import os
import docx2txt

#TODO убрать слова автора, сокращения

EOS_PUNCTS = {".": ".PERIOD", "?": "?QUESTIONMARK", "!": "!EXCLAMATIONMARK"}
INS_PUNCTS = {",": ",COMMA", ";": ";SEMICOLON", ":": ":COLON", "-": "-DASH"}
punct = {".": r".PERIOD", ",": ",COMMA", ":": ":COLON", ";": ",COMMA",
         "!": "!EXCLAMATIONMARK", "-": ",COMMA", "—": ",COMMA", ".—": r".PERIOD", "–": ",COMMA", ",-": ",COMMA"}

forbidden_symbols = re.compile(r"[\[\]\(\)\/\\\=\+\_\*]")
numbers = re.compile(r"\d")
multiple_punct = re.compile(r'([\.\?\!\,\:\;\-]) *(?:[\.\?\!\,\:\;\-]){1,}')

def is_number(el):
    for num in nums:
        if re.findall(num, el):
            return True
    return False


def skip(line):

    if line.strip() == '':
        return True

    if forbidden_symbols.search(line) is not None:
        print(re.findall(r"[\[\]\(\)\/\\\>\<\=\+\_\*]", line))
        return True
    return False


def read_and_write_data(path, entry):
    with open(path + entry.name, "r", encoding="utf-8") as file:
        info = file.read()
    if path.endswith("good/") or path.endswith("so-so/"):
        info = re.search(r"(?<=<body>).*(?=</body>)", info, flags=re.DOTALL).group(0)
    text_prepare(info, entry.name)


def process_line(line):
    if not re.findall(r"[А-яІЇіїЄє]", line):
        return ""
    line = re.sub(forbidden_symbols, '', line)
    line = re.sub(r"\d \. \d", r"", line, flags=re.M)
    line = line.replace(' - ', ' ')
    line = line.replace(' –', '')
    line = line.replace(' —', '')
    line = re.sub(r"\s?([.,;:!—()\"])\s?", r" \1 ", line, flags=re.M)  # tokenize
    line = re.sub(r"\n +", r"\n", line, flags=re.M)
    line = line.replace("!EXCLAMATIONMARK -DASH", "!EXCLAMATIONMARK")
    line = line.replace("?QUESTIONMARK -DASH", "?QUESTIONMARK")
    """for num in nums:
        line = re.sub(num, "<NUM>", line, flags=re.M)"""
    """line = re.sub(r"\w+-<NUM> ", "<NUM> ", line, flags=re.M)
    line = re.sub(r"\d+-\w+", "<NUM>", line, flags=re.M)"""
    line = line.strip()

    tokens = line.split(" ")
    output_tokens = []

    for token in tokens:

        if token in punct.keys():
            output_tokens.append(punct[token])
            #is_number(token) or
        elif token.isnumeric():
            output_tokens.append("<NUM>")
        else:
            output_tokens.append(token)
    return " ".join(output_tokens) + " "

def text_prepare(text, entry_name):
    """препроцесінг, токенізація тексту"""
    global skipped
    if text:
        text = text.strip()
        text = text.upper()

        # заміна поганих знаків
        text = re.sub(r"\(.+?\)", "", text, flags=re.M)
        text = re.sub(r"^Розділ \w+$", "", text, flags=re.M)
        text = re.sub(r"^\d+$", "", text, flags=re.M)
        text = re.sub(r"<d>–.+(?<=\.)", "", text, flags=re.M)
        text = text.replace("©", "")
        text = text.replace("1+1", "1")
        text = re.sub(r"http.*?\.ua", r"\n", text, flags=re.M)
        text = re.sub(r"\n\n+", r"\n", text, flags=re.M)

        text = text.replace(",—", ",").replace("’", "'")
        text = text.replace("? —", "?")
        text = text.replace("...", ".").replace("\n—", "\n")
        text = text.replace("?—", "?")
        text = re.sub(r"^— ", "", text)
        text = re.sub(r"\s\s+", " ", text, flags=re.M)
        text = re.sub(r"<.+?>", r"", text, flags=re.M)
        text = re.sub(r"^[0-9IXVХІ]+[.)][0-9]*([.]|[0-9XVIХІ])*\)?", r"", text, flags=re.M) # прибираємо пункти
        text = text.replace(" - ", " -DASH ")
        text = re.sub(r"(\. \d+ )+\.\d?", ".", text, flags=re.M)
        text = re.sub(r"\d+ : \d+", "1", text, flags=re.M)
        text = text.replace("%", " ВІДСОТКІВ")
        text = text.replace("№", "НОМЕР ")
        text = text.replace("$", "")
        text = re.sub(r"\d+-\d+", "1", text, flags=re.M)
        text = re.sub(r"\w+-\d+ ", "1 ", text, flags=re.M)
        text = re.sub(r"\d+-\w+", "1", text, flags=re.M)
        text = re.sub(r"^ \.", r"", text, flags=re.M)
        #TODO: add from ultimate_preprocessing.py
        #text = re.sub(r"\d+ *\d+", "<NUM>", text, flags=re.M)
        text = re.sub(r"\.( \.)+", ".", text, flags=re.M)
        text = re.sub(r" [XVI]+ ", " 1 ", text, flags=re.M)
        text = text.replace("\\", "")
        text = text.replace("…", "")
        text = re.sub(r"^§.+$", "", text, flags=re.M)
        text = text.replace(",\n", ".\n")
        text = text.replace("\t", " ").replace("•", "").replace("|", "")



        text = text.replace("?", " ?QUESTIONMARK")
        text = re.sub(r" \* (\* .+?\.) ?", r"", text, flags=re.M)
        text = text.replace("(", ",").replace(")", ",")
        text = re.sub(r"\[.*?\]", r"", text, flags=re.M)
        text = multiple_punct.sub(r"\g<1>", text)
        text = text.replace("  ", " ")

        lines = text.split("\n")
        with open("preprocessed/" + entry_name, 'w', encoding='utf-8') as out_txt:
            for line in lines:
                if line:
                    try:
                        last_symbol = line[-1]
                        if last_symbol not in EOS_PUNCTS.keys():
                            line += " ."
                    except IndexError:
                        pass

                    line = process_line(line)
                    line = line.replace(".PERIOD <NUM> .PERIOD <NUM> .PERIOD", ".PERIOD")
                    line = line.replace(".PERIOD <NUM> .PERIOD", ".PERIOD")
                    line = line.replace("<NUM> :COLON <NUM>", "<NUM>")
                    line = line.replace(",COMMA -DASH", ",COMMA")
                    line = line.replace(".PERIOD <NUM> .PERIOD <NUM>", ".PERIOD")
                    line = line.replace("<NUM> -DASH <NUM>", "<NUM>")
                    line = line.replace("<NUM> <NUM>", "<NUM>")
                    line = re.sub("\d+", "<NUM>", line, flags=re.M)
                    line = re.sub(r"<NUM> |(-<NUM>)|(—<NUM>)|–<NUM>", "<NUM>", line)
                    line = re.sub(r"<NUM>( <NUM>)+", "<NUM>", line)
                    line = line.replace("<NUM>ГА", "<NUM>")
                    line = line.replace("  ", " ")
                    if skip(line):
                        skipped += 1
                        with open("./texts/bad.txt", "a", encoding="utf-8") as file:
                            file.write("#\n" + line + "\n#\n")
                        continue

                    out_txt.write(line)
                    out_txt.write("\n")


skipped = 0
path = "./texts/"
dirs = ["add/", "good/", "so-so/", "child_lit/"]
if __name__ == "__main__":
    try:
        os.remove("./texts/bad.txt")
        with os.scandir("./preprocessed") as entries:
            for entry in entries:
                os.remove(entry)
    except FileNotFoundError:
        pass
    with os.scandir("./Тексти") as entries:
        for entry in entries:
            MY_TEXT = docx2txt.process(entry)
            with open("./texts/child_lit/"+entry.name[:-4]+"txt", "w", encoding="utf-8") as file:
                file.write(MY_TEXT)
    for directory in dirs:
        full_path = path + directory
        with os.scandir(full_path) as entries:
            for entry in entries:
                read_and_write_data(full_path, entry)
        print("Skipped %d lines" % skipped)
