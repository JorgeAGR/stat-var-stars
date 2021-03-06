'''
== Classifier App ==
+ Simple GUI that allows visualization of data
for human analysis purpose
'''
import matplotlib as mpl
mpl.use('TkAgg')
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import os
import sys
import csv
from astropy.io import fits
import numpy as np
import subprocess
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.backends.backend_pdf import PdfPages
import PyPDF2 as pypdf2
import pandas as pd

#mpl.use('PDF')

# == Functions & Global Variables == #

parameters = np.load('etc/tnldict.npz')
flags = np.load('etc/flagarray.npy')
stars = parameters['stars']
vals = list(map(list, zip( parameters['teff'], parameters['logg'], flags)))#parameters['flag'] )))

starlist = dict(zip(stars,vals))

def flag2label(n):
    if n == 1:
        return r'$\delta$ Sct'
    elif n == 2:
        return r'$\gamma$ Dor'
    elif n == 3:
        return r'$\delta / \gamma$ Hybrid'
    elif n == 4:
        return 'Binary'
    elif n == 5:
        return 'LFO'
    elif n == 6:
        return 'HFO'
    elif n == 7:
        return 'Interesting'
    elif n == 0:
        return 'Junk'

def str2float(x, neg):
    try:
        return float(x)
    except:
        if neg:
            return -np.inf
        else:
            return np.inf

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
                                    self.values.append(np.nan)
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
        
        self.f, self.ax = plt.subplots(2, figsize = (25, 6))
        plt.subplots_adjust(hspace = 0.5)
        
        self.axlc = self.ax[0]
        self.axas = self.ax[1]
        
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        #click = self.f.canvas.mpl_connect('scroll_event', self.onclick)
        
    #def onclick(self, event):
        #print('you pressed', event.button, event.xdata, event.ydata)

class WindowCanvas(tk.Frame):
    
    def __init__(self,parent):
        
        tk.Frame.__init__(self,parent)
        
        self.f, self.ax = plt.subplots()
        
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.X, expand=True)

class TabMenu(tk.Frame): # Section of sidebar containing main option and buttons to view the other menus.
    
    def __init__(self,parent):
        
        tk.Frame.__init__(self, parent)
        
        tabs = tk.Frame(self)
        tabs.grid(row = 0, sticky = tk.E+tk.W)
        
        tabs.columnconfigure(0, weight = 1)
        tabs.columnconfigure(1, weight = 1)
        
        self.showSearch = tk.Label(tabs, text = 'Search', relief = tk.SUNKEN, width = 7)
        self.showSearch.grid(row = 0, column = 0)
        
        self.showTools = tk.Label(tabs, text = 'Plot', relief = tk.RAISED, width = 7)
        self.showTools.grid(row = 0, column = 1)
        
        self.showTarget = tk.Label(tabs, text = 'Info', relief = tk.RAISED, width = 7)
        self.showTarget.grid(row = 0, column = 2)

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
        
        self.list = tk.Listbox(frame_file_list, yscrollcommand = self.scrollbar.set, width = 16, exportselection = False)
        self.list.grid(row = 0, column = 0, sticky = 'NS')
        self.scrollbar.config(command = self.list.yview)
        
        self.listFiles(None)
        
    def readCampaigns(self):
        with open('etc/config.txt') as config:
            read = csv.reader(config, delimiter = ',')
            for line in read:
                if 'campaigns' in line:
                    self.campaigns = []
                    self.campaign_nums = []
                    for i in range(1,len(line)):
                            self.campaigns.append('Campaign ' + line[i])
                            self.campaign_nums.append(line[i])
                    self.campaign_dic = dict(zip(self.campaigns, self.campaign_nums))
    
    def listFiles(self, searchlist):
        if searchlist:
            self.filelist = searchlist
        else:
            directory = 'k2c' + self.campaign_dic[self.campaign_str.get()] + '/data/'
            self.filelist = os.listdir(directory)
        self.filelist = np.sort(self.filelist)
        self.list.delete(0,tk.END)
        for file in self.filelist:
            self.list.insert(tk.END, file)
    
    def menuTrigger(self, event):
        self.listFiles(None)
    
    def selectedFile(self):
        self.file = 'k2c'+ self.campaign_dic[self.campaign_str.get()] + '/data/' + self.list.get(tk.ACTIVE)
        self.flagdir = 'k2c' + self.campaign_dic[self.campaign_str.get()] + '/flags/' + self.list.get(tk.ACTIVE)[0:9] + '.txt'
        return self.file, self.flagdir

