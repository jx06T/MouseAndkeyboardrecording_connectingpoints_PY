# import keyboard
import time
import json
import pynput
import threading
import tkinter as tk
from tkinter import filedialog
import os
from tkinter import ttk
import ctypes
from tkinter import messagebox
PROCESS_PER_MONITOR_DPI_AWARE = 2  # 解决由于屏幕分辨率缩放导致的，pynput监听鼠标位置不准的问题
ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)

key_dict = {
    "\\x01": ['a'],
    "\\x02": ['b'],
    "\\x03": ['c'],
    "\\x04": ['d'],
    "\\x05": ['e'],
    "\\x06": ['f'],
    "\\x07": ['g'],
    "\\x08": ['h'],
    "\\t": ['i'],
    "\\n": ['j'],
    "\\x0b": ['k'],
    "\\x0c": ['l'],
    "\\r": ['m'],
    "\\x0e": ['n'],
    "\\x0f": ['o'],
    "\\x10": ['p'],
    "\\x11": ['q'],
    "\\x12": ['r'],
    "\\x13": ['s'],
    "\\x14": ['t'],
    "\\x15": ['u'],
    "\\x16": ['v'],
    "\\x17": ['w'],
    "\\x18": ['x'],
    "\\x19": ['y'],
    "\\x1a": ['z'],
    "\\x1f": ['-'],
    "<186>": [';'],
    "<187>": ['='],
    "<189>": ['-'],
    "<192>": ['`'],
    "<222>": ["'"],
    "<48>": ['0'],
    "<49>": ['1'],
    "<50>": ['2'],
    "<51>": ['3'],
    "<52>": ['4'],
    "<53>": ['5'],
    "<54>": ['6'],
    "<55>": ['7'],
    "<56>": ['8'],
    "<57>": ['9'],
    "'~'": ['`'],
    "'!'": ['1'],
    "'@'": ['2'],
    "'#'": ['3'],
    "'$'": ['4'],
    "'%'": ['5'],
    "'^'": ['6'],
    "'*'": ['7'],
    "'('": ['8'],
    "')'": ['9'],
    "'_'": ['-'],
    "'+'": ['='],
    "':'": [';'],
    "'\"'": ["'"],
    "'<'": [","],
    "'{'": ["["],
    "'}'": ["]"],
    "'|'": ["\\"],
    "'?'": ["/"],
}


def on_move(x, y):
    if mouselogger[-1][1] == 0 and time.time() - startTime - mouselogger[-1][0] < 0.1:
        return
    if State != 1 and State != 2:
        return False
    if State == 2:
        return
    mouselogger.append((time.time() - startTime, 0, (x, y)))
    # print(x, y)


def on_click(x, y, button, pressed):
    if State == 2:
        return
    mouselogger.append((time.time() - startTime, 1,
                       (x, y), str(button), pressed))
    # print(button,pressed,x, y)


def on_scroll(x, y, dx, dy):
    if State == 2:
        return
    mouselogger.append((time.time() - startTime, 2, (x, y), dx, dy))
    # print(x,y,dy)


def on_press(key):
    global State
    if State != 1 and State != 2:
        return False

    if key == pynput.keyboard.Key.f7:
        return False

    if State == 2:
        if key == pynput.keyboard.Key.f8:
            global startTime
            startTime += (time.time() - g.stopTime)-0.1
            g.button2.configure(text="暫停")
            State = 1
        return
    else:
        if key == pynput.keyboard.Key.f8:
            g.stopTime = time.time()
            g.button2.configure(text="繼續")
            State = 2
            return
        
    if str(key) == '\"\'\"':
        keylogger.append((time.time() - startTime, True, "'"))
        return
    if keylogger[-1][2] == str(key).strip("'") and time.time() - startTime - keylogger[-1][0] < 0.05 and keylogger[-1][1]:
        return

    keylogger.append((time.time() - startTime, True, str(key).strip("'")))


