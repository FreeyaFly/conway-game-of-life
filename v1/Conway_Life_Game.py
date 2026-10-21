# Python3.8+

import math
import time
from tkinter import messagebox as msgbox, messagebox
import tkinter as tk
import webbrowser
import random



class Lifes:
    def __init__(self, rows=36, cols=36):
        self.row = rows + 2
        self.col = cols + 2
        self.items = [[0] * self.col for _ in range(self.row)]
        self.history = []
        self.historySize = 50
        self.running = False
        self.runningSpeed = 100
        self.circleNum=0

    def rndinit(self, rate=0.1):
        self.history = []
        for i in range(self.row):
            for j in range(self.col):
                rnd = random.random()
                if rnd > 1 - rate:
                    self.items[i][j] = 1

    def reproduce(self):
        new = [[0] * self.col for _ in range(self.row)]
        self.add_history()
        if len(self.history) > self.historySize:
            self.history.pop(0)
        for i in range(self.row):
            for j in range(self.col):
                if i * j == 0 or i == self.row - 1 or j == self.col - 1:
                    new[i][j] = 0
                else:
                    lifes = 0
                    for m in range(i - 1, i + 2):
                        for n in range(j - 1, j + 2):
                            if m == i and n == j:
                                continue
                            lifes += self.items[m][n]
                    if self.items[i][j]:
                        if lifes == 2 or lifes == 3:
                            new[i][j] = 1
                        else:
                            new[i][j] = 0
                    else:
                        if lifes == 3:
                            new[i][j] = 1
        for idx, narray in enumerate(new):
            self.items[idx] = narray

    def is_stable(self):
        if len(self.history) < self.historySize:
            return False
        arr = []
        for i in self.history:
            if i not in arr:
                arr.append(i)
        if len(arr) < 10:
            return True
        return False

    def add_history(self, Items=None):
        arr = []
        if Items == None:
            Items = self.items[:]
        for item in Items:
            b = 0
            for i, n in enumerate(item[::-1]):
                b += n * 2 ** i
            arr.append(b)
        self.history.append(arr)
        self.circleNum+=1




def drawCanvas():
    global tv,isclear
    tv = tk.Canvas(win, width=win.winfo_width(), height=win.winfo_height())
    tv.pack(side="top")
    isclear =True

def drawLifes():
    R, XY = 8, [50 + i * size for i in range(num)]
    if Life.running:
        for i, x in enumerate(XY):
            for j, y in enumerate(XY):
                if Life.items[i + 1][j + 1]:
                    tv.itemconfig(rect[i][j], fill='green', outline='green')
                else:
                    tv.itemconfig(rect[i][j], fill='lightgray', outline='lightgray')
        tv.update()
        Life.reproduce()
        varCycle.set(Life.circleNum)

        tLabelCycle = tk.Label(win, width=15, height=1,text=str("当前周期数:{}".format(varCycle.get())))
        tLabelCycle.place(x=830, y=445)
        tLabelCycle.config(justify=tk.LEFT, anchor="nw", borderwidth=10, wraplength=210)

        if Life.is_stable():
            Life.running = False
            if sum(sum(Life.items, [])):
                msgbox.showinfo('Message', '生命繁殖与湮灭进入稳定状态！')
            else:
                msgbox.showinfo('Message', '生命全部湮灭，进入死亡状态！')
    win.after(Life.runningSpeed, drawLifes)


def GenTable():
    global isclear,rect
    if isclear:
        pass
    else:
        tv.delete(tk.ALL)
    try:
        isclear =False
        global  num,size,Life

        # 获取的值，转为浮点数，如果不能转捕获异常
        num = int(tEntryRowCol.get())
        size = math.floor(720/num)

        ## 画格子
        for i in range(num):
            coord = 40, 40, num*size+40, i * size + 40
            tv.create_rectangle(coord)
            coord = 40, 40, i * size + 40, num*size+40
            tv.create_rectangle(coord)

        coord = 38, 38, num*size+40, num*size+40
        tv.create_rectangle(coord, width=2)

        coord = 39, 39, num*size+40, num*size+40
        tv.create_rectangle(coord, width=2)

        coord = 38, 38, num*size+42, num*size+42
        tv.create_rectangle(coord, width=2)


        R, XY = 8, [50 + i * size for i in range(num)]
        rect = [[0] * num for _ in range(num)]
        for i, x in enumerate(XY):
            for j, y in enumerate(XY):
                rect[i][j] = tv.create_rectangle(x - R, y - R, x + R + size - 20, y + R + size - 20,
                                                 tags=('imgButton1'))

                tv.itemconfig(rect[i][j], fill='lightgray', outline='lightgray')
        tv.tag_bind('imgButton1', '<Button-1>', on_Click)


        Life = Lifes(rows=num, cols=num)
        drawLifes()

    except:
        messagebox.showwarning('警告','请输入数字')

def StartLife():
    if sum(sum(Life.items, [])):
        Life.history = []
        Life.running = True
    else:
        msgbox.showinfo('Message', '请点击小方块填入活细胞，或者使用随机功能！')

