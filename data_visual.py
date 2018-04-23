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
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.backends.backend_pdf import PdfPages
import PyPDF2 as pypdf2

#mpl.use('PDF')

# == Functions & Global Variables == #

parameters = np.load('etc/tnldict.npz')
stars = parameters['stars']
vals = list(map(list, zip( parameters['teff'], parameters['logg'], parameters['flag'] )))

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
        
        self.f, self.ax = plt.subplots()
        
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.RIGHT,fill=tk.BOTH,expand=True)
        
        #Displays Matplotlib figure toolbar.
        #self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        #self.toolbar.update()
        #self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        '''
        self.flc, self.axlc = plt.subplots()
        
        self.canvaslc = FigureCanvasTkAgg(self.flc, self)
        self.canvaslc.draw()
        self.canvaslc.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        
        self.fas, self.axas = plt.subplots()
        
        self.canvasas = FigureCanvasTkAgg(self.fas, self)
        self.canvasas.draw()
        self.canvasas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        '''

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
        self.dsctcheck = tk.Checkbutton(types, text = 'Delta Sct', variable = self.dsctvar)
        self.dsctcheck.grid(row = 0, column = 0, sticky = 'W')
        
        self.gdorvar = tk.BooleanVar()
        self.gdorcheck = tk.Checkbutton(types, text = 'Gamma Dor', variable = self.gdorvar)
        self.gdorcheck.grid(row = 0, column = 1, sticky = 'W')
        
        self.binvar = tk.BooleanVar()
        self.bincheck = tk.Checkbutton(types, text = 'Binary' , variable = self.binvar)
        self.bincheck.grid(row = 1, column = 0, sticky = 'W')
        
        self.searchbutton = tk.Button(self, text = 'Search', command = command)
        self.searchbutton.grid(row = 3)

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
        
        self.canvas = PlotCanvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=True)

# == Main Class == #
    
class MainApp(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        
        tk.Tk.wm_title(self, 'K2 Campaign Viewer')
        
        menubar = tk.Menu(self)
        
        filemenu = tk.Menu(menubar, tearoff = 0)
        filemenu.add_command(label = "Save As PDF", command = self.savepdf)
        filemenu.add_separator()
        filemenu.add_command(label = "Exit", command=quit)
        menubar.add_cascade(label = "File", menu=filemenu)
        
        histomenu = tk.Menu(menubar, tearoff = 0)
        histomenu.add_command(label = 'Temperature', command = self.temphist)
        histomenu.add_command(label = 'Log(g)', command = self.logghist)
        menubar.add_cascade(label = 'Histograms', menu = histomenu)
        
        plotsmenu = tk.Menu(menubar, tearoff = 0)
        plotsmenu.add_command(label = 'HR Diagram', command = self.campaignhr)
        menubar.add_cascade(label = 'Plots', menu = plotsmenu)
        
        missionmenu = tk.Menu(menubar, tearoff = 0)
        missionmenu.add_command(label = 'HR Diagram', command = self.missionhr)
        missionmenu.add_command(label = 'Temperature', command = self.missiontemp)
        missionmenu.add_command(label = 'Log(g)', command = self.missionlogg)
        menubar.add_cascade(label = 'Mission', menu = missionmenu)
        
        tk.Tk.config(self, menu = menubar)
        
        plots = tk.Frame(self)
        #plots.grid(row = 0, column = 0, sticky = 'NEWS')
        plots.pack(side = tk.LEFT, expand = True, fill = tk.BOTH)
        
        '''
        self.Canvas = PlotCanvas(plots)
        self.Canvas.pack(expand = True, fill = tk.BOTH)
        '''
        
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
        
        self.SearchTools = SearchTools(sidebar, self.search)
        self.SearchTools.grid(row = 1, sticky = 'NS', pady = 5)
        
        self.LCTools = PlotTools(sidebar, 'Lightcurve')
        self.LCTools.grid(row = 2, sticky = 'NS', pady = 5)
        
        self.ASTools = PlotTools(sidebar, 'Amplitude Spectrum')
        self.ASTools.grid(row = 3, sticky = 'NS', pady = 5)
        
        self.plotupdate = tk.Button(sidebar, text = 'Update', command = self.updatePlot)#, command = self.updatePlot)
        self.plotupdate.grid(row = 4, pady = 5)
        
        self.Display = Display(sidebar)
        #self.Display.grid(row = 1, column = 1, sticky = 'NS')
        self.Display.grid(row = 5, sticky = 'NS', pady = 5)
        
        #self.columnconfigure(0, weight = 10)
        #self.rowconfigure(0, weight = 10)
        #self.rowconfigure(1, weight = 10)
        
        self.Menu.list.bind('<<ListboxSelect>>', self.selectFile)
        self.bind('d', self.keyPress)
        self.bind('g', self.keyPress)
        self.bind('h', self.keyPress)
        self.bind('b', self.keyPress)
        self.bind('s', self.keyPress)
        self.bind('f', self.keyPress)
        self.bind('j', self.keyPress)
        #self.bind(4, self.numberPress)
    
    def selectFile(self,event):
        file = self.Menu.selectedFile()
        self.plot(file[0], file[1])
        self.Display.init(file[0], file[1])
    
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
        
        minteff = self.SearchTools.minteff.get()
        maxteff = self.SearchTools.maxteff.get()
        minlogg = self.SearchTools.minlogg.get()
        maxlogg = self.SearchTools.maxlogg.get()
        dsct = self.SearchTools.dsctvar.get()
        gdor = self.SearchTools.gdorvar.get()
        binary = self.SearchTools.binvar.get()
        
        minteff = str2float(minteff, True)
        maxteff = str2float(maxteff, False)
        minlogg = str2float(minlogg, True)
        maxlogg = str2float(maxlogg, False)
        
        allowed = [get(dsct,1), get(gdor,2), get(binary, 4)]
        
        rm = []
        
        for f in filelist:
            star = starlist[f.rstrip('.fits')]
            axe = False
            
            for i in allowed:
                if i != None:
                    if star[2] != i:
                        axe = True
                        #rm.append(f)
            if search:
                if search not in f:
                    axe = True
                    #rm.append(f)
            elif minteff or maxteff:
                if not check(minteff, maxteff, star[0]):
                    axe = True
                    #rm.append(f)
            elif minlogg or maxlogg:
                if not check(minlogg, maxlogg, star[1]):
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
            self.updateFlag(3) # Dela Sct/ Gamma Dor Hybrid
        elif event.keysym == 'b':
            self.updateFlag(4) # Binary
        elif event.keysym == 's':
            self.updateFlag(5) # Low Freq Other
        elif event.keysym == 'f':
            self.updateFlag(6) # High Freq Other
        elif event.keysym == 'j':
            self.updateFlag(0) # Junk
    
    def updateFlag(self,integer):
        self.obj.setFlag(integer)
        starlist[str(self.obj.cards['EPIC'])][2] = integer
        self.plot(self.obj.file, self.obj.flagdir)
        #self.updatePlot()
    
    def test(self):
        print(float(self.LCTools.maxx.get()) == 5)
        print('test')
    
    def updatePlot(self):
        self.plot(self.obj.file, self.obj.flagdir)
        self.LCTools.clearEntries()
        self.ASTools.clearEntries()
    
    def plot(self, file, flagdir):#, lcx, lcy, asx, asy):
        
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
        #self.Canvas.axlc.clear()
        plt.figure(1)
        #self.CanvasLC.ax.
        plt.plot(time, lc, linewidth = 1)
        plt.title('Object ID: ' + str(self.obj.cards['EPIC']) + '   Type: ' + flag2label(int(flag)), fontsize = 14)
        plt.xlabel('Time $(d)$')
        plt.ylabel('Amplitude $(ppm)$')
        plt.ticklabel_format(style = 'sci', scilimits = (0,0), axis = 'y', useMathText = False)
        self.CanvasLC.ax.xaxis.set_major_locator(MultipleLocator(10))
        self.CanvasLC.ax.xaxis.set_minor_locator(MultipleLocator(2))
        #self.Canvas.axlc.xaxis.set_major_locator(MultipleLocator(10))
        #self.Canvas.axlc.xaxis.set_minor_locator(MultipleLocator(2))
        plt.grid()
        
        if self.LCTools.maxx.get() and self.LCTools.minx.get():
            lcmaxx = float(self.LCTools.maxx.get())
            lcminx = float(self.LCTools.minx.get())
            plt.xlim(lcminx,lcmaxx)
        else:
            plt.xlim(0,time[-1])
        
        if self.LCTools.maxy.get() and self.LCTools.miny.get():
            lcmaxy = float(self.LCTools.maxy.get())
            lcminy = float(self.LCTools.miny.get())
            plt.ylim(lcminy,lcmaxy)
        else:
            None#plt.ylim(-2*(np.std(lc)),2*np.std(lc))
        
        self.CanvasA_LS.ax.clear()
        #self.Canvas.axas.clear()
        plt.figure(2)
        #self.CanvasA_LS.ax.
        plt.plot(freq, als, linewidth = 1)
        plt.axvline(x = 5, linestyle = ':', color = 'black')
        plt.axvline(x = 4.075, linestyle = ':', color = 'red')
        plt.axvline(x = 4.075*2, linestyle = ':', color = 'red')
        plt.axvline(x = 4.075*3, linestyle = ':', color = 'red')
        plt.axvline(x = 4.075*4, linestyle = ':', color = 'red')
        plt.axvline(x = 4.075*5, linestyle = ':', color = 'red')
        plt.ylim(0,None)
        plt.xlabel('Cycles per Day $(1/d)$')
        plt.ylabel('Amplitude $(ppm)$')
        plt.ticklabel_format(style = 'sci', scilimits = (0,0), axis = 'y', useMathText = False)
        plt.grid()
        
        if self.ASTools.maxx.get() and self.ASTools.minx.get():
            asmaxx = float(self.ASTools.maxx.get())
            asminx = float(self.ASTools.minx.get())
            plt.xlim(asminx,asmaxx)
            self.CanvasA_LS.ax.xaxis.set_major_locator(MultipleLocator(asmaxx/4))
            self.CanvasA_LS.ax.xaxis.set_minor_locator(MultipleLocator(asmaxx/8))
            #self.Canvas.axas.xaxis.set_major_locator(MultipleLocator(asmaxx/4))
            #self.Canvas.axas.xaxis.set_minor_locator(MultipleLocator(asmaxx/8))
        else:
            plt.xlim(0,freq[-1])
            self.CanvasA_LS.ax.xaxis.set_major_locator(MultipleLocator(2.5))
            self.CanvasA_LS.ax.xaxis.set_minor_locator(MultipleLocator(0.5))
            #self.Canvas.axas.xaxis.set_major_locator(MultipleLocator(2.5))
            #self.Canvas.axas.xaxis.set_minor_locator(MultipleLocator(0.5))
        
        self.CanvasLC.f.canvas.draw()
        self.CanvasA_LS.f.canvas.draw()
        #self.Canvas.flc.canvas.draw()
        #self.Canvas.fas.canvas.draw()
    
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
                    parameter_array.append(starlist[star][0])
            else:
                for file in self.Menu.filelist:
                    parameter_array.append(starlist[file.rstrip('.fits')][0])
            parameter_array = np.asarray(parameter_array)[~np.isnan(parameter_array)]
            
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
                    parameter_array.append(starlist[star][1])
            else:
                for file in self.Menu.filelist:
                    parameter_array.append(starlist[file.rstrip('.fits')][1])
            parameter_array = np.asarray(parameter_array)[~np.isnan(parameter_array)]
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
            logg_array = []
            teff_array = []
            for star in starlist:
                logg_array.append(starlist[star][1])
                teff_array.append(starlist[star][0])
        else:
            logg_array = []
            teff_array = []
            for file in self.Menu.filelist:
                logg_array.append(starlist[file.rstrip('.fits')][1])
                teff_array.append(starlist[file.rstrip('.fits')][0])
        
        hr = Window()
        plt.plot(teff_array, logg_array, '.', color = 'gray')
        if mission:
            plt.title('K2 Mission' + ': HR Diagram')
        else:
            plt.title(str(self.Menu.campaign_str.get()) + ': HR Diagram')
        plt.xlabel(r'$T_{Eff}$ (K)')
        plt.ylabel('log(g)')
        plt.gca().invert_yaxis()
        plt.gca().invert_xaxis()
    
    def savepdf(self):
        
        # Check if file exists. If not, create
        try:
            with open('k2data.pdf', 'r') as check:
                pass
        except:
            with open('k2data.pdf', 'w+') as create:
                pass
        
        for f in self.Menu.filelist:
            
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
            
            time = time - time[0]
            
            ax0.plot(time, lc, linewidth = 1)
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
            
            ax1.plot(freq, als, linewidth = 1)
            ax1.axvline(x = 5, linestyle = ':', color = 'black')
            ax1.axvline(x = 4.075, linestyle = ':', color = 'red')
            ax1.axvline(x = 4.075*2, linestyle = ':', color = 'red')
            ax1.axvline(x = 4.075*3, linestyle = ':', color = 'red')
            ax1.axvline(x = 4.075*4, linestyle = ':', color = 'red')
            ax1.axvline(x = 4.075*5, linestyle = ':', color = 'red')
            ax1.set_ylim(0,None)
            ax1.set_xlabel('Cycles per Day $(1/d)$', fontsize = 10)
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
                self.Canvas.axas.xaxis.set_major_locator(MultipleLocator(2.5))
                self.Canvas.axas.xaxis.set_minor_locator(MultipleLocator(0.5))
            
            i = 0
            x1 = x2 = 0.075
            x3 = 0.675
            y1 = 0.95
            y2 = 0.90
            skip1 = 0
            skip2 = 0
            while True:
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
                    '''
                    elif i == 7:
                        x1 += 0.175
                    else:
                        x1 += 0.1
                    '''
                if i == 32:
                    break
            
            with PdfPages('lastfig.pdf') as pdf:
                pdf.savefig(fig)
            
            plt.close(fig)
            
            with open('k2data.pdf', 'rb') as mainpdf:
                with open('lastfig.pdf', 'rb') as figpdf:
                    page = pypdf2.PdfFileMerger()
                    try:
                        page.append(pypdf2.PdfFileReader(mainpdf))
                    except:
                        pass
                    page.append(pypdf2.PdfFileReader(figpdf))
                    page.write('k2data.pdf')
        
app = MainApp()
app.mainloop()        