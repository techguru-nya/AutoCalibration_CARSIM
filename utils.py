#!/usr/bin/env python
# coding: utf-8

# # Import

# In[1]:


import os
import sys
import datetime
import time
import subprocess

import glob

import shutil

import pandas as pd
import numpy
import numpy as np

import datetime

import zipfile

import matplotlib.pyplot as plt

import math

from scipy import integrate
from scipy import signal

import shutil

import Read_DCM_5

SAMPLING = 0.005


# # Convert ZIP(D97-->CSV)

# ## ReadComment

# In[2]:


def ReadComment(File):
    Comment = ''
    
    try:
        try:
            with zipfile.ZipFile(File) as zf:
                lst = zf.namelist()

                text = None

                for name in lst:
                    if ".par" not in name and ".TXT" in name:
                        data = zf.read(name)
                        Comment = OutputText(str(data))

        except BadZipFile:
            1
    except NameError:
         Comment = ''

    return Comment


def OutputText(A):
    B = A.split("\\r\\n")
    i = 0
    C = ""
    for b in B:
        if i < 8:
            C += b + ", "
            i += 1

    D = C.replace("b'", "")

    return D


# In[3]:


def RemoveTemp(file):
    is_file = os.path.isfile(file)
    
    if is_file:
        os.remove(file)


def MakePLT(Path0):
    Path1 = Path0 + "Temp.PLT"

    Text = ""
    for S in d_SIGNAL_PLT:
        Text += S + " key="+ d_SIGNAL_PLT[S] + "\n"

    f = open(Path1, "w")
    f.write(Text)
    f.close()

    return Path1


# ## DataTreatment

# In[4]:


def DataTreatment(File, d_Plt, Sampling):
    Csv = None
    NotConvert = False
    
    Folder = os.path.dirname(File) + '/'
    
    root, ext = os.path.splitext(File)
    if (ext == ".ZIP" or ext == ".zip") and "ApplContainer" not in File:
        d97 = UnPackD97(File)

        if d97 != None:
            Plt_new, d_Plt_new, NotAll = MakePLTFromD97(d97, d_Plt)
            
            if Plt_new != None:
                Csv = RunBat(d97, Plt_new, d_Plt_new, Sampling)
                
                dirname, basename = os.path.split(Csv)
                Csv_ = Folder + basename
                os.replace(Csv, Csv_)
            else:
                Csv = None
            
            if Csv == None or NotAll == True:
                NotConvert = True
                
        try:
            Remove_w_ExistFile(d97)
        except TypeError:
            print('TypeError:', File, d97)
            
    return Csv, NotConvert


def UnPackD97(file):
    file_d97 = None
    file_in_zip = ''
    
    dirname, basename = os.path.split(file)
    dirname_ = dirname + '/'
    
    try:
        try:
            with zipfile.ZipFile(file) as zf:
                lst = zf.namelist()

                for file_in_zip in lst:
                    root, ext = os.path.splitext(file_in_zip)
                    
                    if ext == ".D97" or ext == ".d97":  
                        # shutil.unpack_archive(file, dirname_, format='zip')
                        
                        with zipfile.ZipFile(file) as existing_zip:
                            existing_zip.extract(file_in_zip, dirname_)
                            
                        file_d97 = file_in_zip
                        break
                        
        except BadZipFile:
            file_d97 = None
    except NameError:
        if file_in_zip != '':
            Remove_w_ExistFile(Folder + file_in_zip)
            
        file_d97 = None
    
    if file_d97 != None:
        file_out = UnPackD97__Change_FileName(dirname_, file, file_d97)
    else:
        file_out = None
    
    return file_out


def UnPackD97__Change_FileName(Folder, ZIP, D97):    
    # path = Folder + D97
    root, ext = os.path.splitext(ZIP)
    path_new = root + '.D97'
    
    dirname, basename = os.path.split(ZIP)
    path_base = dirname + '/' + D97
    # path_new = Folder + file_name
    
    # print(path_base, path_new)
    # if path_new != path_base:
    #     if os.path.exists(path_new) == True:
    #         os.remove(path_new)
            
    os.rename(path_base, path_new)
    
    return path_new   


def RunBat(file_, Plt, d_Plt, Sampling):
    dirname, basename = os.path.split(file_)
    file = basename
    
    if ".D97" in file:
        CSV = file.replace(".D97", ".CSV")
    elif ".d97" in file:
        CSV = file.replace(".d97", ".CSV")

    # Bat = dirname + "ChangeFormat.bat"
    File0 = dirname + '/' + file
    File1 = dirname + '/' + "1__" + file
    File2 = dirname + '/' + "2__" + file
    File3 = dirname + '/' + "3__" + CSV

    # Text = "MDFDSET3c ifn=" + File0 + ";pltfn=" + Plt + " ofn=" + File1 + "\n"
    Command = "MDFDSET6c ifn=" + File0 + ";pltfn=" + Plt + " ofn=" + File1 + "\n"
    subprocess.call(Command, shell=True)
    
    # Text = "MDFMDL6c ifn=" + File0 + " ofn=" + File1 + " INCLUDE_SG=" + Plt + "\n" 
    
    Command = "MDFMDL6c ifn=" + File1 + " ofn=" + File2 + " tc=" + str(Sampling) + "\n"
    subprocess.call(Command, shell=True)
    
    Command = "SDTM3c ifn=" + File2 + " ofn=" + File3
    subprocess.call(Command, shell=True)
    
#     f = open(Bat, "w")
#     f.write(Text)
#     f.close()