def on_release(key):
    if key == pynput.keyboard.Key.f7 or key == pynput.keyboard.Key.f8 :
        return 
    if State == 2:
        return
    if str(key) == '\"\'\"':
        keylogger.append((time.time() - startTime, False, "'"))
        return
    keylogger.append((time.time() - startTime, False, str(key).strip("'")))


def mouse1():
    # Collect events until released
    with pynput.mouse.Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll) as listener:
        listener.join()


def keyboard1():
    with pynput.keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()
    keylogger.append((time.time() - startTime, False, "end"))
    # print(keylogger)
    g.button1.configure(text="錄製")
    g.button2.configure(text="暫停")

    global State
    State = 0


def savejson(this):  # str
    name = filedialog.asksaveasfilename(initialdir=".", initialfile=g.text_box.cget(
        "text"), defaultextension=".json")
    if not name:
        return
    with open(name, "w") as f:
        a = {"key": keylogger, "mouse": mouselogger}
        f.write(json.dumps(a))
    g.text_box.configure(text=os.path.basename(name))


def openjson(this):
    name = filedialog.askopenfilename(initialdir=".", filetypes=[
                                      ('JSON Files', '*.json')])
    if not name:
        return
    try:
        with open(name) as f:
            a = json.loads(f.read())
            global keylogger
            global mouselogger
            keylogger = a["key"]
            mouselogger = a["mouse"]
        g.text_box.configure(text=os.path.basename(name))
    except:
        print(name)


def play(a):
    if a == 0:
        try:
            d = float(g.text_box3.get())
        except ValueError:
            d = 1
        if d == -1:
            d = -3
        g.count = d

        global State
        if State == 3 or State == 4:
            State = 0
            g.count = 0
            g.button5.configure(text="撥放")
            g.button6.configure(text="暫停")
            time.sleep(0.1)
            abc()
            return

        if State != 0:
            return

    State = 3
    pmouse = threading.Thread(target=playmouse, args=(mouselogger,))
    pkey = threading.Thread(target=playkey, args=(keylogger,))
    g.button5.configure(text="中止")
    pmouse.start()
    pkey.start()
    if a == 0:
        defgg = threading.Thread(target=defg)
        defgg.start()


def playmouse(mouseall):
    mouse = pynput.mouse.Controller()
    buttons = {
        "Button.left": pynput.mouse.Button.left,
        "Button.right": pynput.mouse.Button.right,
        "Button.middle": pynput.mouse.Button.middle
    }
    j = 0
    for i in mouseall:
        if State != 3 and State != 4:
            return
        if State == 4:
            while State == 4:
                time.sleep(0.3)
                pass
        

        if g.combo.get() != "K" and i[1]!='type':
            if i[1] == 0:
                mouse.position = (i[2][0], i[2][1])
            elif i[1] == 1:
                mouse.position = (i[2][0], i[2][1])
                if i[4]:
                    time.sleep(0.1)
                    mouse.press(buttons[i[3]])
                else:
                    mouse.release(buttons[i[3]])

            elif i[1] == 2:
                mouse.position = (i[2][0], i[2][1])
                mouse.scroll(i[3], i[4])

        if j + 1 == len(mouseall):
            return
        try:
            d = float(g.text_box2.get())
        except ValueError:
            d = 1
        if d < 0:
            d = 1
        print(i)
        time.sleep((mouseall[j+1][0]-mouseall[j][0])*d)
        j += 1


