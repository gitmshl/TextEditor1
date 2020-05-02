import tkinter as tk
import tkinter.filedialog as fl
import tkinter.messagebox as msgbox

filename = ""
change_something = False


def handle():
    global filename, change_something
    if change_something:
        if msgbox.askokcancel(title="Сохранение файла", message="Файл был изменен. Сохранить изменения?"):
            save()


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
                text.insert(0.0, t)
                handle()
                filename = file_name
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
    root.title("untitled")
    text.delete(0.0, tk.END)
    change_something = False


def save_as(file_name=None):
    print("save_as function call")
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


def keypress(event):
    global change_something, root, filename
    c = event.keysym
    s = event.state
    ctrl  = (s & 0x4) != 0
    alt   = (s & 0x8) != 0 or (s & 0x80) != 0
    shift = (s & 0x1) != 0
    if change_something or alt or ctrl or shift:
        return
    change_something = True
    root.title(f"*{filename.split('/')[-1] if filename else 'untitled'}")



root = tk.Tk()
root.title("untitled")

text = tk.Text(root, bg="gray12", fg="white")
text.config(insertbackground="white")

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
text.bind("<Tab>", tab_handle)
text.bind("<KeyPress>", keypress)

root.mainloop()