#     res = subprocess.run([Bat], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    Remove_w_ExistFile(File0)
    Remove_w_ExistFile(File1)
    # Remove_w_ExistFile(Bat)

    try:        
        FileOut = ModifyCSV(File3, d_Plt)
        Remove_w_ExistFile(File2)
        Remove_w_ExistFile(File3)
        Remove_w_ExistFile(Plt)
        
    except FileNotFoundError:
        # dirname, basename = os.path.split(file)
        root, ext = os.path.splitext(file_)
        Plt_ = root + '.PLT'
        # Bat_ = root + '.bat'
        
        os.rename(Plt, Plt_)
        
        root, ext = os.path.splitext(File0)
        File0_ = root + '_.D97'
        File3_ = root + '.csv'
        
        # DFMDL6c ifn=c:/TSDE_Workarea/ktt2yk/Work/CarSim/SIM_ABS_Ice/ABS_Ice_N_Spike_base_.D97 t0=1 t1=23 ofn=c:/TSDE_Workarea/ktt2yk/Work/CarSim/SIM_ABS_Ice/1__ABS_Ice_N_Spike_base.D97
        Command = "MDFMDL6c ifn=" + File0 + " t0=0 t1=30" + " ofn=" + File0_ + "\n"
        subprocess.call(Command, shell=True)
        
        Command = "MDFDSET3c ifn=" + File0_ + ";pltfn=" + Plt_ + " ofn=" + File1 + "\n"
        subprocess.call(Command, shell=True)
        
        Command = "MDFMDL6c ifn=" + File1 + " ofn=" + File2 + " tc=" + str(Sampling) + "\n"
        subprocess.call(Command, shell=True)
        
        Command = "SDTM3c ifn=" + File2 + " ofn=" + File3_
        subprocess.call(Command, shell=True)
        
        # f = open(Bat_, "w")
        # f.write(Text_)
        # f.close()
        
        print("FileNotFoundError", Plt_)
        FileOut = None

    return FileOut


def ChangePath(Folder0, File0):
    FILE1 = File0.split("/")
    File = Folder0 + FILE1[-1]
    Folder = Folder0 + FILE1[-2]
    
    return File, Folder, FILE1[-1]


def ModifyCSV(File, d_Plt):
    for i, S in enumerate(d_Plt):
        if i == 0:
            Text_PLT = "TIME" + "," + d_Plt[S]
        else:
            Text_PLT += "," + d_Plt[S]

    with open(File) as f:
        Text_CSV = f.read()

    Text = Text_PLT + "\n" + Text_CSV
    Text = Text.replace(",", "\t")

    f = open(File, "w")
    f.write(Text)
    f.close()
    
    df = pd.read_table(File, sep="\t", index_col=0, skiprows=[1])
    
    dirname, basename = os.path.split(File)
    File2 = dirname + '/' + basename.replace("3__", "")
    # File2 = File2.replace(".CSV", ".csv")
    
    basename_without_ext = os.path.splitext(os.path.basename(File2))[0]
    dirname, basename = os.path.split(File2)
    # now = datetime.datetime.now()
    # FileOut = dirname + '\\' + basename_without_ext + '_' + now.strftime('%Y%m%d_%H%M%S') + '.csv'
    FileOut = dirname + '/' + basename_without_ext + '.csv'
    df.to_csv(FileOut)

    # ExistFile(FileOut)

    return FileOut


def Remove_w_ExistFile(PathFile):
    if os.path.exists(PathFile) == True:
        os.remove(PathFile)


# ##  MakePLTFromD97

# In[58]:


def MakePLTFromD97(File_D97, d_Plt):
    l_Signals_new = []
    d_Plt_new = {}
    
    dirname, basename = os.path.split(File_D97)
    dirname_ = dirname + '/'
    
    D97 = File_D97

    if os.path.exists(D97) == True:
        l_Signals_D97 = ReadD97(D97)
        l_Signals_PLT = list(d_Plt.keys())
        
        for T in l_Signals_PLT:
            if T in l_Signals_D97:
                l_Signals_new.append(T)
            else:
                Error = "Error: " + T + " is nothing."
                # print(Error)

        d_Plt2 = {}
        for S in d_Plt:
            if d_Plt[S] in d_Plt2:
                d_Plt2[d_Plt[S]] = d_Plt2[d_Plt[S]] + [S]
            else:
                d_Plt2[d_Plt[S]] = [S]

        # print(1, d_Plt2)
        NotAll = False
        for S in d_Plt2:
            Found = False
            
            for S1 in d_Plt2[S]:
                if S1 in l_Signals_new:
                    d_Plt_new[S1] = S
                    Found = True
                    break
            
            if Found == False:
                NotAll = True
                    
        # print(2, d_Plt_new)

        Text = ""
        for T in d_Plt_new:
            Text += T + "\n"
        
        # print(3, Text)
                
        Plt_new = dirname_ + 'Temp.PLT'
        
        if Text != "":
            f = open(Plt_new, 'w')
            f.write(Text)
            f.close()
        else:
            Plt_new = None
            d_Plt_new = None
            NotAll = False
    else:
        Plt_new = None    
        d_Plt_new = None
        NotAll = False

    return Plt_new, d_Plt_new, NotAll


def ReadD97(Path):
    Out = []

    #f=open(Path, 'r', encoding="utf_8")
    f = open(Path, 'rb')

    i = 2
    while True:
        line_b = f.readline()
        line = str(line_b)

        # if "[SIGNAL0]" not in line and "[SIGNAL" in line:
        if "[SIGNAL" in line:
            i = 0

        if i == 1 and "NAME=" in line:
            T = line.replace("NAME=", "")
            T = T.replace("\n", "")
            T = T.replace("b'", "")
            T = T.replace("'", "")
            T = T.replace("\\", "*")
            T = T.replace("*r*n", "")

            Out.append(T)

        if "[DATA]" in line:
            break

        i += 1

    f.close()

    return Out


