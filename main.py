import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
from bs4 import BeautifulSoup
import subprocess, json, threading, statistics, time, webbrowser
import concurrent.futures

test_case = 1
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

#   class for tkinter Treeview and related functions
class result_window:

    def __init__(self, parent,stat, headings, name):
        # Draw a treeview of a fixed type
        # self.viewer=viewer
        self.stat=stat
        self.parent=parent
        self.fileList=[]
        self.tree = ttk.Treeview(self.parent, show='headings', columns=headings)
        self.tree.grid(sticky='NSEW')
        for n in range(len(name)):
            self.tree.heading(headings[n], text=name[n])
        self.tree.column(headings[0], width=30, stretch=tk.NO, anchor='e')
        self.tree.column(headings[1], width=400)


        self.tree.bind('<Button-1>',self.left_click)
        self.tree.bind('d', self.delete_entry)
        # self.tree.bind(('<Button-3>' ), self.double_left_click)
        # self.tree.bind(('<Button-2>'), self.double_left_click)
        # self.tree.bind(('w'), self.double_left_click)
        self.last_focus = None


    def display(self):

        self.delete()
        index = iid = 0
        self.abs=[]
        self.rel=[]
        for row in self.fileList:
            # print(row)
            inPath = row[0]

            # pvp = row[3]
            # pop = row[4]

            p1 = inPath.relative_to(self.file_path)
            disp = '  >>  '.join(p1.parts)
            self.tree.insert("", index, iid, values=(iid + 1, disp))

            index = iid = index + 1


    # generate queue for processing
    def queue(self):
        fl = self.fileList
        # id = list(range(0, len(fl)))
        index = self.tree.selection()
        # if any items are selected, modify the file list to be processed
        if len(index) != 0:
            N = [int(i) for i in index]
            fl = [fl[j] for j in N]
            # id = N
        return fl
    # clears selection of all items in treeview
    def clear(self):
        for item in self.tree.selection(): self.tree.selection_remove(item)
        # self.viewer.clearFrame()

    def delete(self):
        self.tree.delete(*self.tree.get_children())

    # display status of a treeview item
    def processing_status(self, iid, stsMsg):
        self.tree.set(iid, 'Status', stsMsg)
        self.parent.update_idletasks()

    def left_click(self, event):
        iid = self.tree.identify_row(event.y)
        self.clickID = iid
        if not iid == '':
            iid = int(iid)

    def delete_entry(self, event):
        iid = self.clickID
        if not iid == '':
            iid = int(iid)
            del self.fileList[iid]
            self.delete()
            self.display()
            self.clickID = ''