class SearchTools(tk.LabelFrame):
    
    def __init__(self, parent, command):
        
        tk.LabelFrame.__init__(self, parent, text = 'Search')
        
        self.searchbar = tk.Entry(self)
        self.searchbar.grid(row = 0)
        
        ranges = tk.Frame(self)
        ranges.grid(row = 1)
        
        minlabel = tk.Label(ranges, text = 'Min')
        minlabel.grid(row = 0, column = 1, padx = 5)
        
        maxlabel = tk.Label(ranges, text = 'Max')
        maxlabel.grid(row = 0, column = 2, padx = 5)
        
        tefflabel = tk.Label(ranges, text = 'T_eff')
        tefflabel.grid(row = 1, column = 0, padx = 5)
        
        logglabel = tk.Label(ranges, text = 'log(g)')
        logglabel.grid(row = 2, column = 0, padx = 5)
        
        self.minteff = tk.StringVar()
        self.minteffentry = tk.Entry(ranges, width = 5, textvariable = self.minteff)
        self.minteffentry.grid(row = 1, column = 1, padx = 5)

        self.maxteff = tk.StringVar()
        self.maxteffentry = tk.Entry(ranges, width = 5, textvariable = self.maxteff)
        self.maxteffentry.grid(row = 1, column = 2, padx = 5)
        
        self.minlogg = tk.StringVar()
        self.minloggentry = tk.Entry(ranges, width = 5, textvariable = self.minlogg)
        self.minloggentry.grid(row = 2, column = 1, padx = 5)

        self.maxlogg = tk.StringVar()
        self.maxloggentry = tk.Entry(ranges, width = 5, textvariable = self.maxlogg)
        self.maxloggentry.grid(row = 2, column = 2, padx = 5)
        
        types = tk.Frame(self)
        types.grid(row = 2)
        
        self.dsctvar = tk.BooleanVar()
        self.dsctcheck = tk.Checkbutton(types, text = 'd Sct', variable = self.dsctvar)
        self.dsctcheck.grid(row = 0, column = 0, sticky = 'W')
        
        self.gdorvar = tk.BooleanVar()
        self.gdorcheck = tk.Checkbutton(types, text = 'g Dor', variable = self.gdorvar)
        self.gdorcheck.grid(row = 0, column = 1, sticky = 'W')
        
        self.binvar = tk.BooleanVar()
        self.bincheck = tk.Checkbutton(types, text = 'Binary' , variable = self.binvar)
        self.bincheck.grid(row = 1, column = 0, sticky = 'W')
        
        self.dghybvar = tk.BooleanVar()
        self.dghybcheck = tk.Checkbutton(types, text = r'd/g Hybrid', variable = self.dghybvar)
        self.dghybcheck.grid(row = 1, column = 1, sticky = 'W')
        
        self.intvar = tk.BooleanVar()
        self.intcheck = tk.Checkbutton(self, text = 'Interesting', variable = self.intvar)
        self.intcheck.grid(row = 3, column = 0, sticky = 'W')
        
        self.searchbutton = tk.Button(self, text = 'Search', command = command)
        self.searchbutton.grid(row = 4)

class PlotTools(tk.LabelFrame):
    
    def __init__(self, parent, label):
        
        tk.LabelFrame.__init__(self, parent, text = label)
        
        #Labels for 'Min' and 'Max'
        minlabel = tk.Label(self, text = 'Min')
        minlabel.grid(row = 0, column = 1)
        maxlabel = tk.Label(self, text = 'Max')
        maxlabel.grid(row = 0, column = 2)      
        
        #This label simply marks X as to identify its corresponding entry boxes
        xtools = tk.Label(self,text='X')
        xtools.grid(row = 1, column = 0,padx = 5)
        
        #Entry box for X Minimum
        self.minx = tk.StringVar()
        self.minrangex = tk.Entry(self,width = 6, textvariable = self.minx)
        self.minrangex.grid(row=1,column=1,padx=5)
        
        #Entry box for X Maximum
        self.maxx = tk.StringVar()
        self.maxrangex = tk.Entry(self,width = 6, textvariable = self.maxx)
        self.maxrangex.grid(row=1,column=2,padx=5)
        
        #Previous descriptions repeat accordingtly to Y and Z as well
        ytools = tk.Label(self,text='Y')
        ytools.grid(row = 2, column = 0, padx = 5, pady = (0,5))
        
        self.miny = tk.StringVar()
        self.minrangey = tk.Entry(self,width = 6, textvariable = self.miny)
        self.minrangey.grid(row = 2, column = 1, padx = 5)
        
        self.maxy = tk.StringVar()
        self.maxrangey = tk.Entry(self,width = 6, textvariable = self.maxy)
        self.maxrangey.grid(row = 2, column = 2, padx = 5)
    
    def clearEntries(self):
        
        self.minrangex.delete(0,tk.END)
        self.maxrangex.delete(0,tk.END)
        self.minrangey.delete(0,tk.END)
        self.maxrangey.delete(0,tk.END)
    
    def percentbox(self):
        tk.Label(self, text = '% Max Amp').grid(row = 3, column = 1)
        self.percent = tk.IntVar()
        self.percent.set(60)
        self.percentagebox = tk.Spinbox(self, from_ = 10, to = 100,
                                        increment = 10, width = 4, textvariable = self.percent)
        self.percentagebox.grid(row = 3, column = 2)
        
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
        #for i in range(len(obj.cards.keys())):
        while True:
            if 'TWOMASS' in obj.cards.keys():
                i += 1
                valuetitle = str(list(obj.cards.keys())[i])
                uncertaintytitle = str(list(obj.cards.keys())[i+1])
                if (i != 15) and (i >= 9):
                    tk.Label(self.frame, text = valuetitle + ': ' + 
                             str(obj.cards[valuetitle]) + ' +/- ' +
                             str(obj.cards[uncertaintytitle])).grid(row = i, sticky = 'W')
                    i += 1
                else:
                    if (i != 8):
                        tk.Label(self.frame, text = valuetitle + ': ' + str(obj.cards[valuetitle])).grid(row = i, sticky = 'W')
                if i == 33:
                    break
            else:
                i += 1
                valuetitle = str(list(obj.cards.keys())[i])
                uncertaintytitle = str(list(obj.cards.keys())[i+1])
                if (i != 14) and (i >= 8):
                    tk.Label(self.frame, text = valuetitle + ': ' + 
                             str(obj.cards[valuetitle]) + ' +/- ' +
                             str(obj.cards[uncertaintytitle])).grid(row = i, sticky = 'W')
                    i += 1
                else:
                    tk.Label(self.frame, text = valuetitle + ': ' + str(obj.cards[valuetitle])).grid(row = i, sticky = 'W')
                if i == 32:
                    break
                

class Window(tk.Toplevel):
    
    def __init__(self):
        
        tk.Toplevel.__init__(self)
        
        self.canvas = WindowCanvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.geometry('900x450')

