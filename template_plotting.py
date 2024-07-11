import matplotlib
matplotlib.use('Agg')

import ROOT as r
from optparse import OptionParser
from time import sleep
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mplhep as hep
from root_numpy import hist2array
import ctypes
from pathlib import Path
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import os 
#import misc.plotRPFWithUnc as plotRPFWithUnc

matplotlib.use('Agg')
r.gROOT.SetBatch(True)
r.gStyle.SetOptFit(111)

base_path='/uscms_data/d3/roguljic/el8_anomalous/el9_fitting/templates_v2/'


def makehistograms(mcpath,datapath,year,process):    
    
    print(mcpath)
    print(datapath)

    log=True

    histos  = []
    labels  = []
    edges   = []
    colors  = []
    histosData = []#we're assuming only one data_obs dataset
    edgesData  = []#it's still kept in array (with one element) to be similar to other processes
    colorsData = []
    labelsData = []
    histosSig  = [0,0]#we're assuming only one signal dataset
    edgesSig   = [0,0]#it's still kept in array (with one element) to be similar to other processes
    labelsSig  = [0,0]
    colorsSig  = [0,0]


    mcsig=r.TFile.Open(mcpath)
    data=r.TFile.Open(datapath)

    mckeys=mcsig.GetListOfKeys()
    datakeys=data.GetListOfKeys()
        
    for key in mckeys:
        keyname=key.GetName()
        if 'SR' in keyname:
            print('No histogram created')
            continue
        if 'Pass' in keyname:
            pf_flag=True
            index=1
        elif 'Fail' in keyname:
            pf_flag=False
            index=0
        else:
            print('pf_flag error')
        print('Creating histogram for mc ',keyname)
        h=mcsig.Get(keyname)
        projection = h.ProjectionX("proj_name")
        hist, edges = hist2array(projection,return_edges=True)
        histosSig[index]=hist
        if pf_flag:
            labelsSig[index]='CR Pass MC'
            colorsSig[index]='r'
        else:
            labelsSig[index]='CR Fail MC'
            colorsSig[index]='b'
        edgesSig[index]=edges[0]

    for key in datakeys:
        keyname=key.GetName()
        if 'SR' in keyname:
            print('No histogram created')
            continue
        if 'Pass' in keyname:
            pf_flag=True
        elif 'Fail' in keyname:
            pf_flag=False
        else:
            print('pf_flag error')
        print('Creating histogram for data ',keyname)
        h=data.Get(keyname)
        projection = h.ProjectionX("proj_name")
        hist, edges = hist2array(projection,return_edges=True)
        histosData.append(hist)
        if pf_flag:
            labelsData.append('CR Pass data')
            colorsData.append('r')
        else:
            labelsData.append('CR Fail data')
            colorsData.append('b')
        edgesData.append(edges[0])
        

    plt.style.use([hep.style.CMS])
    f, ax = plt.subplots()

    hep.histplot(histosSig,edgesSig[0],stack=False,ax=ax,label=labelsSig,linewidth=3,histtype="fill",color=colors)
    hep.histplot(histosData,edgesData[0],stack=False,ax=ax,label=labelsData,linewidth=3,histtype="errorbar",color=colors)
    if(log):
        ax.set_yscale("log")
    #ax.legend()

    if log:
        yTitle='log(NEvents)'
    else:
        yTitle='NEvents'
    xTitle='mjj'

    ax.set_ylabel(yTitle)
    ax.set_xlabel(xTitle)
    plt.xlabel(xTitle, horizontalalignment='right', x=1.0)
    plt.ylabel(yTitle,horizontalalignment='right', y=1.0)
    hep.cms.text("Simulation WiP "+process+" " + year,loc=0)
    plt.legend(loc='upper right',ncol=2)#loc="best",ncol=2)#loc = 'best'
    plt.tight_layout()
    if not log:
        outFile=process+year+'mjj'
    else:
        outFile='log'+process+year+'mjj'
    print("Saving {0}".format(outFile))

    plt.savefig(outFile)
    plt.savefig(outFile.replace(".png",".pdf"))

    plt.clf()


    return


def getfilepaths(process,year,data):
    if data:
        filepaths=[]
        newfile=base_path+'templates_data_obs_'+year+'.root'
        if not os.path.exists(newfile):
            print('File does not exist: ',newfile)
        else:
            filepaths.append(newfile)
        return filepaths
    else:
        if process=='MXMY':
            filepaths=[]
            MXs=['1200','1400','1600','1800','2000','2200','2400','2500','2600','2800','3000','3500','4000']
            for MX in MXs:
                newfile=base_path+'templates_MX'+MX+'_MY90_'+year+'.root'
                if not os.path.exists(newfile):
                    print('File does not exist: ',newfile)
                else:
                    filepaths.append(newfile)
            return filepaths
        elif process=='QCD':
            filepaths=[]
            QCD_ranges=['700to1000','1000to1500','1500to2000','2000toinf']
            for range in QCD_ranges:
                newfile=base_path+'templates_QCD_HT'+range+'_'+year+'.root'    
                if not os.path.exists(newfile):
                    print('File does not exist: ',newfile)
                else:
                    filepaths.append(newfile)
            return filepaths
        elif process=='TTToHadronic':
            filepaths=[]
            newfile=base_path+'templates_TTToHadronic_'+year+'.root'
            if not os.path.exists(newfile):
                print('File does not exist: ',newfile)
            else:
                filepaths.append(newfile)
            return filepaths
        elif process=='TTToSemiLeptonic':
            filepaths=[]
            newfile=base_path+'templates_TTToSemiLeptonic_'+year+'.root'
            if not os.path.exists(newfile):
                print('File does not exist: ',newfile)
            else:
                filepaths.append(newfile)
            return filepaths
        else:
            print("Invalid process name")
            return


if __name__ == '__main__':
    wp = "tight_medium"

    #years=['2016','2016APV','2017','2018']
    #processes=['MXMY','QCD','TTToHadronic','TTToSemiLeptonic']
    years=['2016']
    processes=['TTToSemiLeptonic']

    for year in years:
        for process in processes:
            mcpaths=getfilepaths(process,year,False)
            data=getfilepaths('x',year,True)
            for mcpath in mcpaths:
                makehistograms(mcpath,data[0],year,process)
            