# ## MakeTraceList

# In[59]:


def MakeTraceList(l_Folder, l_Ext, l_Ext_wo):
    print(l_Folder)
    
    l_Traces = []
    
    for Folder in l_Folder:
        for current, subfolders, subfiles in os.walk(Folder):
            for file in subfiles:
                if "ApplContainer" not in file:
                    for Ext_ in l_Ext:
                        if Ext_ in file: 
                            Trace = current + '/'+ file
                            # Trace = current + file
                            l_Traces.append(Trace)
                            break
    
    l_Traces_ = []
    for T in l_Traces:
        Delete = False
        for Ext in l_Ext_wo:
            if Ext in T:
                Delete = True
                break
                
        if Delete == False:
            l_Traces_.append(T)

    return l_Traces_


def CopyMeasurement(df, Folder):
    df1 = df.dropna(subset=["File"])
    L_Measurement = list(df1["File"])

    L_Measurement_New = []

    i = 0
    for Path in L_Measurement:
        FileName = os.path.basename(Path)

        Path1 = Folder + FileName
        if Path1 not in L_Measurement_New:
            L_Measurement_New.append(Path1)
        else:
            FileName1 = FileName.replace(".zip", "")
            FileName1 = FileName1.replace(".ZIP", "")
            Folder_new = Folder + FileName1 + "_" + str(i)
            os.mkdir(Folder_new)
            Path1 = Folder_new + "/" + FileName
            L_Measurement_New.append(Path1)
        i += 1

    i = 0
    for M in L_Measurement:
        try:
            shutil.copy(M, L_Measurement_New[i])
        except FileNotFoundError:
            0
        i += 1


# ## Select_Signal
# - D97ファイルをCSV変換するためのPLT作成で使用する信号
# - PLTから計測信号を設定する。

# In[60]:


def Select_Signal(File):
    d_Signal = {}
    
    f = open(File, 'r', encoding="ascii")
    l_line_plt = f.readlines()

    for line in l_line_plt:
        line = line.replace("\n", "")
        l_line = line.split(" ")

        if l_line[0] != "" and "~" not in l_line[0] and "//" not in l_line[0] and "+" not in l_line[0] and "*" not in l_line[0]:
            d_Signal[l_line[0]] = GetKey(l_line)

    f.close()

    return d_Signal


def GetKey(l_in):
    Out = l_in[0]
    
    for Text in l_in:
        l_Text = Text.split("=")
        
        if l_Text[0] == "key":
            Out = l_Text[1]
            
    return Out


# ## SaveData, ReadData

# In[61]:


def SaveData(Data1, Data2, File):
    # basename_without_ext = os.path.splitext(os.path.basename(File))[0]
    # dirname, basename = os.path.split(File)
    root, ext = os.path.splitext(File)
    now = datetime.datetime.now()
    File_new = root + '___' + now.strftime('%Y%m%d_%H%M%S') + ext
    
    print('Save:', File_new)
    pd.to_pickle((Data1, Data2), File_new)
    
    return File_new


def ReadData(File):
    # basename_without_ext = os.path.splitext(os.path.basename(File))[0]
    dirname, basename = os.path.split(File)
    root, ext = os.path.splitext(File)
    # now = datetime.datetime.now()
    
    l_Files = os.listdir(dirname)
    l_date = []
    
    for F in l_Files:
        root1, ext1 = os.path.splitext(dirname + '/' + F)
        dirname1, basename1 = os.path.split(dirname + '/' + F)
        
        if ext == ext1:
            if '___' in basename1:
                l_basename1 = basename1.split('___')
                basename0, ext0 = os.path.splitext(basename)

                if basename0 == l_basename1[0]:                
                    date = l_basename1[-1]
                    date1, date1_ext = os.path.splitext(date)
                    l_date.append(date1)
                    # print(2, date)
                
    l_date.sort()
    print(l_date)
    
    File_new = root + '___' + l_date[-1] + ext
    
    print('Read:', File_new)
    Data1, Data2 = pd.read_pickle(File_new)
    
    return Data1, Data2


# ## SAVE_ZIP_to_CSV

# In[87]:


def SAVE_ZIP_to_CSV(d_Plt, Folder_In, Sampling, Override):
    d_Csvs = {}
    l_None = []
    
    l_Traces = MakeTraceList(Folder_In, ['.ZIP', '.zip'], [])
    
    # for Zip in l_Traces:
    for i, Zip in enumerate(l_Traces):
        Size = os.path.getsize(Zip)
        print(i + 1, '/', len(l_Traces), ';', Zip, Size)
        
        dirname, basename = os.path.split(Zip)
        Csv_ = dirname + '\\' + basename 
        Csv_ = Csv_.replace('.ZIP', '.csv')
        
        if os.path.exists(Csv_) == False or Override == True:
            Csv, NotConvert = DataTreatment(Zip, d_Plt, Sampling)
        else:
            Csv = Csv_
            NotConvert = False
            
        Text = ReadComment(Zip)
        
        if Csv != None:
            d_Csvs[Zip] = (Text, Csv, Size)
        
        if NotConvert == True:
            l_None.append(Zip)
    
    return d_Csvs, l_None


# ## SAVE_CSV_to_D97_w_ZIP

# In[63]:


def SAVE_CSV_to_D97_w_ZIP(df, File):
    root, ext = os.path.splitext(File)
    dirname = os.path.dirname(File)
    
    CSV = root + '_mod.csv'
    ZIP = root + '_mod.zip'
    D97 = root + '_mod.d97'
    D97_ = os.path.basename(D97)
    BAT = dirname + '/' + '_.bat'
    
    df.to_csv(CSV, index=False)
    
    Command = "SDTM3c ifn=" + CSV + " ofn=" + D97
    subprocess.call(Command, shell=True)
    
#     f = open(BAT, "w")
#     f.write(Text)
#     f.close()

#     res = subprocess.run([BAT], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
 
    compFile = zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED)
    compFile.write(D97, arcname=D97_)
    compFile.close()
    
    # Remove_w_ExistFile(D97)
    Remove_w_ExistFile(CSV)
    # Remove_w_ExistFile(BAT)
    
    return ZIP


# ## Run 

# In[88]:


# PLT_Convert = 'c:\\TSDE_Workarea\\ktt2yk\\Work\\Common\\ABS\\HONDA_32RA_ABS.PLT' 
# PATH_Search = ['c:\\TSDE_Workarea\\ktt2yk\\Work\\Common\\ABS']
# SAMPLING = 0.005 

# d_SIGNAL_PLT = Select_Signal(PLT_Convert)
# d_CSVs, l_Not_Convert = SAVE_ZIP_to_CSV(d_SIGNAL_PLT, PATH_Search, SAMPLING, True)           


# # READ COMMENT in TRACE

# ## COMMENT_LIST

# In[31]:


def COMMENT_LIST(l_Path):
    l_Trace = MakeTraceList(l_Path, ['.zip', '.ZIP'], [])

    d_Comment = {}

    for Tra in l_Trace:
        Com = ReadComment(Tra)
        d_Comment[Tra] = Com
        
    return d_Comment


# ## COMMENT_SEARCH

# In[32]:


def COMMENT_SEARCH(d_Comment, l_Key, l_Key_Remove):
    d_Searched = {}
    
    for Tra in d_Comment:
        Com = d_Comment[Tra]
        
        Counter = 0
        for Key in l_Key:
            if Key.lower() in Com.lower():
                Counter += 1
        
        if Counter == len(l_Key):
            d_Searched[Tra] = Com
    
    l_Remove = []
    for i, Tra in enumerate(d_Searched):
        Com = d_Searched[Tra]

        for Key in l_Key_Remove:
            if Key.lower() in Com.lower():
                l_Remove.append(Tra)
                break

    for Tra in l_Remove:
        d_Searched.pop(Tra)     
    
    return d_Searched


# ## COPY_FILE

# In[33]:


def COPY_FILE(l_File, Dir):
    l_Out = []
    
    for File in l_File:
        shutil.copy2(File, Dir)
        
        basename = os.path.basename(File)
        Out = Dir + File
        l_Out.append(Out)
        
    return l_Out


# ## RUN

# In[ ]:


# l_PATH = ['d:\\Projects\\22MY_3A0A_CR-V\\Data\\91_HEV_Data\\MS_2WD\\', 'd:\\Projects\\22MY_3A0A_CR-V\\Data\\91_HEV_Data\\Summer_2WD\\']
# l_PATH = ['d:\\Projects\\22MY_3A0A_CR-V\\Data\\91_HEV_Data\\MS_4WD\\', 'd:\\Projects\\22MY_3A0A_CR-V\\Data\\91_HEV_Data\\Summer_4WD\\']

# l_PATH = ['\\\\apac.bosch.com\\dfsjp\\LOC\\YH\\JC\\ORG\\ELM\\EAx\\Common\\Application_Common\\30_Function_Team_activity\\TCS_Material\\HM_dTCS_bookshelving\\Trace\\01_Representative_Data\\AxleSplit\\']
# d_COM = COMMENT_LIST(l_PATH)

# d_SEARCH= COMMENT_SEARCH(d_COM, ['jump'], ['hill', 'slalom', '20%', 'Ice_With_snow'])

# DIR = 'c:\\TSDE_Workarea\\ktt2yk\\Work\\VDC20\\MTCS\\'
# l_OUT = COPY_FILE(list(d_SEARCH), DIR)


# # Modify Signal

# ## Modify_Signal_CSSIM_INPUT

# In[13]:


def Modify_Signal_CSSIM_INPUT(l_Traces, File):
    l_Out = []
    
    d_Parameter = Read_DCM_5.Read_DCM(File)
    Abrollumfang_VA = d_Parameter['Abrollumfang_VA'][2][0]
    Abrollumfang_HA = d_Parameter['Abrollumfang_HA'][2][0]
    
    for Csv in l_Traces:
        print(Csv)
        df = pd.read_table(Csv, sep=",", index_col=None)
        
        # df['nMotNET_TRC'] = df['nMotNET_TRC'] / (2 * 3.14 / 60)        
        df['Ays'] = df['Ays'] * (-1)
        df['Yrs'] = df['Yrs'] * (-1)
        df['v_FL'] = df['v_FL'] * 3.6 * ((1000 / 3600) / Abrollumfang_VA * 60)
        df['v_FR'] = df['v_FR'] * 3.6 * ((1000 / 3600) / Abrollumfang_VA * 60)
        df['v_RL'] = df['v_RL'] * 3.6 * ((1000 / 3600) / Abrollumfang_HA * 60)
        df['v_RR'] = df['v_RR'] * 3.6 * ((1000 / 3600) / Abrollumfang_HA * 60)
        df['SasInCor'] = df['SasInCor'] * (-1) * 180 / 3.14
        # df['p_MC_Model'] = df['p_MC_Model'] * 10
        
        # if 'nMotNET_SMU' in df.columns:
        #     df['nMotNET_SMU'] = df['nMotNET_SMU'] / (2 * 3.14 / 60)
        
        root, ext = os.path.splitext(Csv)
        Csv_ = root + '_mod' + ext
        df.to_csv(Csv_, header=False, index=False)
        
        l_Out.append(Csv_)
        
    return l_Out


