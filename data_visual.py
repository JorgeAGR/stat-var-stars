'''
== Classifier App ==
+ Simple GUI that allows visualization of data
for human analysis purpose
- Implement flag updating
- Add a search bar
'''
import tkinter as tk
#matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import os
import csv
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# == Data Classes == #

class Object(object):
    
    def __init__(self, file, flagdir):
        self.file = file  #String of name of the file
        self.flagdir = flagdir
        
        self.titles = []
        self.values = []
        
        with fits.open(self.file) as hdul:
            for i in range(len(hdul)):
                for title in hdul[i].header:
                    if title not in ('SIMPLE', 'BITPIX', 'NAXIS', 'EXTEND', 'EXTNAME'):
                        if i == 0:
                            self.titles.append(title)
                            if title in ('KEPLERID', 'EPIC','CAMPAIGN','MODULE','CHANNEL'):
                                self.values.append(int(hdul[i].header[title]))
                            else:
                                if hdul[i].header[title] == '':
                                    self.values.append('N/A')
                                else:
                                    try:
                                        self.values.append(round(float(hdul[i].header[title]), 3))
                                    except:
                                        self.values.append(hdul[i].header[title])
                        elif i == 3:
                            if title in ('TTYPE1'):
                                self.titles.append(hdul[i].header[title])
                                self.values.append(hdul[i].data[hdul[i].header[title]][-1])
                        else:
                            if title in ('TTYPE1', 'TTYPE2', 'TTYPE3'):
                                self.titles.append(hdul[i].header[title])
                                self.values.append(hdul[i].data[hdul[i].header[title]])
                            if title in ('TUNIT1', 'TUNIT2', 'TUNIT3'):
                                self.titles.append(hdul[i].header['TTYPE'+title[-1]]+' UNIT')
                                self.values.append(hdul[i].header[title])
        
        self.cards = dict(zip(self.titles,self.values))
        
        self.FLAGS = []
        with open(self.flagdir) as file:
            for line in file:
                self.FLAGS.append(line)
    
    def setFlag(self, integer):
        with open(self.flagdir, 'a') as file:
            file.write('\n')
            file.write(str(integer))
                

# == GUI Classes == #

class PlotCanvas(tk.Frame):
    
    def __init__(self,parent):
        
        tk.Frame.__init__(self,parent)
        
        self.f, self.ax = plt.subplots()
        
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.RIGHT,fill=tk.BOTH,expand=True)
        
        #Displays Matplotlib figure toolbar.
        #self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        #self.toolbar.update()
        #self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

class Menu(tk.Frame):
    
    def __init__(self, parent):
        
        tk.Frame.__init__(self, parent)
        
        self.readCampaigns()
        
        self.campaign_str = tk.StringVar()
        self.campaign_str.set(self.campaigns[0])
        
        self.campaign_menu = tk.OptionMenu(self, self.campaign_str, *self.campaigns, command = self.menuTrigger)
        self.campaign_menu.grid(row = 0, column = 0, sticky = tk.N)
        
        frame_file_list = tk.Frame(self)
        frame_file_list.grid(row = 1, column = 0)
        
        self.scrollbar = tk.Scrollbar(frame_file_list)
        self.scrollbar.grid(row = 0, column = 1, sticky = 'NS')
        
        self.list = tk.Listbox(frame_file_list, yscrollcommand = self.scrollbar.set, width = 16)
        self.list.grid(row = 0, column = 0, sticky = 'NS')
        self.scrollbar.config(command = self.list.yview)
        
        self.listFiles()
        
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
        self.filelist = np.sort(self.filelist)
        self.list.delete(0,tk.END)
        for file in self.filelist:
            self.list.insert(tk.END, file)
    
    def menuTrigger(self, event):
        self.listFiles()
    
    def selectedFile(self):
        self.file = 'k2c'+ self.campaign_dic[self.campaign_str.get()] + '/data/' + self.list.get(tk.ACTIVE)
        self.flagdir = 'k2c' + self.campaign_dic[self.campaign_str.get()] + '/flags/' + self.list.get(tk.ACTIVE)[0:9] + '.txt'
        return self.file, self.flagdir

class PlotTools(tk.LabelFrame):
    
    def __init__(self,parent, pltax):
        
        tk.LabelFrame.__init__(self,parent, text = pltax)
        
        #Labels for 'Min' and 'Max'
        minlabel = tk.Label(self,text = 'Min')
        minlabel.grid(row=0,column=1)
        maxlabel = tk.Label(self, text = 'Max')
        maxlabel.grid(row=0,column = 2)      
        
        #This label simply marks X as to identify its corresponding entry boxes
        xtools = tk.Label(self,text='X')
        xtools.grid(row = 1, column = 0,padx = 5)
        
        #Entry box for X Minimum
        self.minrangex = tk.Entry(self,width = 6)
        self.minrangex.grid(row=1,column=1,padx=5)
        
        #Entry box for X Maximum
        self.maxrangex = tk.Entry(self,width = 6)
        self.maxrangex.grid(row=1,column=2,padx=5)
        
        #Previous descriptions repeat accordingtly to Y and Z as well
        ytools = tk.Label(self,text='Y')
        ytools.grid(row = 2, column = 0, padx = 5, pady = (0,5))
        
        self.minrangey = tk.Entry(self,width = 6)
        self.minrangey.grid(row = 2, column = 1, padx = 5)
        
        self.maxrangey = tk.Entry(self,width = 6)
        self.maxrangey.grid(row = 2, column = 2, padx = 5)
    
    def clearEntries(self):
        
        self.minrangex.delete(0,tk.END)
        self.maxrangex.delete(0,tk.END)
        self.minrangey.delete(0,tk.END)
        self.maxrangey.delete(0,tk.END)
        
