import random
import tkinter as tk
import torch
import torch.nn as nn
import copy

grid = []
colors = ["white", "yellow", "red"]
canvas = tk.Canvas()
finished = False


class connect4Model(nn.Module):
    def __init__(self):
        super(connect4Model, self).__init__()
        self.fc1 = nn.Linear(42, 128)  # Layer completamente connesso 1
        self.fc2 = nn.Linear(128, 64)  # Layer completamente connesso 2
        self.fc3 = nn.Linear(64, 1)    # Layer completamente connesso 3

    def forward(self, x):
        x = x.view(-1, 42)             # Flattening dell'array di input
        x = nn.ReLU()(self.fc1(x))    # Applicazione funzione di attivazione ReLU al primo layer
        x = nn.ReLU()(self.fc2(x))    # Applicazione funzione di attivazione ReLU al secondo layer
        x = nn.Tanh()(self.fc3(x))    # Applicazione funzione di attivazione Tanh al terzo layer per ottenere valore tra -1 e 1
        return x


model = torch.load('connect4Model_epoch010.pth')


def protecc():
    global grid

    for col in range(7):
        x = col
        y = -1
        while y < 5 and grid[x][y + 1] == 0:
            y += 1

        if y == -1:
            continue

        gridCopy = copy.deepcopy(grid)
        gridCopy[x][y] = 2

        for g in [list(i) for i in zip(*gridCopy)]:
            print(g)
        print()

        startings = [[0, 0], [0, 0], [0, 0], [0, 0]]
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        counters = [0, 0, 0, 0]

        # find startings
        for i in range(4):
            pos = [0, 0]
            for j in range(4):
                pos[0] -= directions[i][0]
                pos[1] -= directions[i][1]
                if x + pos[0] < 0 or x + pos[0] >= 7 or y + pos[1] < 0 or y + pos[1] >= 6:
                    break
                elif gridCopy[x][y] == gridCopy[x + pos[0]][y + pos[1]]:
                    startings[i] = [pos[0], pos[1]]
                else:
                    break

        # count from there
        for i in range(4):
            pos = startings[i]
            for j in range(4):
                pos[0] += directions[i][0]
                pos[1] += directions[i][1]
                if x + pos[0] < 0 or x + pos[0] >= 7 or y + pos[1] < 0 or y + pos[1] >= 6:
                    break
                elif gridCopy[x][y] == gridCopy[x + pos[0]][y + pos[1]]:
                    counters[i] += 1
                else:
                    break

        if max(counters) >= 3:
            return x, y

    return -1, -1




def botChoosing():
    global grid  # user = 2
    global model

    x, y = protecc()

    if x == -1:
        bestCol = -1
        maxScore = -1
        for col in range(7):
            x = col
            y = -1
            while y < 5 and grid[x][y + 1] == 0:
                y += 1

            if y == -1:
                continue

            gridCopy = copy.deepcopy(grid)
            gridCopy[x][y] = 1

            vet = [el for sublist in gridCopy for el in sublist]
            vet = [el if el < 2 else -1 for el in vet]
            modelInput = torch.tensor(vet, dtype=torch.float32)

            modelOutput = model(modelInput)
            if float(modelOutput) > maxScore:
                maxScore = float(modelOutput)
                bestCol = x

        if bestCol == -1:
            bestCol = random.randint(0, 6)

        x, y = bestCol, -1
        while y < 5 and grid[x][y + 1] == 0:
            y += 1

    return x, y


def click(event):
    global grid
    global colors
    global canvas
    global finished

    if finished:
        return

    clicked_tag = event.widget.gettags(tk.CURRENT)
    if clicked_tag:
        # click dell'utente
        shape_id = clicked_tag[0]
        x = int(shape_id[0])
        y = -1

        while y < 5 and grid[x][y+1] == 0:
            y += 1

        if y == -1:
            return

        shape_id = str(x)+"-"+str(y)

        canvas.itemconfig(shape_id, fill="red")
        grid[x][y] = 2

        check(shape_id, True)

        if not finished:
            # random click del bot
            x, y = botChoosing()

            shape_id = str(x) + "-" + str(y)
            canvas.itemconfig(shape_id, fill="yellow")
            grid[x][y] = 1
            check(shape_id, False)


def check(shape_id, userTurn):
    global grid
    global colors
    global canvas
    global finished

    x = int(shape_id[0])
    y = int(shape_id[2])

    startings = [[0, 0], [0, 0], [0, 0], [0, 0]]
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    counters = [0, 0, 0, 0]

    # find startings
    for i in range(4):
        pos = [0, 0]
        for j in range(4):
            pos[0] -= directions[i][0]
            pos[1] -= directions[i][1]
            if x+pos[0] < 0 or x+pos[0] >= 7 or y+pos[1] < 0 or y+pos[1] >= 6:
                break
            elif grid[x][y] == grid[x+pos[0]][y+pos[1]]:
                startings[i] = [pos[0], pos[1]]
            else:
                break

    # count from there
    for i in range(4):
        pos = startings[i]
        for j in range(4):
            pos[0] += directions[i][0]
            pos[1] += directions[i][1]
            if x+pos[0] < 0 or x+pos[0] >= 7 or y+pos[1] < 0 or y+pos[1] >= 6:
                break
            elif grid[x][y] == grid[x+pos[0]][y+pos[1]]:
                counters[i] += 1
            else:
                break

    if max(counters) >= 3:
        if userTurn:
            print("User win!")
        else:
            print("Computer win!")
        finished = True


canvas.create_rectangle(10, 10, 710, 610, outline="black", fill="blue", width=2)

for i in range(7):
    grid.append([])
    for j in range(6):
        grid[i].append(0)

for i in range(7):
    for j in range(6):
        el = canvas.create_oval(20 + i * 100, 20 + j * 100, 100 + i * 100, 100 + j * 100,
                                outline="black", fill=colors[0], width=2, tags=str(i) + "-" + str(j))
        canvas.tag_bind(el, "<Button-1>", click)

canvas.configure(width=720, height=620)
canvas.pack()
canvas.mainloop()