# In[14]:


def Modify_Signal_CSSIM_INPUT_pMC_10(l_Traces, File):
    l_Out = []
    
    d_Parameter = Read_DCM_5.Read_DCM(File)
    Abrollumfang_VA = d_Parameter['Abrollumfang_VA'][2][0]
    Abrollumfang_HA = d_Parameter['Abrollumfang_HA'][2][0]
    PT_DT_DiffRatio_Axle = d_Parameter['PT_DT_DiffRatio_Axle'][2][0]
    PT_DT_DiffRatio_Axle_2 = d_Parameter['PT_DT_DiffRatio_Axle_2'][2][0]
    
    for Csv in l_Traces:
        print(Csv)
        df = pd.read_table(Csv, sep=",", index_col=None)
        
        omega_FA = (df['v_FL'] + df['v_FR']) * 0.5 / (Abrollumfang_VA / 2 / math.pi)
        omega_RA = (df['v_RL'] + df['v_RR']) * 0.5 / (Abrollumfang_HA / 2 / math.pi)
        
        df['nMotNET_TRC'] = 0.995 * omega_RA * PT_DT_DiffRatio_Axle_2 / (2 * math.pi / 60.0)
        df['nMotNET_SMU'] = 0.955 * omega_FA * PT_DT_DiffRatio_Axle / (2 * math.pi / 60.0)
        
        # df['nMotNET_TRC'] = df['nMotNET_TRC'] / (2 * 3.14 / 60)        
        df['Ays'] = df['Ays'] * (-1)
        df['Yrs'] = df['Yrs'] * (-1)
        df['v_FL'] = df['v_FL'] * 3.6 * ((1000 / 3600) / Abrollumfang_VA * 60)
        df['v_FR'] = df['v_FR'] * 3.6 * ((1000 / 3600) / Abrollumfang_VA * 60)
        df['v_RL'] = df['v_RL'] * 3.6 * ((1000 / 3600) / Abrollumfang_HA * 60)
        df['v_RR'] = df['v_RR'] * 3.6 * ((1000 / 3600) / Abrollumfang_HA * 60)
        df['SasInCor'] = df['SasInCor'] * (-1) * 180 / 3.14
        df['p_MC_Model'] = df['p_MC_Model'] / 10
        
        # if 'nMotNET_SMU' in df.columns:
        #     df['nMotNET_SMU'] = df['nMotNET_SMU'] / (2 * 3.14 / 60)
        
        root, ext = os.path.splitext(Csv)
        Csv_ = root + '_mod' + ext
        df.to_csv(Csv_, header=False, index=False)
        
        l_Out.append(Csv_)
        
    return l_Out


# ## Modify_Signal_Simout

# In[15]:


def Modify_Signal_Simout(l_Traces, File):
    l_Out = []
    
    d_Parameter = Read_DCM_5.Read_DCM(File)
    Cp_FA = d_Parameter['Abrollumfang_VA'][2][0]
    Cp_RA = d_Parameter['Abrollumfang_HA'][2][0]
    
    for Csv in l_Traces:
        print(Csv)
        df = pd.read_table(Csv, sep=",", index_col=None)
        
        # df['nMotNET_TRC'] = df['nMotNET_TRC'] / (2 * 3.14 / 60)        
        df['BRK_TRQ_FL'] = df['BRK_TRQ_FL'] * Cp_FA
        df['BRK_TRQ_FR'] = df['BRK_TRQ_FR'] * Cp_FA
        df['BRK_TRQ_RL'] = df['BRK_TRQ_RL'] * Cp_RA
        df['BRK_TRQ_RR'] = df['BRK_TRQ_RR'] * Cp_RA
        
        root, ext = os.path.splitext(Csv)
        Csv_ = root + '_mod' + ext
        df.to_csv(Csv_, header=True, index=False)
        
        l_Out.append(Csv_)
        
    return l_Out


# ## Modify_Signal

# In[16]:


def Modify_Signal(l_Traces, d_Sig):
    l_Out = []
    
    for Csv in l_Traces:
        print(Csv)
        df = pd.read_table(Csv, sep=",", index_col=None)
        
        for S in d_Sig:
            if S in df.columns:
                df[S] = df[S] * d_Sig[S]
        
        root, ext = os.path.splitext(Csv)
        Csv_ = root + '_sig' + ext
        df.to_csv(Csv_, header=True, index=False)
        
        l_Out.append(Csv_)
        
    return l_Out


# In[17]:


def DIFF(data, n):
    data_ = data.diff() / SAMPLING
    
    if n != 0:
        data_ = data_.rolling(n, center=False).mean()
    
    data_ = data_.fillna(0)
    
    return data_


def INTEG(x, y):
    integ = integrate.cumtrapz(y, x)
    integ_ = [0] + list(integ)
    
    return integ_
    