def playkey(keyall):
    keyboard = pynput.keyboard.Controller()
    j = 0
    global State
    for i in keyall:
        if State != 3 and State != 4:
            break
        if State == 4:
            while State == 4:
                time.sleep(0.3)
                pass

        if i[2] != "start" and i[2] != "end" and g.combo.get() != "M":
            if i[1]:
                if i[2][:3] == "Key":
                    keyboard.press(eval(i[2], {}, {
                        "Key": pynput.keyboard.Key
                    }))
                elif i[2][:1] != "\\" and i[2][:1] != "<":
                    keyboard.press(i[2])
                elif i[2] in key_dict:
                    keyboard.press(key_dict[i[2]][0])
            else:
                if i[2][:3] == "Key":
                    keyboard.release(eval(i[2], {}, {
                        "Key": pynput.keyboard.Key
                    }))
                elif i[2][:1] != "\\" and i[2][:1] != "<":
                    keyboard.release(i[2])
                elif i[2] in key_dict:
                    keyboard.release(key_dict[i[2]][0])

        if j + 1 == len(keyall):
            if g.count > 1 or g.count == -3 and State != 0 and State != 4:
                try:
                    d = float(g.text_box4.get())
                except ValueError:
                    d = 1
                if d < 0:
                    d = 0
                time.sleep(d)
                play(1)
                if g.count != -3:
                    g.count -= 1
            else:
                State = 0
                g.button5.configure(text="撥放")
                g.button6.configure(text="暫停")
                time.sleep(0.1)
                abc()
            return

        try:
            d = float(g.text_box2.get())
        except ValueError:
            d = 1
        if d < 0:
            d = 1
        time.sleep((keyall[j+1][0]-keyall[j][0])*d)
        j += 1


class GUI():
    def __init__(self):
        root = tk.Tk()
        root.geometry("350x190+300+300")
        root.title("鍵盤錄製")
        root.bind("<Map>", lambda event: self.initial())
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.root = root
        self.count = -1
        self.stopTime = 0
        frame1 = tk.Frame(self.root, pady=5, width=100)
        frame1.pack()

        self.button1 = tk.Button(frame1, text="錄製", height=1)
        self.button1.bind("<Button-1>", lambda event: recordd(0))
        self.button1.grid(row=0, column=0, padx=10, sticky="NW")

        self.button2 = tk.Button(frame1, text="暫停", height=1)
        self.button2.bind("<Button-1>", lambda event: pause(1))
        self.button2.grid(row=0, column=1, padx=10, sticky='NW')

        frame2 = tk.Frame(self.root, pady=4.5)
        frame2.pack()

        # self.text_box = tk.Entry(frame2, width=15)
        self.text_box = tk.Label(frame2, text="new_MKR.json")
        self.text_box.grid(row=0, column=0)

        self.button3 = tk.Button(frame2, text="保存", height=1)
        self.button3.bind("<ButtonRelease>", lambda event: savejson(0))
        self.button3 .grid(row=0, column=1, padx=10)

        self.button4 = tk.Button(frame2, text="匯入", height=1)
        self.button4.bind("<ButtonRelease>", lambda event: openjson(0))
        self.button4 .grid(row=0, column=2, padx=10)

        frame4 = tk.Frame(self.root, pady=4.5)
        frame4.pack()

        self.button5 = tk.Button(frame4, text="撥放", height=1)
        self.button5.bind("<Button-1>", lambda event: play(0))
        self.button5.grid(row=1, column=0, padx=10)

        self.button6 = tk.Button(frame4, text="暫停", height=1)
        self.button6.bind("<Button-1>", lambda event: pause(2))
        self.button6.grid(row=1, column=1, padx=10)

        frame3 = tk.Frame(self.root, pady=4.5)
        frame3.pack()

        a = tk.Label(frame3, text="速度").grid(row=2, column=1, padx=0)
        a = tk.Label(frame3, text="次數").grid(row=2, column=3, padx=0)
        a = tk.Label(frame3, text="間隔").grid(row=2, column=5, padx=0)
        a = tk.Label(frame3, text="模式").grid(row=2, column=7, padx=0)

        self.text_box2 = tk.Entry(frame3, width=3)
        self.text_box2.grid(row=2, column=2, padx=1)
        self.text_box2.bind("<Return>", nono)
        self.text_box3 = tk.Entry(frame3, width=3)
        self.text_box3.grid(row=2, column=4, padx=1)
        self.text_box3.bind("<Return>", nono)
        self.text_box4 = tk.Entry(frame3, width=3)
        self.text_box4.grid(row=2, column=6, padx=1)
        self.text_box4.bind("<Return>", nono)

        style = ttk.Style()
        style.theme_use("default")  # 使用預設主題
        # style.map("TCombobox", selectbackground=[("", "white")])
        style.map("TCombobox", selectbackground=[
                  ("", "#d9d9d9")], selectforeground=[("", "black")])

        values = ["KM", "K", "M"]
        self.combo = ttk.Combobox(
            frame3, values=values, width=3, state="readonly")
        self.combo.grid(row=2, column=8, padx=2)
        self.root.after(1000, self.update)

    def initial(a):
        a.text_box2.delete(0, tk.END)
        a.text_box2.insert(0, 1)
        a.text_box3.delete(0, tk.END)
        a.text_box3.insert(0, 1)
        a.text_box4.delete(0, tk.END)
        a.text_box4.insert(0, 1)
        a.combo.current(0)

    def start(a):
        a.root.mainloop()

    def update(a):
        pass
        # print(type(g.combo.get()))
        # a.root.after(100, a.update)

    def close(a):
        result = messagebox.askquestion("Save file", "是否儲存檔案", parent=g.root, 
                                 icon=messagebox.WARNING)
    
        if result == "yes":
            savejson(0)
        else:
            pass
        time.sleep(0.1)
        a.root.destroy()
        del a


