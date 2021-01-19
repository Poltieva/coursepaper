##################### FIRST STAGE ############################
import os, re
from random import shuffle

EOS_PUNCTS = [".PERIOD", "?QUESTIONMARK", "!EXCLAMATIONMARK"]

data = ""
path = "./preprocessed/"
with os.scandir(path) as entries:
    for entry in entries:
        with open(path + entry.name, "r", encoding="utf-8") as file:
            data += file.read()

data = data.split("\n")
shuffle(data)
data = "\n".join(data)

data = data.replace("  ", " ")
data = data.replace(",COMMA .PERIOD", ".PERIOD")
data = re.sub(r"NUM>(?=\S)", r"NUM> ", data, flags=re.M)
data = re.sub(r"(?<=\S)<NUM>", r" <NUM>", data, flags=re.M)
data = data.replace("<NUM> P ", "<NUM>")
data = data.split(" ")

len_data = len(data)
index = int(round(len_data * 0.8))
while data[index] not in EOS_PUNCTS:
    index += 1
index += 1
train = data[:index]
index2 = int((len_data - index) / 2) + index
while data[index2] not in EOS_PUNCTS:
    index2 += 1
index2 += 1
test = data[index: index2]
dev = data[index2:]
path = "./data_dir1/"
with open(path + "data.train.txt", "w", encoding="utf-8") as file:
    file.write(" ".join(train))
with open(path + "data.test.txt", "w", encoding="utf-8") as file:
    file.write(" ".join(test))
with open(path + "data.dev.txt", "w", encoding="utf-8") as file:
    file.write(" ".join(dev))