# data_ = LOWPASS(list(data_), (0.5, 5, 1, 2))
def LOWPASS(x, _):
    samplerate = 1 / 0.005                                   #波形のサンプリングレート
    
    # fp = 0.5       #通過域端周波数[Hz]
    # fs = 5       #阻止域端周波数[Hz]
    # gpass = 1       #通過域端最大損失[dB]
    # gstop = 2      #阻止域端最小損失[dB]
    fp, fs, gpass, gstop = _ 

    fn = samplerate / 2                           #ナイキスト周波数
    wp = fp / fn                                  #ナイキスト周波数で通過域端周波数を正規化
    ws = fs / fn                                  #ナイキスト周波数で阻止域端周波数を正規化
    N, Wn = signal.buttord(wp, ws, gpass, gstop)  #オーダーとバターワースの正規化周波数を計算
    b, a = signal.butter(N, Wn, "low")  
    y = signal.filtfilt(b, a, x)                  #信号に対してフィルタをかける
    
    return y                                      #フィルタ後の信号を返す


# ## Run

# In[18]:


# OUT_PATH = 'c:/TSDE_Workarea/ktt2yk/Work/Traces/Honda-e/Winter_Fix/SIM_Vehicle/'
# DCM = 'c:/TSDE_Workarea/ktt2yk/Work/DCM/Honda-e_20230228/Honda-e/Complete_ESP10CB_VarCode_1_Honda_e.dcm'

# l_TRACE = MakeTraceList([OUT_PATH], ['.CSV', '.csv'], ['_mod.csv'])

# l_TRACE = Modify_Signal_CSSIM_INPUT(l_TRACE, DCM)
# l_TRACE = Modify_Signal_Simout(l_TRACE, DCM)


# # DATAFRAME

# ## CONCAT_DATA

# In[19]:


def CONCAT_DATA(l_DATA):
    n = 0
    
    for i, df_ in enumerate(l_DATA):
        n1 = n + len(df_)
        l_Index = list(np.arange(n, n1))
        df_['Index'] = l_Index
        df_ = df_.set_index('Index')

        if i == 0:
            df = df_
        else:
            df = pd.concat([df, df_])

        n = n1 + 1

    return df


# ## CONCAT_DATA_w_Transition

# In[1]:


def CONCAT_DATA_w_Transition(l_DATA, T_Transition):
    l_df = []
    df_k1 = None
    TIME = 0
    
    for i, df in enumerate(l_DATA):
        df_1, df_2, TIME = Dataframe_Transition(i, TIME, df_k1, df)

        l_df.append(df_1)
        l_df.append(df_2)

        df_k1 = df

    df_concat = CONCAT_DATA(l_df)
    
    df_concat['datetime'] = pd.to_datetime(df_concat['TIME']* 1000, unit='ms')
    df_concat.set_index('datetime', inplace=True)
    df_resampling = df_concat.resample('5L').mean()
    df_resampling.interpolate(method='linear', inplace=True)

    return df_resampling


# In[2]:


def Dataframe_Transition(i, T, df1, df2):
    data = {'TIME': [T, T+5]}
    df2['TIME'] = df2['TIME'] + T + 5.005
    T_out = df2['TIME'].max()
    
    l_col = list(df2.columns)
    l_col.remove('TIME')
    
    if i == 0:
        df2_ = df2.iloc[0]
        
        for S in l_col:
            data[S] = [df2_[S], df2_[S]]
    
    else:
        df1_ = df1.iloc[df1.index.max()]
        df2_ = df2.iloc[0]
        
        for S in l_col:
            data[S] = [df1_[S], df2_[S]]
    
    df = pd.DataFrame(data)
    
    return df, df2, T_out


# # CSSIM(Matlab) Run File

# ## MATLAB_RUN_FILE_ZIP

# In[20]:


def MATLAB_RUN_FILE_ZIP(l_Trace, Mdl, Path):
    Text = ''
    Out = Path + 'Matlab_Run_w_ZIP.m'
    
    for T in l_Trace:
        dirname, basename = os.path.split(T)
        root_, ext = os.path.splitext(basename)
        root = root_.replace('_mod', '')
        File_ = root + '_simout.zip'
        File_Sim = root + '_simout.xls'
        
        Text += 'delete INPUT.csv\n'
        Text += 'delete simout.xls\n'
        Text += 'copyfile ' + basename + ' INPUT.csv\n'
        Text += "sim('" + Mdl + "')\n"
        Text += 'movefile oml_bbxxxxx.zip ' + File_ + '\n'
        Text += 'delete INPUT.csv\n'
        Text += 'copyfile simout.xls ' + File_Sim + '\n'
        Text += '\n'
        
    f = open(Out, "w")
    f.write(Text)
    f.close()
    
    return Out


# ## MATLAB_RUN_FILE_D97

# In[21]:


def MATLAB_RUN_FILE_D97(l_Trace, Mdl, Path):
    Text = ''
    Out = Path + 'Matlab_Run_w_D97.m'
    
    for T in l_Trace:
        dirname, basename = os.path.split(T)
        root_, ext = os.path.splitext(basename)
        root = root_.replace('_mod', '')
        File_d97 = root + '.d97'
        File_zip = root + '_simout.zip'
        File_Sim = root + '_simout.xls'
        
        Text += 'delete INPUT.csv\n'
        Text += 'delete simout.xls\n'
        Text += 'copyfile ' + basename + ' INPUT.csv\n'
        Text += "sim('" + Mdl + "')\n"
        Text += 'movefile oml_bbxxxxx.d97 ' + File_d97 + '\n'
        Text += "zip('" + File_zip + "' , '" + File_d97 + "')\n"
        Text += 'delete INPUT.csv\n'
        Text += 'delete ' + File_d97 + '\n'
        Text += 'copyfile simout.xls ' + File_Sim + '\n'
        Text += '\n'
        
    f = open(Out, "w")
    f.write(Text)
    f.close()
    
    return Out


