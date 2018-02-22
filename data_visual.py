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
        self.campaign_str.set(self.campaigns[0])
        
        self.campaign_menu = tk.OptionMenu(self, self.campaign_str, *self.campaigns)
        self.campaign_menu.grid(row = 0, column = 0, sticky = tk.N)
        
        self.listFiles()
        
        frame_file_list = tk.Frame(self)
        frame_file_list.grid(row = 1, column = 0)
        
        self.scrollbar = tk.Scrollbar(frame_file_list)
        self.scrollbar.grid(row = 0, column = 1)
        
        self.list = tk.Listbox(frame_file_list, yscrollcommand = self.scrollbar.set, width = 16)
        for file in self.filelist:
            self.list.insert(tk.END, file)
        
        self.list.grid(row = 0, column = 0)
        self.scrollbar.config(command = self.list.yview)
        
    def readCampaigns(self):
        with open('etc/config.txt') as config:
            read = csv.reader(config, delimiter = '|')
            for line in read:
                if 'campaigns available' in line:
                    self.campaigns = []
                    self.campaign_nums = []
                    for i in range(1,len(line)):
                            self.campaigns.append('Campaign ' + line[i])
                            self.campaign_nums.append(line[i])
                    self.campaign_dic = dict(zip(self.campaigns, self.campaign_nums))
    
    def listFiles(self):
        directory = 'k2c' + self.campaign_dic[self.campaign_str.get()] + '/data/'
        self.filelist = os.listdir(directory)

class MainApp(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        
        tk.Tk.wm_title(self, 'K2 Campaign Viewer')
        
        self.Canvas = PlotCanvas(self)
        self.Canvas.grid(row = 0, column = 0)
        
        self.Menu = Menu(self)
        self.Menu.grid(row = 0, column = 1, sticky = tk.N+tk.S)
        

app = MainApp()
app.mainloop()        