import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
import subprocess, json, threading, statistics, time, webbrowser, os, re
import concurrent.futures


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

    def textField_var(self, lbl,var, w_, x_, y_):
        textField = tk.Entry(self.master, textvariable=var, width=w_)
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
        b = tk.Label(self.master, textvariable=charVariable)
        b.grid(row=y_, column=x_, sticky=algn)
        return b


    def popupMenu(self, charVariable,choices,x_,y_,width,stick):
        popupMenu=tk.OptionMenu(self.master, charVariable, *choices)
        popupMenu.configure(width=width)
        popupMenu.grid(row=y_,column=x_,sticky=stick)
        # self.labelMenu=tk.Label(self.master,text=label)
        # self.labelMenu.grid(row=y_, column=x_-1)


class appFuncs:
    @staticmethod
    def thread(*args):
        n=1
        for i in args:
            if n==0:
               self = i
            if n==1:
                command = i
            if n==2:
                is_daemon = i
            n+=1
        # self.update_idletasks()
        x = threading.Thread(target=subprocess.run, args=[command])
        x.daemon = is_daemon
        x.start()

    def process(self,command):
        subprocess.run(command)


    # Generates file dialog box
    @staticmethod
    def selectPath():
        file_path = '' #todo replace with current path
        f = tk.filedialog.askdirectory()
        if f != '':
            file_path = f
        return file_path

    @staticmethod
    def select_file(title):
        file_path = ''
        f = tk.filedialog.askopenfilename(title=title, filetypes =(("NIFTI files","*.nii.gz*"),("all files","*.*")))
        if f != '':
            file_path = f
        return file_path

        # generates output folder path
    @staticmethod
    def generate_analysis_name(roi_tree):
        roi_name = roi_tree.selection_name
        name = f'PPI_{roi_name}'
        return name


    # generates output folder path
    @staticmethod
    def generateOutpath(inPath, prefix, suffix):
        z=inPath.stem.replace(prefix,'');  z=z+suffix
        outPath = (Path(inPath).parent) / z
        return outPath

    @staticmethod
    def generateProcessedOutpath(path):
        fo=Path(path).glob('*.feat')
        processedOutpath=''
        for i in fo:
           processedOutpath=i
        return processedOutpath

    # Identify previously processed datasets
    @staticmethod
    def prevProcessed(outPath):
        pvp = 0
        if Path(outPath).is_dir(): pvp = 1
        return pvp

    @staticmethod
    def postProcessed(path):
        # idenitfy if the dataset has been processed through ICA and post-processed as well
        pop = 0
        # is feat file present?
        # print(path)
        fo=Path(path).glob('*.feat')
        for i in fo:
            if i.is_dir() == True:
                pop = 1
        return pop

    @staticmethod
    def postProcessed_identifier(path):
        # if melodic.ica is a sibling directory, then this is assumed to be post-processed dataset generated from
        # ICA-AROMA processed data
        pop_i = 0
        fo = Path(path).parent/'melodic.ica'
        if fo.is_dir() == True: pop_i = 1
        return pop_i

    @staticmethod
    def write_to_file(file_obj,text,loc):
        pass