# ## MATLAB_RUN_FILE_wo_D97

# In[22]:


def MATLAB_RUN_FILE_wo_D97(l_Trace, Mdl, Path):
    Text = ''
    Out = Path + 'Matlab_Run_wo_D97.m'
    
    for T in l_Trace:
        dirname, basename = os.path.split(T)
        root_, ext = os.path.splitext(basename)
        root = root_.replace('_mod', '')
        # File_d97 = root + '_OOL.d97'
        # File_zip = root + '_OOL.zip'
        File_Sim = root + '_simout.xls'
        
        Text += 'delete INPUT.csv\n'
        Text += 'delete simout.xls\n'
        Text += 'copyfile ' + basename + ' INPUT.csv\n'
        Text += "sim('" + Mdl + "')\n"
        # Text += 'movefile oml_bbxxxxx.d97 ' + File_d97 + '\n'
        # Text += "zip('" + File_zip + "' , '" + File_d97 + "')\n"
        Text += 'delete INPUT.csv\n'
        # Text += 'delete ' + File_d97 + '\n'
        Text += 'copyfile simout.xls ' + File_Sim + '\n'
        Text += '\n'
        
    f = open(Out, "w")
    f.write(Text)
    f.close()
    
    return Out


# ## Run

# In[23]:


# SEARCH_PATH = ['c:/TSDE_Workarea/ktt2yk/Work/Traces/XT1E/SIM/Winter_Fix/2023_0222__Jenkins_N245_2ChTrqLatest_wBugFix/', 'c:/TSDE_Workarea/ktt2yk/Work/Traces/XT1E/SIM/Winter_Fix/2023_0302_XT1E_Bigslip/']
# OUT_PATH = 'c:/TSDE_Workarea/ktt2yk/Work/Traces/Honda-e/Winter_Fix/SIM_Vehicle/'

# MDL = 'HM_BB86152_Var01_M_TCS_HondaE_RWD_20230315.mdl'
# MDL = 'HM_BB86153_Var01_M_TCS_XT1E_4WD_20230317_OOL.mdl'
# MDL = 'HM_BB86153_Var01_M_TCS_XT1E_4WD_20230317.mdl'

# l_TRACE = MakeTraceList(SEARCH_PATH, ['_mod.CSV', '_mod.csv'], [])

# MATLAB_RUN_FILE_ZIP(l_TRACE, MDL, OUT_PATH)
# MATLAB_RUN_FILE_D97(l_TRACE, MDL, OUT_PATH)
# MATLAB_RUN_FILE_wo_D97(l_TRACE, MDL, OUT_PATH)


# # CSSIM SIMOUT to CSV

# ## SIMOUT_to_CSV

# In[24]:


def SIMOUT_to_CSV(l_Trace, Plt):
    l_Out = []
    
    d_Signal = Select_Signal(Plt)
    
    for T in l_Trace:
        df = pd.read_excel(T, header=None)
        df_ = pd.read_excel(T, header=None)
        
        for e, Col in enumerate(df.columns):
            if e == 0:
                df_ = df_.rename(columns={e: "TIME"})
            else:
                S = list(d_Signal.keys())[e - 1]
                df_ = df_.rename(columns={e: S})
        
        root, ext = os.path.splitext(T)
        T_ = root + '.csv'
        df_.to_csv(T_, index=False)
        
        l_Out.append(T_)
    
    return l_Out


# ## Run

# In[25]:


# SEARCH_PATH_SIMOUT = ['c:/TSDE_Workarea/ktt2yk/Work/Traces/Honda-e/Winter_Fix/SIM_OOL_w_D97/', 'c:/TSDE_Workarea/ktt2yk/Work/Traces/Honda-e/Winter_Fix/SIM_OOL_wo_D97/']
# PLT_SIMOUT = 'c:/TSDE_Workarea/ktt2yk/Work/PLT/MTCS_MEDC_SIMOUT_1CH.PLT'

# l_TRACE = MakeTraceList(SEARCH_PATH_SIMOUT, ['_simout.xls'], [])
# SIMOUT_to_CSV(l_TRACE, PLT_SIMOUT)


# # PATH

# In[26]:


def CHANGE_PATH(Path):
    Path = Path.replace('c:/TSDE_Workarea/ktt2yk', '')
    Path = Path.replace('c:\\TSDE_Workarea\\ktt2yk', '')
    Path = Path.replace('\\', '/')
    
    return Path


# # PLOT to COMPARE 

# ## READ_DATA

# In[27]:


def READ_DATA(l_Trace, Signal, Time, Delay):
    l_Out = []
    
    S1, S2 = Signal
    T1, T2 = Time
    
    for S2_ in S2:
        S2__ = S2[S2_]
        
        X = []
        Y = []
        L = []

        for e, F in enumerate(l_Trace):
            Csv = l_Trace[e]
            df = pd.read_table(Csv, sep=",", index_col=None)
            df['TIME'] = df['TIME'] + Delay[e]
            # df.drop(columns=['TIME', 'C'])
            
            Con = 'TIME >= ' + str(T1) + ' and TIME <= ' + str(T2) 
            df_ = df.query(Con)
            x = df_[S1]
            y = df_[S2_]
            
            X.append(x)
            Y.append(y)
            L.append(F)

        Out = (S1, S2__, X, Y, L)
        l_Out.append(Out)
    
    return l_Out


# ## PLOT

# In[28]:


