import os
import platform
import datetime
import time
import calendar

def find(path, dir):
    if not isinstance(path, str) or not isinstance(dir, str) or not path or not dir:
        print("error: 'path' and 'dir' have to be non empty strings")
        return

    depth = -1
    dir_index = 0
    dir_indices = []
    contents = [path]
    stack = []
    dir = dir.rpartition('/')[2]
    dir = dir.rpartition('\\')[2]
    while True:
        dirs = []
        for entry in contents:
            try:
                os.listdir(entry)
            except NotADirectoryError:
                continue
            dirs.append(entry)
            tmp = entry.rpartition('/')[2]
            tmp = tmp.rpartition('\\')[2]
            if dir == tmp:
                print(entry)

        if dirs:
            stack.append(dirs)
            depth += 1
            dir_indices.append(dir_index)
            dir_index = 0
        else:
            while stack:
                if dir_index < len(stack[depth]) - 1:
                    dir_index += 1
                    dir_indices[depth] += 1
                    break

                del stack[depth]
                if depth:
                    depth -= 1
                    dir_index = dir_indices[depth]
                    del dir_indices[-1]

            if not stack:
                break

        contents = os.listdir(stack[depth][dir_index])
        for i, entry in enumerate(contents):
            contents[i] = stack[depth][dir_index]
            if stack[depth][dir_index][-1] not in ['/', '\\']:
                contents[i] += '/'
            contents[i] += entry

class A:
    A = 1
    def __init__(self):
        self.a = 1

if __name__ == "__main__":
    find(".", "images")
    print(platform.uname())

    timestamp = 1572879180
    print(time.gmtime(timestamp))
    print(time.localtime(timestamp))
    t = datetime.time(14, 53)
    print(t.strftime("%H:%M:%S"))

    c = calendar.Calendar()
    for iter in c.itermonthdays2(2019, 11):
        print(iter, end=" ")
    c = calendar.Calendar(6)
    calendar.setfirstweekday = 6
    print(calendar.calendar(2000))
    date1 = datetime.date(1992, 2, 1)
    date2 = datetime.date(1993, 2, 1)
    print(date2-date1)
    dt1 = datetime.datetime(1992, 3, 2, 5, 5, 5)
    dt2 = datetime.datetime(1992, 3, 1, 0, 0, 0)
    print(dt1-dt2)
    print(hasattr(A(), 'a'))

    