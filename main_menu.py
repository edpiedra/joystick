#/usr/bin/env python

import tkinter, os, sys 

def _quit_b():
    print("[JOYSTICK] quitting...")
    menu.destroy()
    
def _goggles_b():
    print("[JOYSTICK] goggles...")
    menu.destroy()
    os.system("~/Scripts/joystick/goggles-joystick.py")
    sys.exit()
    
menu = tkinter.Tk()
menu.overrideredirect(True)
menu.geometry("240x240+0+310")

menu.configure(
    bg="#A6D4EF",
    bd=10,
)

quit_b = tkinter.Button(
    menu,
    text="QUIT",
    activebackground="#944E49",
    bd=2,
    bg="#4989C2",
    command=(_quit_b),
    fg="black",
    height=2,
    justify="center",
    padx=2,
    pady=10,
    relief="flat",
    width=25,
)

goggles_b = tkinter.Button(
    menu,
    text="GOGGLES",
    activebackground="#944E49",
    bd=2,
    bg="#4989C2",
    command=(_goggles_b),
    fg="black",
    height=2,
    justify="center",
    padx=2,
    pady=10,
    relief="flat",
    width=25,
)

quit_b.pack()
goggles_b.pack()

menu.mainloop()