def PLOT(d_Trace, PLT, _, fig_setting, Dir):    
    d_ = Select_Signal(PLT)
    SIGNAL = ('TIME', d_)
    TIME, DELAY, LABEL = _
    
    figsize_x_, figsize_y_, dpi_ = fig_setting[0]
    left_, right_, bottom_, top_ = fig_setting[1]
    
    l_Fig = []
    
    for e, title in enumerate(d_Trace):
        l_Trace_ = d_Trace[title]

        for T in l_Trace_:
            print(T)

        if len(TIME) == 1:
            TIME_ = TIME[0]
        else:
            TIME_ = TIME[e]

        if len(DELAY) == 1:
            DELAY_ = DELAY[0]
        else:
            DELAY_ = DELAY[e]

        if len(LABEL) == 1:
            LABEL_ = LABEL[0]
        else:
            LABEL_ = LABEL[e]

        # FIG_ = FIG[e]
        # l_DATA_ = l_DATA[e]
        # root, ext = os.path.splitext(l_Trace_[0])
        # dirname, basename = os.path.split(l_Trace_[0])
        FIG_ = Dir + title + '.png'

        # basename = os.path.basename(l_Trace_[0])
        # root, ext = os.path.splitext(basename)
        # Title = root

        l_DATA = READ_DATA(l_Trace_, SIGNAL, TIME_, DELAY_)
        
        PLOT = False
        for n, _ in enumerate(l_DATA):
            S1, S2, X, Y, Label = _
            
            if len(X) >= 2:
                PLOT = True
                break
        
        if PLOT == True:
            fig = plt.figure(figsize=(figsize_x_, figsize_y_), dpi=dpi_)
            fig.subplots_adjust(left=left_, right=right_, bottom=bottom_, top=top_)

            for n, _ in enumerate(l_DATA):
                S1, S2, X, Y, Label = _

                n1 = len(l_DATA)
                ax = fig.add_subplot(n1, 1, n+1)

                x_lim0, x_lim1 = RANGE_LIMIT(X, TIME_)

                for m, x in enumerate(X):
                    y = Y[m]

                    # root, ext = os.path.splitext(Label[m])
                    # ax.plot(x, y, label=root)
                    ax.plot(x, y, label=LABEL_[m])

                    # ax.set_ylabel(S2)
                    ax.set_ylabel(S2[-14:])
                    # ax.set_xlim(TIME[0], TIME[1])
                    ax.set_xlim(x_lim0, x_lim1)

                if n < len(l_DATA) - 1:
                    ax.tick_params(labelbottom=False)

                plt.legend(loc='upper left', bbox_to_anchor=(1, 1.03)) 

            ax.set_xlabel(S1)
            # plt.suptitle(root, fontsize=10)
            plt.suptitle(title)
            plt.show()

            fig.savefig(FIG_)
            l_Fig.append(FIG_)
        
    return l_Fig


def RANGE_LIMIT(X, T):
    T_Min = T[0]
    T_Max = T[1]
    
    for e, x in enumerate(X):
        T_Min = max(T_Min, min(x))
        T_Max = min(T_Max, max(x))
    
    return T_Min, T_Max


# ## COMPARE LIST

# In[29]:


def COMPARE_LIST(Path, l_Key):
    d_Out = {}
    
    l_Traces = MakeTraceList(Path, l_Key, [])
    # print(l_Traces)
    
    l_basename = []
    for T in l_Traces:
        dirname, basename = os.path.split(T)
        
        basename_ = basename
        for Key in l_Key:
            basename_ = basename_.replace(Key, '')
        l_basename.append(basename_)
        
    l_basename_ = list(set(l_basename))        
    
    for basename in l_basename_:        
        l_Out1 = []
        for T in l_Traces:
            if basename in T:
                l_Out1.append(T)
        
        l_Out2 = []
        for Key in l_Key:
            for Out1 in l_Out1:
                if Key in Out1:
                    l_Out2.append(Out1)
                    l_Out1.remove(Out1)

        d_Out[basename] =l_Out2
        
    return d_Out


# In[30]:


# COMPARE_PATH_3 = ['c:/TSDE_Workarea/ktt2yk//Work/Traces/XT1E/SIM/Winter_Fix/SIM_Vehicle/', 'c:/TSDE_Workarea/ktt2yk/Work/Traces/XT1E/SIM/Winter_Fix/SIM_OOL_wo_D97_20230327/']
# OUT_PATH = 'c:/TSDE_Workarea/ktt2yk/Work/Traces/XT1E/SIM/Winter_Fix/SIM_OOL_wo_D97_20230327/'
# PLT_VIEW = 'c:/TSDE_Workarea/ktt2yk/Work/PLT/MTCS_MEDC_SIMOUT_VIEW_2CH.PLT'
# FIG_SETTING = ((10, 6, 100), (0.07, 0.90, 0.1, 0.95))

# TIME = [(1, 1000)]
# DELAY = [[0, 0]]
# # LABEL = [['Sim1', 'Sim2']]
# LABEL = [['Veh', 'Sim']]

# # d_COMPARE = COMPARE_LIST(COMPARE_PATH_1, ['_simout.csv', '_simout.csv'])
# # d_COMPARE = COMPARE_LIST(COMPARE_PATH_2, ['_simout.csv', '_mod.csv'])
# d_COMPARE = COMPARE_LIST(COMPARE_PATH_3, ['_mod.csv', '_simout.csv'])

# l_FIG = PLOT(d_COMPARE, PLT_VIEW, (TIME, DELAY, LABEL), FIG_SETTING, OUT_PATH)

