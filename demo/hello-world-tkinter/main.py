import tkinter as tk

from argsense import cli


@cli
def hello_world() -> None:
    """
    minimal tkinter demo app.
    """
    root = tk.Tk()
    root.title("Hello World App")
    label = tk.Label(root, text="Hello, World!")
    label.pack()
    root.mainloop()


@cli
def listbox() -> None:
    # root = tk.Tk()
    # scrollbar = tk.Scrollbar(root)
    # scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    # mylist = tk.Listbox(root, yscrollcommand=scrollbar.set)
    # for line in range(100):
    #     mylist.insert(tk.END, 'This is line number' + str(line))
    # mylist.pack(side=tk.LEFT, fill=tk.BOTH)
    # scrollbar.config(command=mylist.yview)
    # root.mainloop()
    
    top = tk.Tk()
    box = tk.Listbox(top)
    box.insert(1, 'Python')
    box.insert(2, 'Java')
    box.insert(3, 'C++')
    box.insert(4, 'Any other')
    box.pack()
    top.mainloop()


if __name__ == '__main__':
    # pox demo/hello-world-tkinter/main.py hello-world
    # pox demo/hello-world-tkinter/main.py listbox
    cli.run()