def BreakLife():
    Life.running = not Life.running
    if Life.running:
        Life.history.clear()
        Life.add_history()


def RandomLife():
    Life.rndinit()
    Life.running = True
    tLabelCycle = tk.Label(win, width=15, height=1, text=str("当前周期数:0"))
    tLabelCycle.place(x=830, y=445)
    tLabelCycle.config(justify=tk.LEFT, anchor="nw", borderwidth=10, wraplength=210)


def ClearLife():
    tLabelCycle = tk.Label(win, width=15, height=1, text=str("当前周期数:0"))
    tLabelCycle.place(x=830, y=445)
    tLabelCycle.config(justify=tk.LEFT, anchor="nw", borderwidth=10, wraplength=210)
    Life.running = False
    Life.history = []
    Life.items = [[0] * (num+2) for _ in range((num+2))]
    Life.circleNum =0   ### 解决周期数没彻底清零的问题
    for x in range(num):
        for y in range(num):
            tv.itemconfig(rect[x][y], fill='lightgray', outline='lightgray')


def btnCommand(i):
    if i == 0:
        return GenTable
    if i == 1:
        return StartLife
    elif i == 2:
        return BreakLife
    elif i == 3:
        return RandomLife
    elif i == 4:
        return ClearLife


def on_Enter(event):
    tCanvas.itemconfig(tVisit, fill='orange')


def on_Leave(event):
    tCanvas.itemconfig(tVisit, fill='green')


def on_Release(event):
    url = 'https://conwaylife.com/forums/'
    webbrowser.open(url, new=0, autoraise=True)


def on_Click(event):
    #print(event.x,event.y)
    x, y = (event.x - 40) // size, (event.y - 40) // size
    if not Life.running:
        if Life.items[x + 1][y + 1]:
            tv.itemconfig(rect[x][y], fill='lightgray', outline='lightgray')
        else:
            tv.itemconfig(rect[x][y], fill='green', outline='green')
        Life.items[x + 1][y + 1] = not Life.items[x + 1][y + 1]


def on_Close():
    if msgbox.askokcancel("Quit", "Do you want to quit?"):
        Life.running = False
        print(Copyright())
        win.destroy()


def Introduce():
    txt = '''【康威生命游戏】\n\n生存定律：
    (1)当前细胞为死亡状态时，如果它周围8格中有恰好3个活细胞，下一回合该细胞变成活细胞（模拟繁殖）。
    (2)当前细胞为存活状态时，当它周围的活细胞<2个时，下一回合该细胞变成死细胞（数量稀少）。
    (3)当前细胞为存活状态时，当它周围的活细胞>3个时，下一回合该细胞变成死细胞（数量过多）。
    (4)当前细胞为存活状态时，如果它周围8格中有2或3个活细胞，下一回合该细胞继续存活。'''
    return txt


def Copyright():
    return "Conway's Game of Life\nVer1.0, March 2023"


if __name__ == '__main__':

    # 新建窗口
    win = tk.Tk()
    X, Y = win.maxsize()
    W, H = 1024, 800
    winPos = f'{W}x{H}+{(X - W) // 2}+{(Y - H) // 2}'
    win.geometry(winPos)

    # 不可resize
    win.resizable(False, False)

    # 标题
    win.title('康威生命游戏模拟器')
    win.update()

    # 新建画布
    drawCanvas()


    tLabel = tk.Label(win, width=30, height=20, background='lightgray')
    tLabel.place(x=780, y=38)
    tLabel.config(text='\n\n\n'.join((Introduce(), Copyright())))
    tLabel.config(justify=tk.LEFT, anchor="nw", borderwidth=10, wraplength=210)




    #### 新增
    tLabel = tk.Label(win, width=30, height=20)
    tLabel.place(x=830, y=405)
    tLabel.config(text='行列数')
    tLabel.config(justify=tk.LEFT, anchor="nw", borderwidth=10, wraplength=210)

    tEntryRowCol = tk.Entry(win, width=20)
    tEntryRowCol.place(x=880, y=410, width=75,height=30)


    # 周期数变量
    varCycle = tk.IntVar()  # 保存为一个int类型的变量
    varCycle.set(0)  # 设置初始值


    tButton = [None] * 5
    bX, bY, dY = 835, 490, 50
    txt = ['生成','开始', '暂停', '随机', '清空']
    for i in range(5):
        tButton[i] = tk.Button(win, text=txt[i], command=btnCommand(i))
        tButton[i].place(x=bX, y=bY + dY * i, width=120, height=40)



    tCanvas = tk.Canvas(win, width=200, height=45)
    tCanvas.place(x=800, y=760)
    tVisit = tCanvas.create_text((88, 22), text=u"点此访问康威生命游戏论坛...")
    tCanvas.itemconfig(tVisit, fill='green', tags=('btnText'))
    tCanvas.tag_bind('btnText', '<Enter>', on_Enter)
    tCanvas.tag_bind('btnText', '<Leave>', on_Leave)
    tCanvas.tag_bind('btnText', '<ButtonRelease-1>', on_Release)
    win.protocol("WM_DELETE_WINDOW", on_Close)
    win.mainloop()