class Viewer:

    def __init__(self,parent):
        self.parent = parent
        parent.protocol("WM_DELETE_WINDOW", self.do_nothing)
        parent.minsize(300, 400)
        self.parent.title(': Image Viewer')
        self.fr = tk.Frame(parent,borderwidth=1, padx=20,pady=10)
        self.fr.pack(fill = "both", expand = True)

    def display(self, im_list, mode):
        self.clearFrame(self.fr)

        # Unprocessed viewer
        if mode == 1:
            self.main_im_list = im_list
            self.labels = ['Psychological', 'Physiological', 'Interaction (Pos)', 'Interaction (Neg)']
            frame = self.fr
            self.main_image_viewer(frame)

        # Processed but not post processed
        if mode == 2:
            frame = self.fr
            self.IC_im_list = im_list
            self.scroll_viewer_setup(frame)
            self.scroll_viewer()


    def main_image_viewer(self, frame):
        el = Elements(frame)
        for i in range(0, len(self.main_im_list)):
            el.label1(self.labels[i], 0, 2*i, 'nesw', 1, 1)
            self.fr.rowconfigure(2*i+1, weight=1)
            im_path = self.main_im_list[i]
            photo = tk.PhotoImage(file=im_path)
            label = tk.Label(frame, image=photo, pady=20)
            label.photo = photo
            label.grid(row=2*i+1)


    def scroll_viewer_setup(self,fr):
        self.ic = len(self.IC_im_list)
        self.j = 0
        self.count = tk.StringVar()
        self.count.set(f'{self.j + 1} of {self.ic} Motion associated independent components')
        el = Elements(fr)
        el.button('Previous', self.scroll, -1, 0, 0, 'e', 1)
        el.button('  Next  ', self.scroll, 1, 1, 0, 'w', 1)
        el.label2(self.count, 2, 0, 'w')
        self.frame_scroll = tk.Frame(fr, borderwidth=1,  padx=20, pady=10)
        self.frame_scroll.grid(row=1, columnspan=10, sticky='nsew')


    def scroll(self, scr):
        self.j += scr
        if (self.j >= self.ic):
            self.j = self.ic-1
        if self.j<0:
            self.j = 0
        self.count.set(f'{self.j + 1} of {self.ic} components')
        self.clearFrame(self.frame_scroll)
        self.scroll_viewer()

    def scroll_viewer(self):
        ic_im_path = self.IC_im_list[self.j]
        photo = tk.PhotoImage(file=ic_im_path)
        label = tk.Label(self.frame_scroll, image=photo, pady=20)
        label.photo = photo
        label.grid(row=0, sticky='nsew')

    def clearFrame(self,frame):
        # destroy all widgets from frame
        for widget in frame.winfo_children():
           widget.destroy()

    @staticmethod
    def do_nothing():
        pass