def nono(e):
    e.widget.master.focus()


def recordd(a):
    d = threading.Thread(target=record, args=(a,))
    d.start()


def record(a):
    global State
    if State == -1:
        State = -2
        g.button1.configure(text="錄製")
        abc()
        return
        
    if State == 0:
        State = -1
        g.button1.configure(text="按F7開始或點擊取消")
        with pynput.keyboard.Events() as events:
            for event in events:
                if State == -2:
                    break
                if event.key == pynput.keyboard.Key.f7:
                    break
        if State == -2:
            State = 0
            return
                
        global startTime
        global keylogger
        global mouselogger
        State = 1
        mouse = threading.Thread(target=mouse1)
        keyboard = threading.Thread(target=keyboard1)
        startTime = time.time()
        keylogger = [(0, False, "start")]
        mouselogger = [(0, "type", "x,y", "!1", "!2")]
        mouse.start()
        keyboard.start()
        g.button1.configure(text="停止")
        g.button2.configure(text="暫停")

    elif State == 1 or State == 2:
        State = 0
        abc()
        g.button1.configure(text="錄製")
        g.button2.configure(text="暫停")


def pause(a):
    global State
    if State != 0:
        if a == 1:
            if State == 1:
                State = State + 1
                abc()
                g.button2.configure(text="繼續")
            elif State == 2:
                State = State - 1
                abc()
                g.button2.configure(text="暫停")
        else:
            if State == 3:
                State = State + 1
                abc()
                g.button6.configure(text="繼續")
            elif State == 4:
                State = State - 1
                abc()
                g.button6.configure(text="暫停")


def abc():
    keyboard = pynput.keyboard.Controller()
    keyboard.press(pynput.keyboard.Key.ctrl)
    time.sleep(0.01)
    keyboard.release(pynput.keyboard.Key.ctrl)


def defg():
    global State
    while True:
        if State == 0:
            break
        with pynput.keyboard.Events() as events:
            for event in events:
                if State == 0:
                    break
                if event.key == pynput.keyboard.Key.f7:
                    State = 0
                    break
                elif event.key == pynput.keyboard.Key.f8:
                    if "Press" in str(event):
                        if State % 2 == 0:
                            g.button6.configure(text="暫停")
                        else:
                            g.button6.configure(text="繼續")
                        State = 7 - State
                else:
                    pass
    g.button5.configure(text="撥放")
    g.button6.configure(text="暫停")


State = 0
# 無 錄製 暫停 撥放
#  f7 錄製/結束、撥放/結束
# f8 暫停
startTime = time.time()
keylogger = [(0, False, "start")]
mouselogger = [(0, "type", "x,y", "!1", "!2")]
g = GUI()
g.start()