class Display(tk.LabelFrame): #WORK ON THIS
    
    def __init__(self,parent):
        
        tk.LabelFrame.__init__(self, parent, text = 'Info')
        self.frame = tk.Frame(self)
        self.frame.pack(fill=tk.X, expand=True)
        
        
    def init(self,file, flagdir):
        self.frame.destroy()
        self.frame = tk.Frame(self)
        self.frame.pack()
        obj = Object(file, flagdir)
        i = 0
        for title in obj.cards:
            tk.Label(self.frame, text = title + ': ' + str(obj.cards[title])).grid(row = i, sticky = 'W')
            i += 1
            if title == 'E_EBV':
                return

# == Main Class == #
    
class MainApp(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        
        tk.Tk.wm_title(self, 'K2 Campaign Viewer')
        
        plots = tk.Frame(self)
        #plots.grid(row = 0, column = 0, sticky = 'NEWS')
        plots.pack(side = tk.LEFT, expand = True, fill = tk.BOTH)
        
        self.CanvasLC = PlotCanvas(plots)
        #self.CanvasLC.grid(row = 0, column = 0, sticky = 'NEWS')
        self.CanvasLC.pack(expand = True, fill = tk.BOTH)
        
        self.CanvasA_LS = PlotCanvas(plots)
        #self.CanvasA_LS.grid(row = 1, column = 0, sticky = 'NEWS')
        self.CanvasA_LS.pack(expand = True, fill = tk.BOTH)
        
        sidebar = tk.Frame(self)
        #sidebar.grid(row = 0, column = 1, sticky = 'NS')
        sidebar.pack(side = tk.LEFT, fill = tk.Y)
        
        self.Menu = Menu(sidebar)
        #self.Menu.grid(row = 0, column = 1, sticky = 'NS')
        self.Menu.grid(row = 0, sticky = 'NS', pady = (0,5))
        
        self.LCTools = PlotTools(sidebar, 'Lightcurve')
        self.LCTools.grid(row = 1, sticky = 'NS', pady = 5)
        
        self.ASTools = PlotTools(sidebar, 'Amplitude Spectrum')
        self.ASTools.grid(row = 2, sticky = 'NS', pady = 5)
        
        self.Display = Display(sidebar)
        #self.Display.grid(row = 1, column = 1, sticky = 'NS')
        self.Display.grid(row = 3, sticky = 'NS', pady = 5)
        
        #self.columnconfigure(0, weight = 10)
        #self.rowconfigure(0, weight = 10)
        #self.rowconfigure(1, weight = 10)
        
        self.Menu.list.bind('<<ListboxSelect>>', self.selectFile)
        self.bind(1, self.numberPress)
        self.bind(2, self.numberPress)
        self.bind(3, self.numberPress)
        self.bind(4, self.numberPress)
    
    def selectFile(self,event):
        file = self.Menu.selectedFile()
        self.plot(file[0], file[1])
        self.Display.init(file[0], file[1])
    
    def numberPress(self,event):
        self.updateFlag(event.keysym)
    
    def updateFlag(self,integer):
        self.obj.setFlag(integer)
        self.plot(self.obj.file, self.obj.flagdir)
    
    def plot(self,file,flagdir):
        
        # Maybe use Object class to manage all this file info
        #file = 'k2c'+ self.Menu.campaign_dic[self.Menu.campaign_str.get()] + '/data/' + self.Menu.list.get(tk.ACTIVE)
        
        self.obj = Object(file, flagdir)
        time = self.obj.cards['TIME']
        lc = self.obj.cards['LC']
        freq = self.obj.cards['FREQS']
        als = self.obj.cards['AMP_LOMBSCARG']
        flag = self.obj.FLAGS[-1]
        
        time = time - time[0]
        
        self.CanvasLC.ax.clear()
        plt.figure(1)
        #self.CanvasLC.ax.
        plt.plot(time, lc)
        #self.CanvasLC.ax.set_xticks(np.arange(min(time), max(time)+1,10000))
        plt.title('Object ID: ' + str(self.obj.cards['EPIC']) + '   Flag: ' + str(flag), fontsize = 14)
        plt.xlim(0,None)
        plt.xlabel('Time $(d)$')
        plt.ylabel('Amplitude $(ppm)$')
        plt.ticklabel_format(style = 'sci', scilimits = (0,0), axis = 'y', useMathText = False)
        plt.grid()
        
        self.CanvasA_LS.ax.clear()
        plt.figure(2)
        #self.CanvasA_LS.ax.
        plt.plot(freq, als)
        plt.xlim(0,None)
        plt.ylim(0,None)
        plt.xlabel('Cycles per Day $(1/d)$')
        plt.ylabel('Amplitude $(ppm)$')
        plt.ticklabel_format(style = 'sci', scilimits = (0,0), axis = 'y', useMathText = False)
        plt.grid()
        
        self.CanvasLC.f.canvas.draw()
        self.CanvasA_LS.f.canvas.draw()

app = MainApp()
app.mainloop()        