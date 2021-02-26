import random as rm


def gen_line(l, m, src):
    n = rm.randint(l, m)
    line = [1 for i in range(n)] + [0 for i in range(11 - n)]
    rm.shuffle(line)
    for i in range(len(line)):
        if m != 0:
            if line[i] == 1:
                line[i] = rm.choice(src)
            else:
                line[i] = (rm.randint(50, 200), 30)
        else:
            line[i] = (rm.randint(50, 200), rm.randint(90, 110))
    return line


def gen_lvl():
    lower = ["bpan", "dabp", "darp", "dayp", "ftng", "gpan", "lbpl", "lypl", "wpan", "ypan"]
    upper = ["blfp", "bsfp", "glfp", "gsfp", "rlfp", "rsfp", "ylfp", "ysfp"] + lower
    lvl = []
    lvl.append(gen_line(5, 10, lower))
    lvl.append(gen_line(0, 0, upper))
    lvl.append(gen_line(6, 9, upper))
    lvl.append(gen_line(0, 0, upper))
    lvl.append(gen_line(4, 7, upper))
    lvl.append(gen_line(0, 0, upper))
    return lvl

if __name__ == "__main__":
    r = gen_lvl()
    for i in r:
        print(i)