class MainArea(tk.Frame):
    def __init__(self, master,stat, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        self.stat = stat
        # self.viewer = viewer
        # self.config = config
        self.overwrite = tk.IntVar()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.master = master

        # Frame for all controls
        self.f1 = tk.LabelFrame(self, text='Controls', borderwidth=1, padx=10, pady=10, relief='raised')
        self.f1.grid(row=0, column=0, sticky='NSEW',columnspan = 2)

        # Frame for File list Tree View
        self.f2 = tk.Frame(self, borderwidth=0, relief='raised', pady=10)
        self.f2.grid(row=1, column=0, sticky='NSEW')
        self.f2.columnconfigure(0, weight=1)
        self.f2.rowconfigure(0, weight=1)

        # Frame for File list Tree View
        self.f3 = tk.Frame(self, borderwidth=0, relief='raised', pady=10)
        self.f3.grid(row=1, column=1, sticky='NSEW')
        # self.f3.columnconfigure(0, weight=.5)
        self.f3.rowconfigure(0, weight=1)

        # Individual elements
        # Display results and status
        self.result_tree = result_window(self.f2, stat,['Number','Name', 'Status'], ['#', 'Name', 'Status'])
        # Display ROIs
        self.roi_tree = result_window(self.f3, stat,['Number', 'Name'], ['#', 'ROI'])

        # Display results and status
        # self.result_tree = result_window(self.f2, viewer, stat)

        self.file_path = ''
        self.roi_path = ''

        # Controls
        el = Elements(self.f1)
        el.button("Database", self.selectPath, {self.file_path}, 0, 0, tk.W + tk.E, 1)  # Selection of root directory
        el.button("Select ROI", self.selectPath, {self.roi_path}, 0, 1, tk.W + tk.E, 1)  # Selection of root directory
        el.button("Timecourse", self.generate_timecourse, '', 0, 2, tk.W + tk.E, 1)  # Generate time course
        el.button("Generate Profile", self.generate_profile, '', 0, 3, tk.W + tk.E, 1)  # Generate profile
        el.button("Process", self.process, '', 0, 4, tk.W + tk.E, 1)  # Generate profile

        self.dataset = el.textField("Identifier", 20, 1, 0)  # Task or Dataset to be searched for
        self.filters = el.textField("Filters", 20, 1, 1)  # keywords to filter individual datasets
        el.button("Search", self.search, '', 3, 0, tk.N + tk.S, 1)  # button press to start search
        el.button("Clear", self.search, '', 3, 1, tk.N, 1)  # button press to clear selection
        # el.check('Overwrite', self.overwrite, 4, 1)  # checkbox for overwrite option


        # method for calling directory picker
    def selectPath(self, var):
        if test_case == 1:
            root = Path(__file__).parent.absolute()
            self.roi_path = self.roi_tree.file_path = root/'test_data'/'PPI'
            self.file_path = root/'test_data'/'Subject'
        else:
            var = appFuncs.selectPath()
            self.stat.set('Database Selected: %s', var)
            print(var)
        # self.result_tree.file_path = self.file_path


        # executed on clicking search button, this function lists all the datasets
    def search(self):
        #  ROI Search
        r_list = Path(self.roi_path).glob(f'*.nii*')
        roi_list = []
        self.roi_tree.fileList = roi_list
        for j in r_list:
            roi_list.append([j,100])
        self.roi_tree.display()
        self.roi_tree.fileList = roi_list

        ##############################

        self.result_tree.file_path = self.file_path
        dataset = self.dataset.get()
        identifier = f'*{dataset}*.feat'
        if dataset=='':identifier = f'*.feat'

        # Search for all files that match task
        search_list = Path(self.file_path).rglob(f'{identifier}')

        filtered_list = self.apply_filters(search_list)
        self.result_tree.fileList = self.aggregated_list(filtered_list)
        self.result_tree.display()  # display the results


    #  generates time course for each user in the list
    def generate_timecourse(self):

        roi_id = self.roi_tree.clickID
        roi = self.roi_tree.fileList[int(roi_id)][0]
        roi_name = Path(Path(roi).stem).stem
        cluster_name_unbin = roi_name + '_unbin_native.nii.gz'
        cluster_name_bin = roi_name + '_bin_native.nii.gz'
        timecourse_name = f'timecourse_{roi_name}.txt'


        for row in self.result_tree.fileList:
            file = row[0]
            subject = file
            # subject = Path(file).parent
            mat_file = subject / 'reg' / 'standard2example_func.mat'
            ref = subject/ 'filtered_func_data.nii.gz'
            print(f'File : {subject}    and cluster name unbin is {cluster_name_unbin}')

            flirt = ['flirt', '-in', roi, '-omat', mat_file, '-ref', ref, '-out', subject/cluster_name_unbin]
            maths = ['fslmaths', subject/cluster_name_unbin, '-bin', subject/cluster_name_bin]
            meants = ['fslmeants', '-i', ref, '-o', subject/timecourse_name, '-m', subject/cluster_name_bin]
            print(flirt)
            print('\n\n')
            subprocess.run(flirt)
            subprocess.run(maths)
            subprocess.run(meants)
        print('Timecourses Generated!')


    #  Allows user to create a custom design profile which can then be applied to all datasets
    def generate_profile(self):
        # use a sample profile to load the basics and
        # call FSL from here and run the FEAT tool.
        id = 0
        for row in self.result_tree.fileList:
            if id == 0:
                subject = row[0]
                id += 1
            else:
                break
        roi_id = self.roi_tree.clickID
        roi = self.roi_tree.fileList[int(roi_id)][0]
        roi_name = Path(Path(roi).stem).stem
        output_dir = subject/f'PPI_{roi_name}.feat'
        subject_dir = subject/'filtered_func_data.nii.gz'
        subject_timecourse = subject/f'timecourse_{roi_name}.txt'

        root = Path(__file__).parent.absolute()
        sample_profile = root /'sample_design.fsf'
        base_profile = root /'temp'/'temp_design.fsf'
        subprocess.run(['cp', sample_profile, base_profile])
        # read in the base profile
        fin = open(base_profile, "rt")
        data = fin.read()
        data = data.replace('#%#',str(output_dir))
        data = data.replace('#$#', str(subject_dir))
        data = data.replace('#!#', str(subject_timecourse))

        fin.close()
        fin = open(base_profile, "wt")
        fin.write(data)
        fin.close()

        subprocess.run(['Feat', base_profile])


        # reverse the subject specific paths
        fin = open(base_profile, "rt")
        data = fin.read()
        data = data.replace(str(output_dir), '#%#')
        data = data.replace(str(subject_dir), '#$#')
        data = data.replace(str(subject_timecourse), '#!#')

        fin.close()
        fin = open(base_profile, "wt")
        fin.write(data)
        fin.close()

    def process(self):
        root = Path(__file__).parent.absolute()
        base_profile = root /'temp'/'temp_design.fsf'

        roi_id = self.roi_tree.clickID
        roi = self.roi_tree.fileList[int(roi_id)][0]
        roi_name = Path(Path(roi).stem).stem

        for row in self.result_tree.fileList:
            subject = row[0]
            print(subject)
            subject_profile = root/'temp'/ f'temp_{Path(subject).stem}.fsf'
            output_dir = subject / f'PPI_{roi_name}.feat'
            subject_dir = subject / 'filtered_func_data.nii.gz'
            subject_timecourse = subject / f'timecourse_{roi_name}.txt'
            subprocess.run(['cp', base_profile, subject_profile])
            # subject_profile = base_profile
            # read in and modify the subject profile

            print(str(subject_profile))
            fin = open(subject_profile, "rt")
            data = fin.read()
            data = data.replace('#%#', str(output_dir))
            data = data.replace('#$#', str(subject_dir))
            data = data.replace('#!#', str(subject_timecourse))

            fin.close()
            fin = open(subject_profile, "wt")
            fin.write(data)
            fin.close()

            subprocess.run(['feat', subject_profile])
            subprocess.run(['rm', '-rf', f'temp/{subject_profile}'])

        # empty the temp folder
        subprocess.run(['rm', '-rf','temp/*'])


    def apply_filters(self,file_list):
        # List of datasets as string for display purposes
        filters = self.filters.get()
        if len(filters) != 0:
            filters = filters.split(";")
            fl = [row for row in file_list if any(f in str(row) for f in filters)]
        else:
            fl = file_list
        return fl

    def aggregated_list(self, filtered_list):
        fl = []
        for row in filtered_list:
            fl.append([row,1])
        return fl


#-----------------------------------------------------------------------------------------------------------------------

class StatusBar(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.label = tk.Label(self, bd=1, relief='sunken', anchor='w')
        self.label.pack(fill=tk.X)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()

#-----------------------------------------------------------------------------------------------------------------------


class appFuncs:
    # Generates file dialog box
    @staticmethod
    def selectPath():
        file_path = '' #todo replace with current path
        f = tk.filedialog.askdirectory()
        if f != '':
            file_path = f
        return file_path

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
        self.statusbar = StatusBar(parent)
        self.mainarea = MainArea(parent, self.statusbar, borderwidth=1, relief=tk.RAISED)

        # configurations
        self.mainarea.grid(column=0, row=0, sticky='WENS')
        self.statusbar.grid(column=0, row=1, sticky='WE')
        self.statusbar.set('Ready')

#-----------------------------------------------------------------------------------------------------------------------


root = tk.Tk()
PR = MainApp(root)
root.mainloop()

# todo make functions to remove all repetitions
# todo save temp design file in temp folder and just edit that instead