# class roi_funcs:
#     def __init__(self,master,roi_path, roi_search, roi_tree):
#         self.master = master
#         self.er = Elements(self.master)
#         self.roi_path = roi_path
#         self.roi_search = roi_search
#         self.roi_tree = roi_tree
#
#     def atlas_based(self):
#         # Threshold
#         self.thr_low = self.er.textField('Threshhold (low)',10,1,1)
#         self.thr_high = self.er.textField('Threshhold (high)', 10, 3, 1)
#         # Binarize button
#         self.er.button('Binarize',self.binarize,'',1,2,'w',1)
#
#         command = ['fsleyes','-std']
#         # subprocess.run(command)
#
#
#     def binarize(self):
#         roi_path = self.roi_tree.file_path
#         roi = self.roi_tree.selection_name
#         output = roi+ '_bin'
#         low = self.thr_low.get()
#         high = self.thr_high.get()
#         # threshold
#         command = ['fslmaths',Path(roi_path)/roi]
#         if low: command += ['-thr',low]
#         if high:command += ['-uthr', high]
#         if low or high:
#             command += [Path(roi_path)/output]
#             print(command)
#             subprocess.run(command)
#             input = output
#         else:
#             input = roi
#         # Binarize
#         command = ['fslmaths', Path(roi_path)/input, '-bin',Path(roi_path)/output]
#         subprocess.run(command)
#
#     def peak_group(self):
#         self.er.button('Select image', self.cluster_select, '', 0, 1, 'w', 1)
#         self.er.button('Extract', self.cluster_extract, '', 0, 2, 'w', 1)
#         print('Peak Group')
#
#     def peak_individual(self):
#         print('Peak Individual')
#
#     def group_differences(self):
#         print('Group Differences')
#
#     def geometry_based(self):
#         # self.FSLDIR = os.environ['FSLDIR']
#         self.FSLDIR = '/usr/local/fsl/'
#
#         self.x_c = self.er.textField(f'x:', '3', 4, 1)
#         self.y_c = self.er.textField(f'y:', '3', 7, 1)
#         self.z_c = self.er.textField(f'z:', '3', 10, 1)
#         self.roi_name = self.er.textField(f'ROI Name: ', '20', 15, 1)
#         # Size of ROI
#         self.roi_size = self.er.textField(f'Size (mm): ', '5', 12, 1)
#         self.er.button('Generate ROI', self.geometry_process, '', 20, 1, 'w', 1)
#         # self.er.button('Generate ROI', fn.appFuncs.thread, (self.master, self.geometry_process,True), 20, 1, 'w', 1)
#
#         # Standard image
#         standard_search = Path(f'{self.FSLDIR}data/standard').glob('*.nii.gz')
#         self.standard_list =[e.name for e in standard_search]
#         self.standard_list.sort()
#         self.image_var = tk.StringVar(self.master)
#
#         self.std_image_options = self.er.popupMenu(self.image_var,self.standard_list,1,1,25,'w')
#         self.image_var.set(self.standard_list[22])
#
#         # Geometry options
#         self.option_var =tk.StringVar(self.master)
#         self.geometries = ['sphere','box','gauss']
#         self.geometry_options = self.er.popupMenu(self.option_var,self.geometries,1,2,10,'w')
#         self.option_var.set(self.geometries[0])
#
#     def geometry_process(self):
#         self.master.update_idletasks()
#         point_name = Path(self.roi_path) / f'{str(self.roi_name.get())}_point.nii.gz'
#         roi_name_unbin = Path(self.roi_path) / f'{self.roi_name.get()}_unbin.nii.gz'
#         roi_name = Path(self.roi_path) / f'{self.roi_name.get()}.nii.gz'
#         template = f'{self.FSLDIR}data/standard/{self.image_var.get()}'
#
#         # Generate a point for the seed region
#         command = ['fslmaths', template, '-mul', '0', '-add', '1', '-roi', str(self.x_c.get()), '1', str(self.y_c.get()), '1',
#                    str(self.z_c.get()), '1', '0', '1', str(point_name), '-odt', 'float']
#         subprocess.run(command)
#         # Generate an ROI around the point
#         command = ['fslmaths', point_name, '-kernel', self.option_var.get(), str(self.roi_size.get()), '-fmean', roi_name_unbin,  '-odt', 'float']
#         subprocess.run(command)
#         # Binarize the ROI mask
#         command = ['fslmaths', roi_name_unbin, '-bin', roi_name]
#         subprocess.run(command)
#         # Delete point and non-binarized files
#         Path(point_name).unlink()
#         Path(roi_name_unbin).unlink()
#
#         self.roi_search()
#
#     def cluster_select(self):
#         self.var = appFuncs.select_file('Select image file')
#         self.cluster_num()
#         self.cluster = self.er.textField(f'Cluster Number (0-{self.cluster_indexes[0]})', '10', 1, 1)
#
#     def cluster_extract(self):
#         cluster = str(self.cluster.get())
#         mask_name = Path(self.roi_path)/f'extracted_cluster_{cluster}.nii.gz'
#         command = ['fslmaths','-dt','int', self.var, '-thr', cluster, '-uthr', cluster, '-bin', mask_name]
#         subprocess.run(command)
#         print('Extraction complete!')
#
#     def cluster_num(self):
#         self.cluster_indexes =[]
#         file_dir = Path(self.var).parent
#         file_name = Path(Path(self.var).stem).stem
#
#         file_name = str(file_name)
#         m = re.search('zstat(.+?)', file_name)
#         if m:
#             name = Path(file_dir)/f'cluster_zstat{m.group(1)}_std.txt'
#             print(str(name))
#             if Path(name).is_file():
#                 # read and extract data
#                 with open(name) as f:
#                     i = 0
#                     for line in f:
#                         if i == 0:
#                             break
#                     data = [r.split() for r in f]
#                     for r in data:
#                         print(f'{r[0]}     {r[1]}')
#                         self.cluster_indexes.append(r[0])
#                 f.close()
#
#     def blank(self):
#         pass