'''
== Classifier App ==
+ Simple GUI that allows visualization of data
for human analysis purpose
'''
import tkinter as tk
#matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import os
import csv
from astropy.io import fits
from astropy.table import Table
import numpy as np
import numpy.fft as fft
import matplotlib.pyplot as plt

class PlotCanvas(tk.Frame):
    
    def __init__(self,parent):
        
        tk.Frame.__init__(self,parent)
        
        self.f, self.ax = plt.subplots()
        
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.RIGHT,fill=tk.BOTH,expand=True)
        
        #Displays Matplotlib figure toolbar.
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

class Menu(tk.Frame):
    
    def __init__(self, parent):
        
        tk.Frame.__init__(self, parent)
        
        self.readCampaigns()
        
        self.campaign_str = tk.StringVar()
        self.campaign_str.set('Select a Campaign')
        self.campaign_menu = tk.OptionMenu(parent, self.campaign_str, *self.campaigns)
        self.campaign_menu.grid(row = 0, column = 1)
        
        frame_file_list = tk.Frame(self)
        frame_file_list.grid(row = 1, column = 1)
        
        self.scrollbar = tk.Scrollbar(frame_file_list)
        self.scrollbar.grid(row = 1, column = 1)
        
        self.list = tk.Listbox(frame_file_list, yscrollcommand = self.scrollbar.set)
        for line in range(100):
            self.list.insert(tk.END, "This is line number " + str(line))
        
        self.list.grid(row = 1, column = 0)
        self.scrollbar.config( command = self.list.yview )
        
    def readCampaigns(self):
        with open('etc/config.txt') as config:
            read = csv.reader(config, delimiter = '|')
            for line in read:
                if 'campaigns available' in line:
                    self.campaigns = []
                    for i in range(1,len(line)):
                            self.campaigns.append('Campaign ' + line[i])
    
    def listFiles(self):
        None

class MainApp(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        
        tk.Tk.wm_title(self, 'K2 Campaign Viewer')
        
        self.Canvas = PlotCanvas(self)
        self.Canvas.grid(row = 0, column = 0)
        
        self.Menu = Menu(self)
        self.Menu.grid(row = 0, column = 1, sticky = tk.E)
        

app = MainApp()
app.mainloop()        