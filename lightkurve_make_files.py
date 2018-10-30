#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 20:34:00 2018

@author: jorgeagr
"""
import os
from lightkurve import KeplerTargetPixelFile, KeplerLightCurveFile
from lightkurve import log
log.setLevel('ERROR')
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.animation as animation
from matplotlib.backends.backend_pdf import PdfPages
from astropy.io import fits
import numpy as np
import PyPDF2 as pypdf2
from astropy.io import fits
import subprocess

golden_ratio = (np.sqrt(5) + 1) / 2
width = 12
height = width / golden_ratio

mpl.rcParams['font.size'] = 12
mpl.rcParams['figure.titlesize'] = 'large'
mpl.rcParams['legend.fontsize'] = 'small'
mpl.rcParams['figure.figsize'] = (width, height)

def save_pdf(fig, pdf, directory):
    
    with PdfPages(directory + 'lastfig.pdf') as figpdf:
                figpdf.savefig(fig)

    with open(pdf, 'rb') as mainpdf:
        with open(directory + 'lastfig.pdf', 'rb') as figpdf:
            page = pypdf2.PdfFileMerger()
            try:
                page.append(pypdf2.PdfFileReader(mainpdf))
            except:
                pass
            page.append(pypdf2.PdfFileReader(figpdf))
            page.write(pdf)
            
    subprocess.call(['rm', directory + 'lastfig.pdf'])

def check(aperture, row, col, weight):
    try:
        if aperture[row, col]:
            return weight
        else:
            return 0
    except:
        return 0
        

# Lightkurve tut:
# http://lightkurve.keplerscience.org/tutorials/2.09-how-to-use-lightkurve-for-asteroseismology.html

def make_figs(target):
    c = 4
    while True:
        try:
            tpf = KeplerTargetPixelFile.from_archive(target, campaign=c,
                                                     quality_bitmask='default')
            lcf = KeplerLightCurveFile.from_archive(target, campaign=c)
            print(target, ', Campaign', c)
            if np.shape(np.shape(tpf)) == (1,):
                times = []
                for index, image in enumerate(tpf):
                    times.append(tpf[index].shape[0])
                tpf = tpf[np.argmax(times)]
            if np.shape(np.shape(lcf)) == (1,):
                times = []
                for index, image in enumerate(lcf):
                    times.append(lcf[index].PDCSAP_FLUX.flux.shape[0])
                lcf = lcf[np.argmax(times)]
            
            lcf = lcf.PDCSAP_FLUX
                
            break
        except:
            c += 1
    
    directory = 'deltasct/C' + str(c) + '/'
    
    pdf = directory + str(target) + '.pdf'
    
    try:
        with open(pdf, 'r'):
            pass
    except:
        with open(pdf, 'w+'):
            pass
    
    pathdir = 'deltasct/'
    epic_ids = 'deltasct_epic.txt'
    twomass_ids = 'deltasct_2mass.txt'
    
    with open(pathdir + epic_ids) as file:
        for n, line in enumerate(file):
            if str(target) in line:
                row = n

    with open(pathdir + twomass_ids) as file:
        lines = file.readlines()
        twomass = lines[row].lstrip('2MASS ').rstrip('\n')
    
    title = 'EPIC: ' + str(tpf.targetid) + ', 2MASS: ' + twomass
    fig, ax = plt.subplots()
    mpl.cm.get_cmap().set_bad(color='black')
    tpf.plot(ax)
    ax.set_title(title, weight='bold')
    #ax.set_aspect(0.4)
    ax.set_aspect('auto')
    #ax.imshow(tpf.flux[0], aspect=2)
    ax.xaxis.set_major_locator(mtick.MultipleLocator(5))
    ax.xaxis.set_minor_locator(mtick.MultipleLocator(1))
    ax.yaxis.set_minor_locator(mtick.MultipleLocator(1))
    plt.tight_layout()
    save_pdf(fig, pdf, directory)
    plt.close(fig)
    
    fig, ax = plt.subplots()
    mpl.cm.get_cmap().set_bad(color='black')
    tpf.plot(ax, frame=1000, aperture_mask=tpf.pipeline_mask)
    #ax.set_aspect(0.4)
    ax.set_aspect('auto')
    #ax.imshow(tpf.flux[0], aspect=2)
    ax.xaxis.set_major_locator(mtick.MultipleLocator(5))
    ax.xaxis.set_minor_locator(mtick.MultipleLocator(1))
    ax.yaxis.set_minor_locator(mtick.MultipleLocator(1))
    plt.tight_layout()
    save_pdf(fig, pdf, directory)
    plt.close(fig)
    
    fig, ax = plt.subplots(nrows=2)
    
    lcf = lcf.normalize().remove_nans().remove_outliers(sigma=8).fill_gaps()
    ps = lcf.periodogram()
    
    lcf.plot(ax[0])
    lcf.plot(ax[1])
    #fig.suptitle('Target ID: ' + str(tpf.targetid), weight='bold')
    fig.suptitle('Lightcurve', weight='bold')
    #ax[0].set_title('Lightcurve', weight='bold')
    ax[0].set_title('Full Length')
    ax[1].set_title('2-day Window')
    for i in range(2):
        ax[i].xaxis.set_minor_locator(mtick.MultipleLocator(1))
    ax[0].set_xlim(lcf.time[0], lcf.time[-1])
    ax[1].set_xlim(lcf.time[0] + 30, lcf.time[0] + 32)
    '''
    ps.plot(ax=ax[1], color='black')
    ax[1].set_title('Power Spectrum', weight='bold')
    ax[1].axvline(x = 58, linestyle = ':', color = 'black')
    ax[1].set_xlim(0, ps.frequencies.value[-1])
    ax[1].set_ylim(0,max(ps.powers.value)*0.6)
    ax[1].xaxis.set_major_locator(mtick.MultipleLocator(25))
    ax[1].xaxis.set_minor_locator(mtick.MultipleLocator(10))
    '''
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.close(fig)
    save_pdf(fig, pdf, directory)
    
    fig, ax = plt.subplots(nrows=2)
    fig.suptitle('Power Spectrum', weight='bold')
    for i, n in enumerate([0.6, 0.2]):
        ps.plot(ax=ax[i], color='black')
        ax[i].set_title(str(n*100) + '% Amplitude', weight='bold')
        ax[i].axvline(x = 58, linestyle = ':', color = 'black')
        ax[i].set_xlim(0, ps.frequencies.value[-1])
        ax[i].set_ylim(0,max(ps.powers.value)*n)
        ax[i].xaxis.set_major_locator(mtick.MultipleLocator(25))
        ax[i].xaxis.set_minor_locator(mtick.MultipleLocator(10))    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.close(fig)
    save_pdf(fig, pdf, directory)
    

targets = []
with open('deltasct/deltasct_targets.txt') as filelist:
    for line in filelist:
        targets.append(int(line.rstrip('\n')))
            

for i in targets:
    make_figs(i)