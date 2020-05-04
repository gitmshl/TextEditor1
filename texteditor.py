import tkinter as tk
import tkinter.filedialog as fl
import tkinter.messagebox as msgbox
import math
import json

filename = ""
change_something = False

key_word_colors = {'int': 'blue'}
regexp_left = "(\W|^)"
regexp_right = "(\W|$)"


def load_color(filename):
    global key_word_colors
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
    for color in data:
        for word in data[color]:
            key_word_colors[word] = color


def init_color(file_extension):
    with open("__init__colors.txt", 'r') as f:
        lines = f.readlines()

    for filext in lines:
        if file_extension == filext.split(' ')[0]:
            load_color(filext.split(' ')[1].rstrip())
            return
    global key_word_colors
    key_word_colors = {}


def redraw_all(filename=None):
    if filename: 
        init_color(filename.split('.')[-1])
    global text, symbols, regexp_left, regexp_right
    for key_word in key_word_colors:
        color = key_word_colors[key_word]
        startIndex = '1.0'
        while True:
            startIndex = text.search(rf"{regexp_left}{key_word}{regexp_right}", startIndex, tk.END, regexp=True) # search for occurence of k
            if startIndex:
                startIndex = text.search(f"{key_word}", startIndex, tk.END)
                endIndex = text.index('%s+%dc' % (startIndex, (len(key_word)))) # find end of k
                text.tag_add(key_word, startIndex, endIndex) # add tag to k
                text.tag_config(key_word, foreground=color)      # and color it with v
                startIndex = endIndex # reset startIndex to continue searching
            else:
                break


def redraw():
    global text
    for tag in text.tag_names():
        text.tag_delete(tag)
    redraw_all()


def handle():
    global filename, change_something
    if change_something:
        answer = msgbox.askyesnocancel(title="Сохранение файла", message="Файл был изменен. Сохранить изменения?")
        if answer is True:
            save()
        elif answer is None:
            return "cancel"
    return "ok"


def open_file():
    global filename, change_something, text, root
    try:
        file_name = fl.askopenfile(mode="r", defaultextension=".txt").name
        if not file_name:
            return
    except:
        return
    
    text.delete(0.0, tk.END)
    try:
        with open(file_name, "r") as f:
            try:
                t = f.read()
                filename = file_name
                text.insert(0.0, t)
                redraw_all(filename)
                handle()
                root.title(filename.split('/')[-1])
                change_something = False
            except:
                msgbox.showerror(title="Oops ;(", message="Не получилось считать из файла!")
                return
    except:
        msgbox.showerror(title="Oops ;(", message="Не получилось открыть файл. Возможно, он используется другим процессом")
        return


def new_file():
    global filename, text, change_something, root
    handle()
    filename = None
    root.title("untitled")
    text.delete(0.0, tk.END)
    change_something = False


def save_as(file_name=None):
    global filename, text, change_something
    if not file_name:
        try:
            file_name = fl.asksaveasfile(mode="w", defaultextension=".txt").name
            if not file_name:
                return
        except:
            return
    
    filename = file_name
    t = text.get(0.0, tk.END)
    try:
        with open(filename, "w") as f:
            try:
                f.write(t.rstrip())
                change_something = False
                root.title(filename.split('/')[-1])
            except:
                msgbox.showerror(title="Oops ;(", message="Не получилось сохранить файл!")
                return
    except:
        msgbox.showerror(title="Oops ;(", message="Не получилось открыть файл. Возможно, он используется другим процессом")
        return


def save():
    global filename
    save_as(filename)


def quit():
    global root
    handle()
    root.quit()


def select_all(event):
    global text
    text.tag_add(tk.SEL, "1.0", tk.END)
    text.mark_set(tk.INSERT, "1.0")
    text.see(tk.INSERT)
    return 'break'


def tab_handle(event):
    global text
    text.insert(tk.INSERT, " " * 4)
    return "break"


def draw_lines():
    global text, prev_count_of_lines, linenumbers
    count_of_lines = int(text.index('end').split('.')[0]) - 1
    if count_of_lines != prev_count_of_lines:
        linenumbers["width"] = max(2, int(math.log(count_of_lines, 10)) + 1)
        linenumbers.delete(0.0, tk.END)
        linenumbers.insert(0.0, "".join([f"{i}\n" if i < count_of_lines else f"{i}" for i in range(1, count_of_lines + 1)]))
        prev_count_of_lines = count_of_lines


def keyrelease(event):
    global change_something, root, filename
    redraw()
    s = event.state
    draw_lines()
    ctrl  = (s & 0x4) != 0
    alt   = (s & 0x8) != 0 or (s & 0x80) != 0
    shift = (s & 0x1) != 0
    if change_something or alt or ctrl or shift:
        return
    change_something = True
    root.title(f"*{filename.split('/')[-1] if filename else 'untitled'}")


def window_close():
    global root
    if handle() == "ok":
        root.quit()


def scrollBoth(action, position, type=None):
    global text, linenumbers
    text.yview_moveto(position)
    linenumbers.yview_moveto(position)


def updateScroll(first, last, type_=None):
    global text, linenumbers, scrllbar
    text.yview_moveto(first)
    scrllbar.set(first, last)
    draw_lines()
    linenumbers.yview_moveto(first)


def do_backspace(event):
    global text
    before = "".join([text.get("insert-4c"), text.get("insert-3c"), text.get("insert-2c"), text.get("insert-1c")])
    before = before.split('\n')[-1]
    if before == " " * 4:
        text.delete("insert -3 chars", "insert")


root = tk.Tk()
root.title("untitled")

scrllbar = tk.Scrollbar(root)
scrllbar.config(command=scrollBoth)
scrllbar.pack(side=tk.RIGHT, fill="y")

text = tk.Text(root, bg="gray12", fg="white")
text.config(insertbackground="white")
text.config(yscrollcommand=updateScroll)

prev_count_of_lines = 1
linenumbers = tk.Text(root, width=2)
linenumbers.tag_configure('line', justify='right')
linenumbers.config(bg="gray12")
linenumbers.config(fg="white")
linenumbers.insert(0.0, "1")
linenumbers.pack(fill="y", side=tk.LEFT, anchor="s")

text.pack(expand=True, fill='both', anchor='s')

menubar = tk.Menu(root)
filemenu = tk.Menu(menubar)
filemenu.add_command(label="New", command=new_file)
filemenu.add_command(label="Open", command=open_file)
filemenu.add_command(label="Save", command=save)
filemenu.add_command(label="Save as", command=save_as)
filemenu.add_separator()
filemenu.add_command(label="Quit", command=quit)
menubar.add_cascade(label="File", menu=filemenu)

root.config(menu=menubar)

text.bind("<Control-Key-a>", select_all)
text.bind("<Control-Key-A>", select_all)
text.bind("<Control-Key-s>", lambda e: save())
text.bind("<Control-Key-S>", lambda e: save())
text.bind("<Control-Key-o>", lambda e: open_file())
text.bind("<Control-Key-O>", lambda e: open_file())
text.bind("<Control-Key-n>", lambda e: new_file())
text.bind("<Control-Key-N>", lambda e: new_file())
text.bind("<Tab>", tab_handle)
text.bind("<BackSpace>", do_backspace)
text.bind("<KeyRelease>", keyrelease)

root.protocol("WM_DELETE_WINDOW", window_close)

root.mainloop()
