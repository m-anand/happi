import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
from bs4 import BeautifulSoup
import subprocess, json, threading, statistics, time, webbrowser
import concurrent.futures

name='haPPI'
version='0.1-beta'

# helper class for common gui widgets
class Elements:
    def __init__(self, master):
        self.master = master

    # method for all button processes
    def button(self, char, funct, lambdaVal, x_, y_, algn, rows):
        if lambdaVal == '':
            self.b = tk.Button(self.master, text=char, command=funct)
        else:
            self.b = tk.Button(self.master, text=char, command=lambda: funct(lambdaVal))
        self.b.grid(row=y_, column=x_, sticky=algn, rowspan=rows, ipadx=5, ipady=5)

    # method for calling a text entry dialog
    def textField(self, lbl, w_, x_, y_):
        textField = tk.Entry(self.master, width=w_)
        textField.grid(row=y_, column=x_ + 1, sticky=tk.W, ipadx=5, ipady=5)
        textField_lbl = tk.Label(self.master, text=lbl)
        textField_lbl.grid(row=y_, column=x_, sticky=tk.E, ipadx=5, ipady=5)
        return textField

    def check(self, char, var, x_, y_):
        check = tk.Checkbutton(self.master, text=char, variable=var)
        check.grid(column=x_, row=y_)

    def label1(self, char, x_, y_, algn, rows, cols):
        self.b = tk.Label(self.master, text=char)
        self.b.grid(row=y_, column=x_, sticky=algn, rowspan=rows, columnspan=cols)

    def label2(self, charVariable, x_, y_, algn):
        self.b = tk.Label(self.master, textvariable=charVariable)
        self.b.grid(row=y_, column=x_, sticky=algn)


class MainArea(tk.Frame):
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)




class MainApp(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        parent.title(name)
        parent.minsize(800,500)
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        # draw a viewer window
        # viewer_root=tk.Toplevel()

        # Components
        # self.viewer = Viewer(viewer_root)
        # self.menubar = Menubar(parent,self.config)
        # self.statusbar = StatusBar(parent)
        self.mainarea = MainArea(parent, borderwidth=1, relief=tk.RAISED)

        # configurations
        self.mainarea.grid(column=0, row=0, sticky='WENS')
        # self.statusbar.grid(column=0, row=1, sticky='WE')
        # self.statusbar.set('Ready')

#-----------------------------------------------------------------------------------------------------------------------


root = tk.Tk()
PR = MainApp(root)
root.mainloop()