class EntryPopUp(tk.Toplevel):
    # Find way to close this once filename set. Then use that to generate PDF. 
    def __init__(self):
        
        tk.Toplevel.__init__(self)
        self.attributes('-topmost', 'true')
        #self.geometry('200x150')
        
        text = tk.Label(self, text = 'Save file as...')
        text.grid(row = 0, column = 0, sticky = 'NSWE', padx = 3)
        
        self.input = tk.StringVar()
        self.entry = tk.Entry(self, width = 20, textvariable = self.input )
        self.entry.grid(row = 1, column = 0, sticky = 'NSWE', padx = 3)
        
        opts = ['Current Target', 'Campaign Target List']
        
        self.criteria = tk.StringVar()
        self.criteria.set(opts[1])
        optmen = tk.OptionMenu(self, self.criteria, *opts)
        optmen.grid(row = 2, column = 0, sticky = 'WE', padx = 3)
        
        close = tk.Button(self, text = 'Save', command = self.close_window)
        close.grid(row = 3, column = 0, sticky = 'WE', padx = 3)
    
    def close_window(self):
        self.input = self.input.get()
        self.criteria = self.criteria.get()
        self.destroy()

# == Main Class == #
    
class MainApp(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        
        tk.Tk.wm_title(self, 'K2 Campaign Viewer')
        
        #tk.Tk.wm_aspect(self, minNumer = 1, minDenom = 2, maxNumer = 8, maxDenom = 12)
        #tk.Tk.wm_aspect(self, minNumer = 2, minDenom = 1, maxNumer = 2 , maxDenom = 1)
        tk.Tk.wm_geometry(self, '900x600')
        
        menubar = tk.Menu(self)
        
        filemenu = tk.Menu(menubar, tearoff = 0)
        
        targetmenu = tk.Menu(filemenu, tearoff = 0)
        targetmenu.add_command(label = 'Save Target FFT', command = self.saveampls)
        filemenu.add_cascade(label = 'Current Target', menu=targetmenu)
        
        filemenu.add_command(label = "Save As PDF", command = self.savepdf)
        filemenu.add_command(label = 'Save EPIC IDs', command = self.savelist)
        filemenu.add_separator()
        filemenu.add_command(label = "Exit", command=quit)
        menubar.add_cascade(label = "File", menu=filemenu)
        
        campaignmenu = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label = 'Campaign', menu = campaignmenu)
        
        histomenu = tk.Menu(campaignmenu, tearoff = 0)
        histomenu.add_command(label = 'Temperature', command = self.temphist)
        histomenu.add_command(label = 'Log(g)', command = self.logghist)
        campaignmenu.add_cascade(label = 'Histograms', menu = histomenu)
        
        plotsmenu = tk.Menu(campaignmenu, tearoff = 0)
        plotsmenu.add_command(label = 'HR Diagram', command = self.campaignhr)
        campaignmenu.add_cascade(label = 'Plots', menu = plotsmenu)
        
        missionmenu = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label = 'Mission', menu = missionmenu)
        
        missionhistmenu = tk.Menu(missionmenu, tearoff = 0)
        missionhistmenu.add_command(label = 'Temperature', 
                                    command = self.missiontemp)
        missionhistmenu.add_command(label = 'Log(g)',
                                    command = self.missionlogg)
        missionmenu.add_cascade(label = 'Histograms', menu = missionhistmenu)
        
        missionplotmenu = tk.Menu(missionmenu, tearoff = 0)
        missionplotmenu.add_command(label = 'HR Diagram', command = self.missionhr)
        missionmenu.add_cascade(label = 'Plots', menu = missionplotmenu)
        
        tk.Tk.config(self, menu = menubar)
        
        self.Canvas = PlotCanvas(self)
        self.Canvas.grid(row = 0, column = 0, sticky = 'NSEW')
        
        self.columnconfigure(0, weight = 1)
        
        sidebar = tk.Frame(self)
        sidebar.grid(row = 0, column = 4, rowspan = 2, sticky = 'NS')
        
        self.Menu = Menu(sidebar)
        self.Menu.grid(row = 0, column = 0, sticky = 'NS', pady = (0,5))
        
        self.Tabs = TabMenu(sidebar)
        self.Tabs.grid(row = 1, column = 0, sticky = 'NSWE', pady = 5)
        
        self.SearchTools = SearchTools(sidebar, self.search)
        self.SearchTools.grid(row = 2, column = 0, sticky = 'NSWE', pady = 5)
        
        self.PlotTools = tk.Frame(sidebar)
        #self.PlotTools.grid(row = 2, column = 0, sticky = 'NS', pady = 5)
        
        self.LCTools = PlotTools(self.PlotTools, 'Lightcurve')
        self.LCTools.grid(row = 1, column = 0, sticky = 'NSWE', pady = 5)
        
        self.ASTools = PlotTools(self.PlotTools, 'Amplitude Spectrum')
        self.ASTools.percentbox()
        self.ASTools.grid(row = 2, column = 0, sticky = 'NSWE', pady = 5)
        
        self.plotupdate = tk.Button(self.PlotTools, text = 'Update', command = self.updatePlot)#, command = self.updatePlot)
        self.plotupdate.grid(row = 3, pady = 5)
        
        self.Display = Display(sidebar)
        #self.Display.grid(row = 2, column = 0, sticky = 'NS', pady = 5)
        
        self.Tabs.showSearch.bind ("<Button-1>", lambda event, self=self, string = 'search':
                                   self.showTab( event, string))
        self.Tabs.showTools.bind ("<Button-1>", lambda event, self=self, string = 'tools':
                                  self.showTab( event, string))
        self.Tabs.showTarget.bind ("<Button-1>", lambda event, self=self, string = 'target':
                                   self.showTab( event, string))
        self.SearchTools.searchbar.bind ("<Return>", self.quickplot_event)
        
        self.Canvas.f.canvas.mpl_connect('scroll_event', self.onscroll)
        self.Canvas.f.canvas.mpl_connect('button_press_event', self.onclick)
        
        self.Menu.list.bind('<<ListboxSelect>>', self.selectFile)
        self.bind('d', self.keyPress)
        self.bind('g', self.keyPress)
        self.bind('h', self.keyPress)
        self.bind('b', self.keyPress)
        self.bind('s', self.keyPress)
        self.bind('f', self.keyPress)
        self.bind('j', self.keyPress)
        self.bind('i', self.keyPress)
    
    def selectFile(self,event):
        file = self.Menu.selectedFile()
        self.plot(file[0], file[1])
        self.Display.init(file[0], file[1])
    
    def quickplot_event(self, event):
        self.quickplot()
    
    def quickplot(self):
        # MAKE THIS LOOK THROUGH ALL CAMPAIGNS. EZ TO DO BY KNOWING THE START/END IDS FOR EACH CAMPAIGN.
        # DOESNT OWRK>>???? DO IT MANUALLY@!!!!
        search = self.SearchTools.searchbar.get()
        
        if '.fits' in search:
            search = search.rstrip('.fits')
        
        for c in self.Menu.campaign_nums:
            directory = 'k2c' + c + '/data/'
            targets = list(np.sort(os.listdir(directory)))
            if targets != []:
                target = np.int(targets[-1][:9])
                if np.int(search) > target:
                    continue
                else:
                    if (search + '.fits') in targets:
                        campaign = c
        
        #campaign = self.Menu.campaign_dic[self.Menu.campaign_str.get()]
        if search != '':
            #try:
            file = 'k2c'+ campaign + '/data/' + search + '.fits'
            flagdir = 'k2c' + campaign + '/flags/' + search + '.txt'
            self.plot(file, flagdir)
            self.Display.init(file, flagdir)
            #except:
            #    messagebox.showerror('Error','Invalid EPIC ID')
    
    def search(self):
        
        filelist = list(self.Menu.filelist)
        
        def check(minx, maxx, x):
            if minx <= x <= maxx:
                return True
        
        def remove(file):
            filelist.remove(file)
        
        def get(startype, val):
            if startype:
                return val
        
        search = self.SearchTools.searchbar.get()
        
        if search:
            if '.fits' in search:
                search = search.rstrip('.fits')
            self.quickplot()
        
        minteff = self.SearchTools.minteff.get()
        maxteff = self.SearchTools.maxteff.get()
        minlogg = self.SearchTools.minlogg.get()
        maxlogg = self.SearchTools.maxlogg.get()
        dsct = self.SearchTools.dsctvar.get()
        gdor = self.SearchTools.gdorvar.get()
        binary = self.SearchTools.binvar.get()
        hybrid = self.SearchTools.dghybvar.get()
        interest = self.SearchTools.intvar.get()
        
        minteff = str2float(minteff, True)
        maxteff = str2float(maxteff, False)
        minlogg = str2float(minlogg, True)
        maxlogg = str2float(maxlogg, False)
        
        allowed = [get(dsct, 1), get(gdor, 2), get(hybrid, 3), get(binary, 4), get(interest, 7)]
        
        rm = []
        
        for f in filelist:
            if '-b' in f:
                star = starlist[f.rstrip('-b.fits')]
            else:
                star = starlist[f.rstrip('.fits')]
            axe = False
            
            for i in allowed:
                if i != None:
                    if star[2] != i:
                        axe = True
                        #rm.append(f)
            #if search:
                #self.quickplot()
                #if search not in f:
                    #axe = True
                    #rm.append(f)
            if minteff or maxteff:
                if not check(minteff, maxteff, str2float(star[0], True)):
                    axe = True
                    #rm.append(f)
            elif minlogg or maxlogg:
                if not check(minlogg, maxlogg, str2float(star[1], True)):
                    axe = True
                    #rm.append(f)
            if axe:
                rm.append(f)
        
        if rm:
            for i in rm:
                remove(i)
        
        self.Menu.listFiles(filelist)
    
    def keyPress(self,event):
        if event.keysym == 'd':
            self.updateFlag(1) # Delta Scuti Candidate
        elif event.keysym == 'g':
            self.updateFlag(2) # Gamma Doradus Candidate
        elif event.keysym == 'h':
            self.updateFlag(3) # Delta Sct/Gamma Dor Hybrid
        elif event.keysym == 'b':
            self.updateFlag(4) # Binary
        elif event.keysym == 's':
            self.updateFlag(5) # Low Freq Other
        elif event.keysym == 'f':
            self.updateFlag(6) # High Freq Other
        elif event.keysym == 'i':
            self.updateFlag(7)
        elif event.keysym == 'j':
            self.updateFlag(0) # Junk
    
    def updateFlag(self,integer):
        self.obj.setFlag(integer)
        starlist[str(self.obj.cards['EPIC'])][2] = integer
        self.plot(self.obj.file, self.obj.flagdir)
        #self.updatePlot()
    
    def updatePlot(self):
        self.plot(self.obj.file, self.obj.flagdir)
        self.LCTools.clearEntries()
        self.ASTools.clearEntries()
    
    def plot(self, file, flagdir):#, lcx, lcy, asx, asy):
        self.obj = Object(file, flagdir)
        time = self.obj.cards['TIME']
        lc = self.obj.cards['LC']
        freq = self.obj.cards['FREQS']
        als = self.obj.cards['AMP_LOMBSCARG']
        flag = self.obj.FLAGS[-1]
        
        time = time - time[0]
        aspercent = self.ASTools.percent.get() / 100
        
        self.Canvas.f.suptitle('Object ID: ' + str(self.obj.cards['EPIC']) + '   Type: ' + flag2label(int(flag)), fontsize = 12)
        self.Canvas.axlc.clear()
        self.Canvas.axlc.plot(time, lc, linewidth = 0.50)
        self.Canvas.axlc.set_xlabel('Time $(d)$')
        self.Canvas.axlc.set_ylabel('Amplitude $(ppm)$')
        self.Canvas.axlc.ticklabel_format(style = 'sci', scilimits = (0,0), axis = 'y', useMathText = False)
        self.Canvas.axlc.xaxis.set_major_locator(MultipleLocator(10))
        self.Canvas.axlc.xaxis.set_minor_locator(MultipleLocator(2))
        self.Canvas.axlc.grid()
        if self.LCTools.maxx.get() and self.LCTools.minx.get():
            lcmaxx = float(self.LCTools.maxx.get())
            lcminx = float(self.LCTools.minx.get())
            self.Canvas.axlc.set_xlim(lcminx,lcmaxx)
        else:
            self.Canvas.axlc.set_xlim(0,time[-1])
        
        if self.LCTools.maxy.get() and self.LCTools.miny.get():
            lcmaxy = float(self.LCTools.maxy.get())
            lcminy = float(self.LCTools.miny.get())
            self.Canvas.axlc.set_ylim(lcminy,lcmaxy)
        else:
            None
        
        self.Canvas.axas.clear()
        self.Canvas.axas.set_title('Displaying ' + str(aspercent * 100) + '% of Max Amplitude', fontsize = 10)
        self.Canvas.axas.plot(freq, als, linewidth = 0.50)
        self.Canvas.axas.axvline(x = 5, linestyle = ':', color = 'black')
        self.Canvas.axas.axvline(x = 4.075, linestyle = ':', color = 'red')
        self.Canvas.axas.axvline(x = 4.075*2, linestyle = ':', color = 'red')
        self.Canvas.axas.axvline(x = 4.075*3, linestyle = ':', color = 'red')
        self.Canvas.axas.axvline(x = 4.075*4, linestyle = ':', color = 'red')
        self.Canvas.axas.axvline(x = 4.075*5, linestyle = ':', color = 'red')
        self.Canvas.axas.set_xlabel('Frequency $(c/d)$')
        self.Canvas.axas.set_ylabel('Amplitude $(ppm)$')
        self.Canvas.axas.ticklabel_format(style = 'sci', scilimits = (0,0), axis = 'y', useMathText = False)
        self.Canvas.axas.grid()
        
        if self.ASTools.maxx.get() and self.ASTools.minx.get():
            asmaxx = float(self.ASTools.maxx.get())
            asminx = float(self.ASTools.minx.get())
            self.Canvas.axas.set_xlim(asminx,asmaxx)
            self.Canvas.axas.xaxis.set_major_locator(MultipleLocator(asmaxx/4))
            self.Canvas.axas.xaxis.set_minor_locator(MultipleLocator(asmaxx/8))
        else:
            self.Canvas.axas.set_xlim(0,freq[-1])
            self.Canvas.axas.xaxis.set_major_locator(MultipleLocator(2.5))
            self.Canvas.axas.xaxis.set_minor_locator(MultipleLocator(0.5))
        
        if self.ASTools.maxy.get() and self.ASTools.miny.get():
            asmaxy = float(self.ASTools.maxy.get())
            asminy = float(self.ASTools.miny.get())
            self.Canvas.axas.set_ylim(asminy, asmaxy)
        else:
            self.Canvas.axas.set_ylim(0, max(als) * aspercent)
        
        self.Canvas.f.canvas.draw()
    
    def temphist(self):
        self.histogram('TEFF', False)
    
    def logghist(self):
        self.histogram('LOGG', False)
    
    def campaignhr(self):
        self.hr(False)
    
    def missiontemp(self):
        self.histogram('TEFF', True)
    
    def missionlogg(self):
        self.histogram('LOGG', True)
    
    def missionhr(self):
        self.hr(True)
    
    def histogram(self, param, mission):
        
        parameter_array = []
        
        hist = Window()
        if param == 'TEFF':
            if mission:
                for star in starlist:
                    if not ('-b' in str(star)) and not (starlist[str(star)][0] in ('N/A', 'nan')):
                        parameter_array.append(starlist[star][0])
            else:
                for file in self.Menu.filelist:
                    if not ('-b' in str(file)) and not (starlist[file.rstrip('.fits')][0] in ('N/A', 'nan')):
                        parameter_array.append(float(starlist[file.rstrip('.fits')][0]))
            parameter_array = np.asarray(parameter_array)#[~np.isnan(parameter_array)]
            
            plt.hist(parameter_array, bins = np.arange(np.floor(parameter_array.min() / 500) * 500,
                                                       np.ceil(parameter_array.max() / 500) * 500, 500), color = 'black')
            if mission:
                plt.title('K2 Mission'+': Effective Temperature Distribution')
            else:
                plt.title(str(self.Menu.campaign_str.get()) + ': Effective Temperature Distribution')
            plt.xlabel(r'$T_{Eff}$ (K)')
            plt.ylabel('Number of Stars')
            hist.canvas.ax.xaxis.set_major_locator(MultipleLocator(1000))
            hist.canvas.ax.xaxis.set_minor_locator(MultipleLocator(500))
        
        if param == 'LOGG':
            if mission:
                for star in starlist:
                    if not ('-b' in str(star)) and not (starlist[str(star)][1] in ('N/A', 'nan')):
                        parameter_array.append(starlist[star][0])
            else:
                for file in self.Menu.filelist:
                    if not ('-b' in str(file)) and not (starlist[file.rstrip('.fits')][1] in ('N/A', 'nan')):
                        parameter_array.append(float(starlist[file.rstrip('.fits')][1]))
            parameter_array = np.asarray(parameter_array)#[~np.isnan(parameter_array)]
            5
            plt.hist(parameter_array, bins = np.arange(np.floor(parameter_array.min() / 0.25) * 0.25,
                                                       np.ceil(parameter_array.max() / 0.25) * 0.25, 0.25), color = 'black')
            if mission:
                plt.title('K2 Mission' + ': Surface Gravity Distribution')
            else:
                plt.title(str(self.Menu.campaign_str.get()) + ': Surface Gravity Distribution')
            plt.xlabel('log(g)')
            plt.ylabel('Number of Stars')
            hist.canvas.ax.xaxis.set_major_locator(MultipleLocator(0.25))
            #hist.canvas.ax.xaxis.set_minor_locator(MultipleLocator(0.25))
    
    def hr(self, mission):
        
        if mission:
            logg_dic = {1 : [], 2 : [], 3 : [], 4 : [], 'other' : []}
            teff_dic = {1 : [], 2 : [], 3 : [], 4 : [], 'other' : []}
            for star in starlist:
                if not ('-b' in str(star)) and not ((starlist[str(star)][0] or starlist[str(star)][1]) in ('N/A', 'nan')):
                    #logg_array.append(float(starlist[star][1]))
                    #teff_array.append(float(starlist[star][0]))
                    if starlist[star][2] in (1, 2, 3, 4):
                        logg_dic[starlist[star][2]].append(float(starlist[star][1]))
                        teff_dic[starlist[star][2]].append(float(starlist[star][0]))
                    else:
                        logg_dic['other'].append(float(starlist[star][1]))
                        teff_dic['other'].append(float(starlist[star][0]))
        else:
            logg_dic = {1 : [], 2 : [], 3 : [], 4 : [], 'other' : []}
            teff_dic = {1 : [], 2 : [], 3 : [], 4 : [], 'other' : []}
            for file in self.Menu.filelist:
                if not ('-b' in str(file)) and not ((starlist[file.rstrip('.fits')][0] or starlist[file.rstrip('.fits')][1]) in ('N/A', 'nan')):
                    #logg_array.append(float(starlist[file.rstrip('.fits')][1]))
                    #teff_array.append(float(starlist[file.rstrip('.fits')][0]))
                    if starlist[file.rstrip('.fits')][2] in (1, 2, 3, 4):
                        logg_dic[starlist[file.rstrip('.fits')][2]].append(float(starlist[file.rstrip('.fits')][1]))
                        teff_dic[starlist[file.rstrip('.fits')][2]].append(float(starlist[file.rstrip('.fits')][0]))
                    else:
                        logg_dic['other'].append(float(starlist[file.rstrip('.fits')][1]))
                        teff_dic['other'].append(float(starlist[file.rstrip('.fits')][0]))
        
        hr = Window()
        plt.plot(teff_dic['other'], logg_dic['other'], '.', color = 'gray', label = 'Other')
        plt.plot(teff_dic[1], logg_dic[1], '.', color = 'red', label = flag2label(1))
        plt.plot(teff_dic[2], logg_dic[2], '.', color = 'blue', label = flag2label(2))
        plt.plot(teff_dic[3], logg_dic[3], '.', color = 'purple', label = flag2label(3))
        plt.plot(teff_dic[4], logg_dic[4], '.', color = 'green', label = flag2label(4))
        if mission:
            plt.title('K2 Mission' + ': HR Diagram')
        else:
            plt.title(str(self.Menu.campaign_str.get()) + ': HR Diagram')
        plt.xlabel(r'$T_{Eff}$ (K)')
        plt.ylabel('log(g)')
        plt.legend()
        plt.gca().invert_yaxis()
        plt.gca().invert_xaxis()
    
    def savelist(self):
        
        with open('targetlist.txt', 'a+') as targetlist:
            for f in self.Menu.filelist:
                if '-b' not in f:
                    star = f.rstrip('.fits')
                    targetlist.write('EPIC ' + star)
                    targetlist.write('\n')
    
    def showTab(self, event, tab):
        if tab == 'search':
            self.Tabs.showSearch.config(relief = tk.SUNKEN)
            self.Tabs.showTools.config(relief = tk.RAISED)
            self.Tabs.showTarget.config(relief = tk.RAISED)
            self.SearchTools.grid()
            self.PlotTools.grid_remove() 
            self.Display.grid_remove()
        if tab == 'tools':
            self.Tabs.showSearch.config(relief = tk.RAISED)
            self.Tabs.showTools.config(relief = tk.SUNKEN)
            self.Tabs.showTarget.config(relief = tk.RAISED)
            self.SearchTools.grid_remove()
            self.PlotTools.grid() 
            self.Display.grid_remove()
        if tab == 'target':
            self.Tabs.showSearch.config(relief = tk.RAISED)
            self.Tabs.showTools.config(relief = tk.RAISED)
            self.Tabs.showTarget.config(relief = tk.SUNKEN)
            self.SearchTools.grid_remove()
            self.PlotTools.grid_remove() 
            self.Display.grid()
    
    def onscroll(self, event):
        #print('you pressed', event.button,
        #      event.xdata, event.ydata, event.step, event.inaxes)
        x = event.xdata
        
        if event.inaxes == self.Canvas.axlc:
            axes = self.Canvas.axlc
            xdata = self.obj.cards['TIME']
            xdata = xdata - xdata[0]
            
        if event.inaxes == self.Canvas.axas:
            axes = self.Canvas.axas
            xdata = self.obj.cards['FREQS']
            
        #if event.inaxes == self.Canvas.axlc:
        xmin, xmax = axes.get_xlim()
        zoom = 0.5 ** event.step
        xrange = (xmax - xmin) / 2
        xmin = x - xrange * zoom
        xmax = x + xrange * zoom
        
        if xmin < xdata[0]:
            xmin = 0
        if xmax > xdata[-1]:
            xmax = xdata[-1]
        if xmax > xmin:
            axes.set_xlim(xmin, xmax)
            self.Canvas.f.canvas.draw()
         
    def onclick(self, event):
		
        if event.inaxes == self.Canvas.axlc:
            lc = self.obj.cards['LC']
            lcmin, lcmax = self.Canvas.axlc.get_ylim()
            if (event.button == 1) and (lcmax > (max(lc) * 0.1)) and (lcmin < (min(lc) * 0.1)):
                zoom = 0.1
            elif event.button == 3:
                zoom = -0.1
            lcmax = lcmax - max(lc) * zoom
            lcmin = lcmin - min(lc) * zoom
            self.Canvas.axlc.set_ylim(lcmin, lcmax)
            
        elif event.inaxes == self.Canvas.axas:
            als = self.obj.cards['AMP_LOMBSCARG']
            aspercent = self.ASTools.percent.get()
            if (event.button == 1) and (aspercent > 10):
                aspercent += -10
            if (event.button == 3) and (aspercent < 100):
                aspercent += 10
            self.Canvas.axas.set_title('Displaying ' + str(aspercent) + '% of Max Amplitude', fontsize = 10)
            self.Canvas.axas.set_ylim(0, max(als) * aspercent / 100)
            self.ASTools.percent.set(aspercent)
        
        self.Canvas.f.canvas.draw()
    
    def saveampls(self):
        #data = {'amps': self.obj.cards['AMP_LOMBSCARG'], 'freqs': self.obj.cards['FREQS']}
        df = pd.DataFrame()
        df['freqs'] = self.obj.cards['FREQS']
        df['amps'] = self.obj.cards['AMP_LOMBSCARG']
        df.to_csv(str(self.obj.cards['EPIC']) + '_fft.csv', index = False)
    
    def savepdf(self):
        popup = EntryPopUp()
        self.wait_window(popup)
        
        pdf = popup.input
        if '.pdf' not in pdf:
            pdf = pdf + '.pdf'
        
        criteria = popup.criteria
        # Check if file exists. If not, create
        try:
            with open(pdf, 'r'):
                pass
        except:
            with open(pdf, 'w+'):
                pass
        
        if criteria == 'Current Target':
            filelist = [str(self.obj.cards['EPIC']) + '.fits']
        elif criteria == 'Campaign Target List':
            filelist = self.Menu.filelist
        
        for f in filelist:
            
            file = 'k2c'+ self.Menu.campaign_dic[self.Menu.campaign_str.get()] + '/data/' + f
            flagdir = 'k2c' + self.Menu.campaign_dic[self.Menu.campaign_str.get()] + '/flags/' + f[0:9] + '.txt'
            
            self.obj = Object(file, flagdir)
            
            fig = plt.figure(figsize = (16, 8))
            ax0 = fig.add_axes([0.1,0.5,0.8,0.3])
            ax1 = fig.add_axes([0.1,0.1,0.8,0.3])
            
            time = self.obj.cards['TIME']
            lc = self.obj.cards['LC']
            freq = self.obj.cards['FREQS']
            als = self.obj.cards['AMP_LOMBSCARG']
            flag = self.obj.FLAGS[-1]
            
            aspercent = self.ASTools.percent.get() / 100
            
            time = time - time[0]
            
            ax0.plot(time, lc, linewidth = 0.5)
            ax0.set_title('Object ID: ' + str(self.obj.cards['EPIC']) + '   Type: ' + flag2label(int(flag)), fontsize = 12)
            ax0.set_xlabel('Time $(d)$', fontsize = 10)
            ax0.set_ylabel('Amplitude $(ppm)$', fontsize = 10)
            ax0.ticklabel_format(style = 'sci', scilimits = (0,0), axis = 'y', useMathText = False)
            ax0.tick_params(axis = 'both', which = 'both', labelsize = 8)
            ax0.yaxis.offsetText.set_fontsize(8)
            ax0.xaxis.set_major_locator(MultipleLocator(10))
            ax0.xaxis.set_minor_locator(MultipleLocator(2))
            ax0.grid()
            
            if self.LCTools.maxx.get() and self.LCTools.minx.get():
                lcmaxx = float(self.LCTools.maxx.get())
                lcminx = float(self.LCTools.minx.get())
                ax0.set_xlim(lcminx,lcmaxx)
            else:
                ax0.set_xlim(0,time[-1])
            
            if self.LCTools.maxy.get() and self.LCTools.miny.get():
                lcmaxy = float(self.LCTools.maxy.get())
                lcminy = float(self.LCTools.miny.get())
                ax0.set_ylim(lcminy,lcmaxy)
            else:
                None
            
            ax1.plot(freq, als, linewidth = 0.5)
            ax1.axvline(x = 5, linestyle = ':', color = 'black')
            ax1.axvline(x = 4.075, linestyle = ':', color = 'red')
            ax1.axvline(x = 4.075*2, linestyle = ':', color = 'red')
            ax1.axvline(x = 4.075*3, linestyle = ':', color = 'red')
            ax1.axvline(x = 4.075*4, linestyle = ':', color = 'red')
            ax1.axvline(x = 4.075*5, linestyle = ':', color = 'red')
            ax1.set_ylim(0,None)
            ax1.set_title('Displaying ' + str(aspercent * 100) + '% of Max Amplitude', fontsize = 10)
            ax1.set_xlabel('Frequency $(c/d)$', fontsize = 10)
            ax1.set_ylabel('Amplitude $(ppm)$', fontsize = 10)
            ax1.ticklabel_format(style = 'sci', scilimits = (0,0), axis = 'y', useMathText = False)
            ax1.tick_params(axis = 'both', which = 'both', labelsize = 8)
            ax1.yaxis.offsetText.set_fontsize(8)
            ax1.grid()
            
            if self.ASTools.maxx.get() and self.ASTools.minx.get():
                asmaxx = float(self.ASTools.maxx.get())
                asminx = float(self.ASTools.minx.get())
                ax1.set_xlim(asminx,asmaxx)
                self.Canvas.axas.xaxis.set_major_locator(MultipleLocator(asmaxx/4))
                self.Canvas.axas.xaxis.set_minor_locator(MultipleLocator(asmaxx/8))
            else:
                ax1.set_xlim(0,freq[-1])
                ax1.xaxis.set_major_locator(MultipleLocator(2.5))
                ax1.xaxis.set_minor_locator(MultipleLocator(0.5))
            
            if self.ASTools.maxy.get() and self.ASTools.miny.get():
                asmaxy = float(self.ASTools.maxy.get())
                asminy = float(self.ASTools.miny.get())
                ax1.set_ylim(asminy, asmaxy)
            else:
                ax1.set_ylim(0, max(als) * aspercent)
            
            i = 0
            x1 = x2 = 0.075
            x3 = 0.675
            y1 = 0.95
            y2 = 0.90
            skip1 = 0
            skip2 = 0
            while True:
                if 'TWOMASS' in self.obj.cards.keys():
                    i += 1
                    valuetitle = str(list(self.obj.cards.keys())[i])
                    uncertaintytitle = str(list(self.obj.cards.keys())[i+1])
                    if i in [16, 18]:
                        text = valuetitle + ': ' + str(self.obj.cards[valuetitle]) + ' +/- ' + str(self.obj.cards[uncertaintytitle])
                        plt.figtext(x3, 0.825, text, horizontalalignment='left',
                            fontsize=10, multialignment='left')
                        i += 1
                        x3 += 0.125
                    elif (i != 15) and (i >= 9):
                        text = valuetitle + ': ' + str(self.obj.cards[valuetitle]) + ' +/- ' + str(self.obj.cards[uncertaintytitle])
                        plt.figtext(x2, y2, text, horizontalalignment='left',
                            fontsize=10, multialignment='left')
                        i += 1
                        x2 += 0.15
                        skip2 += 1
                        if skip2 == 5:
                            y2 += -0.025
                            x2 = 0.075
                            skip2 = 0
                    elif (i == 8):
                        text = valuetitle + ': ' + str(self.obj.cards[valuetitle])
                        plt.figtext(0.675, 0.95, text, horizontalalignment='left',
                            fontsize=10, multialignment='left')
                    else:
                        text = valuetitle + ': ' + str(self.obj.cards[valuetitle])
                        plt.figtext(x1, y1, text, horizontalalignment='left',
                            fontsize=10, multialignment='left')
                        x1 += 0.15
                        skip1 += 1
                        if skip1 == 4:
                            y1 += -0.025
                            x1 = 0.075
                            skip1 = 0
                    if i == 33:
                        break
                else:
                    i += 1
                    valuetitle = str(list(self.obj.cards.keys())[i])
                    uncertaintytitle = str(list(self.obj.cards.keys())[i+1])
                    if i in [15, 17]:
                        text = valuetitle + ': ' + str(self.obj.cards[valuetitle]) + ' +/- ' + str(self.obj.cards[uncertaintytitle])
                        plt.figtext(x3, 0.825, text, horizontalalignment='left',
                            fontsize=10, multialignment='left')
                        i += 1
                        x3 += 0.125
                    elif (i != 14) and (i >= 8):
                        text = valuetitle + ': ' + str(self.obj.cards[valuetitle]) + ' +/- ' + str(self.obj.cards[uncertaintytitle])
                        plt.figtext(x2, y2, text, horizontalalignment='left',
                            fontsize=10, multialignment='left')
                        i += 1
                        x2 += 0.15
                        skip2 += 1
                        if skip2 == 5:
                            y2 += -0.025
                            x2 = 0.075
                            skip2 = 0                    
                    else:
                        
                        text = valuetitle + ': ' + str(self.obj.cards[valuetitle])
                        plt.figtext(x1, y1, text, horizontalalignment='left',
                            fontsize=10, multialignment='left')
                        x1 += 0.15
                        skip1 += 1
                        if skip1 == 4:
                            y1 += -0.025
                            x1 = 0.075
                            skip1 = 0
                    if i == 32:
                        break
            
            with PdfPages('lastfig.pdf') as figpdf:
                figpdf.savefig(fig)
            
            plt.close(fig)
            
            with open(pdf, 'rb') as mainpdf:
                with open('lastfig.pdf', 'rb') as figpdf:
                    page = pypdf2.PdfFileMerger()
                    try:
                        page.append(pypdf2.PdfFileReader(mainpdf))
                    except:
                        pass
                    page.append(pypdf2.PdfFileReader(figpdf))
                    page.write(pdf)
        subprocess.call(['rm', 'lastfig.pdf'])

def exiting():
    print('Saving flags...')
    newflags = np.array([])
    for i in stars:
        n = starlist[i][2]
        newflags = np.append(newflags, n)
    
    np.save('etc/flagarray.npy', newflags)
      
    print("Exiting...")
    app.quit()
    sys.exit()
    

app = MainApp()
app.tk.call('tk', 'scaling', 2.0)
app.protocol("WM_DELETE_WINDOW", exiting)
app.mainloop()
