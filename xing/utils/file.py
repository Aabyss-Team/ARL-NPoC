
def load_file(path):
    with open(path, "r+", encoding="utf-8") as f:
        return f.readlines()

def append_file(path, msgs):
    with open(path, "a", encoding="utf-8") as f:
        for msg in msgs:
            f.write("{}\n".format(str(msg).strip()))
