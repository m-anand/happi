import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
from bs4 import BeautifulSoup
import subprocess, json, threading, statistics, time, webbrowser, os, re
import concurrent.futures

test_case = 2
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


    def popupMenu(self, charVariable,choices,x_,y_,width,stick):
        popupMenu=tk.OptionMenu(self.master, charVariable, *choices)
        popupMenu.configure(width=width)
        popupMenu.grid(row=y_,column=x_,sticky=stick)
        # self.labelMenu=tk.Label(self.master,text=label)
        # self.labelMenu.grid(row=y_, column=x_-1)

#  Class for tkinter Treeview and related functions
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
            self.selection = self.fileList[iid][0]
            self.selection_name = Path(Path(self.selection).stem).stem

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
        self.f0 = tk.Frame(self, borderwidth=1, relief='raised')
        # self.f0.pack(fill = "both")
        self.f0.grid(row=0, column=0, sticky='NSEW', columnspan=2)

        notebook =ttk.Notebook(self.f0)
        notebook.pack(expand = 1, fill = "both")

        # Frame for PPI
        # self.f1 = tk.LabelFrame(notebook, text='Controls', borderwidth=1, padx=10, pady=10, relief='raised')
        self.fr_ppi = tk.Frame(notebook)
        self.fr_ppi.grid(row=0, column=0, sticky='NSEW', columnspan = 2)

        # Frame for ROI generation
        # self.f4 = tk.LabelFrame(notebook, text='Controls', borderwidth=1, padx=10, pady=10, relief='raised')
        self.fr_roi_gen = tk.Frame(notebook, borderwidth=1, padx=10, pady=10, relief='raised')
        self.fr_roi_gen.grid(row=0, column=0, sticky='NSEW', columnspan = 2)

        self.fr_roi_gen_child = tk.Frame(self.fr_roi_gen, borderwidth=1, padx=10, pady=10)
        self.fr_roi_gen_child.grid(row=1, column=0, sticky='NSEW')


        notebook.add(self.fr_ppi, text ="PPI")
        notebook.add(self.fr_roi_gen, text ="Generate ROI")



        # Frame for File list Tree View
        self.fr_results = tk.Frame(self, borderwidth=0, relief='raised', pady=10, padx = 2)
        self.fr_results.grid(row=1, column=0, sticky='NSEW')
        self.fr_results.columnconfigure(0, weight=1)
        self.fr_results.rowconfigure(0, weight=1)

        # Frame for ROI Tree View
        self.fr_roi_name = tk.Frame(self, borderwidth=0, relief='raised', pady=10, padx = 2)
        self.fr_roi_name.grid(row=1, column=1, sticky='NSEW')
        # self.f3.columnconfigure(0, weight=.5)
        self.fr_roi_name.rowconfigure(0, weight=1)

        # Individual elements
        # Display results and status
        self.result_tree = result_window(self.fr_results, stat, ['Number', 'Name', 'Status'], ['#', 'Name', 'Status'])
        # Display ROIs
        self.roi_tree = result_window(self.fr_roi_name, stat, ['Number', 'Name'], ['#', 'ROI'])

        # Display results and status
        # self.result_tree = result_window(self.f2, viewer, stat)

        self.file_path = ''
        self.roi_path = ''

        # Controls
        el = Elements(self.fr_ppi)
        el.button("Database", self.selectPath, 1, 0, 0, tk.W + tk.E, 1)  # Selection of root directory
        el.button("Select ROI", self.selectPath, 2, 0, 1, tk.W + tk.E, 1)  # Selection of ROI directory
        el.button("Timecourse", self.generate_timecourse, '', 0, 2, tk.W + tk.E, 1)  # Generate time course
        el.button("Generate Profile", self.generate_profile, '', 0, 3, tk.W + tk.E, 1)  # Generate profile
        el.button("Process", self.process, '', 0, 4, tk.W + tk.E, 1)  # Generate profile

        self.search_str = el.textField("Identifier", 20, 1, 0)  # Task or Dataset to be searched for
        self.filters = el.textField("Filters", 20, 1, 1)  # keywords to filter individual datasets
        el.button("Search", self.search, '', 3, 0, tk.N + tk.S, 1)  # button press to start search
        el.button("Clear", self.search, '', 3, 1, tk.N, 1)  # button press to clear selection
        # el.check('Overwrite', self.overwrite, 4, 1)  # checkbox for overwrite option


        ## ROI generation
        self.er = Elements(self.fr_roi_gen)
        self.er.button('ROI Location',self.selectPath, 2, 3, 0, 'e', 1)  # Selection of ROI directory
        self.er.button('Update ROI List', self.roi_search,'', 4, 0, 'e', 1)  # Selection of ROI directory

        self.OptionList = ['Select a method' , 'Atlas based' , 'Peak Activation - Group' , 'Peak Activation - Individual', 'Group Differences' , 'Geometry Based']
        self.option_var = tk.StringVar(self.fr_roi_gen)
        self.option_var.set(self.OptionList[0])

        opt = tk.OptionMenu(self.fr_roi_gen, self.option_var, *self.OptionList)
        opt.config(width=20)
        opt.grid(row=0, column=0, sticky='w')

        self.option_var.trace('w', self.roi_gen)


    def roi_gen(self, *args):
        roif = roi_funcs(self.fr_roi_gen_child,self.roi_path, self.roi_search, self.roi_tree)
        roi_option = self.option_var.get()

        if roi_option == self.OptionList[1]:
            self.clear_frame(self.fr_roi_gen_child)
            roif.atlas_based()


        if roi_option == self.OptionList[2]:
            self.clear_frame(self.fr_roi_gen_child)
            roif.peak_group()

        if roi_option == self.OptionList[3]:
            self.clear_frame(self.fr_roi_gen_child)
            roif.peak_individual()

        if roi_option == self.OptionList[4]:
            self.clear_frame(self.fr_roi_gen_child)
            roif.group_differences()

        if roi_option == self.OptionList[5]:
            self.clear_frame(self.fr_roi_gen_child)
            roif.geometry_based()



        # method for calling directory picker

    def selectPath(self, var):
        self.root = Path(__file__).parent.absolute()

        if test_case == 1:
            self.roi_path = self.roi_tree.file_path = self.root/'test_data'/'PPI'
            self.file_path = self.root/'test_data'/'Subject'

        if test_case == 2:
            self.roi_path = self.roi_tree.file_path = '/home/quest/Desktop/aNMT_pre_withICAaroma/ManuscriptAnalyses/ROI/'
            self.file_path = '/home/quest/Desktop/aNMT_pre_withICAaroma/'
        else:
            path = appFuncs.selectPath()
            if var == 1:
                self.file_path = path
            else:
                self.roi_path = path
            self.stat.set('Selected Path: %s', path)
            # print(var)
            # self.file_path = var
        # self.result_tree.file_path = self.file_path


        # executed on clicking search button, this function lists all the datasets
    def roi_search(self):
        #  ROI Search
        r_list = Path(self.roi_path).glob(f'*.nii*')
        roi_list = []
        self.roi_tree.fileList = roi_list
        for j in r_list:
            roi_list.append([j, 100])
        self.roi_tree.file_path = self.roi_path
        self.roi_tree.display()
        self.roi_tree.fileList = roi_list

    def search(self):
        self.roi_search()
        ##############################
        self.result_tree.file_path = self.file_path
        search_str = self.search_str.get()
        search_str = search_str.split('-')
        search_inc = search_str[0]
        self.search_omit = ''
        if len(search_str) > 1: self.search_omit = search_str[1]


        identifier = f'*{search_inc}*.feat'
        if search_inc == '':identifier = f'*.feat'

        print(f'{search_inc} and {self.search_omit}')

        # Search for all files that match task
        search_list = Path(self.file_path).rglob(f'{identifier}')
        filtered_list = self.apply_omit(search_list)
        filtered_list = self.apply_filters(search_list)
        self.result_tree.fileList = self.aggregated_list(filtered_list)
        self.result_tree.display()  # display the results

    #  generates time course for each user in the list
    def generate_timecourse(self):

        roi = self.roi_tree.selection
        roi_name = self.roi_tree.selection_name

        cluster_name_unbin = roi_name + '_unbin_native.nii.gz'
        cluster_name_bin = roi_name + '_bin_native.nii.gz'
        timecourse_name = f'timecourse_{roi_name}.txt'
        command_list = []


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

            command_list.append([flirt, maths, meants])

        self.threader(command_list)
        print('Timecourses Generated!')

    #  Allows user to create a custom design profile which can then be applied to all datasets
    def generate_profile(self):
        # use a sample profile to load the basics and
        # call FSL from here and run the FEAT tool.
        command_list = []
        id = 1
        roi_name = self.roi_tree.selection_name
        for row in self.result_tree.fileList:
            subject = row[0]
            output_dir = subject / f'PPI_{roi_name}.feat'
            subject_dir = subject / 'filtered_func_data'
            subject_timecourse = subject / f'timecourse_{roi_name}.txt'

            if id == 1:
                sample_profile = self.root / 'sample_design.fsf'
                base_profile = self.root / 'temp' / 'temp_design.fsf'
                subprocess.run(['cp', sample_profile, base_profile])

                # read in the base profile
                files = [base_profile, output_dir, subject_dir, subject_timecourse]
                self.replace(files, 1)
                command = ['feat', base_profile]
                command_list.append([command])
                # Open Feat setup in FSL with this reference file
                subprocess.run(['Feat', base_profile])
                # reverse the subject specific paths
                self.replace(files, 2)

            subject_profile = self.root / 'temp' / f'temp_{id}.fsf'
            subprocess.run(['cp', base_profile, subject_profile])
            # read in and modify the subject profile
            files = [subject_profile, output_dir, subject_dir, subject_timecourse]
            self.replace(files, 1)
            command = ['feat', subject_profile]
            command_list.append([command])
            id += 1

        self.command_list_process = command_list
        # print(command_list)

    def process(self):
        self.threader(self.command_list_process)
        # empty the temp folder
        self.clear_dir(self.root/'temp')
        print('Processing completed!')

#####  Filtering results ########################################
    def apply_omit(self,file_list):
        filters = self.search_omit
        if len(filters) != 0:
            filters = filters
            fl = [row for row in file_list if ~any(f in str(row) for f in filters)]
        else:
            fl = file_list
        return fl

    def apply_filters(self,file_list):
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

################################################################
    @staticmethod
    def replace(files, type):
        profile = files[0]
        output_dir = files[1]
        subject_dir = files[2]
        subject_timecourse = files[3]

        fin = open(profile, "rt")
        data = fin.read()

        if type ==1:
            data = data.replace('#%#', str(output_dir))
            data = data.replace('#$#', str(subject_dir))
            data = data.replace('#!#', str(subject_timecourse))
        else:
            print(subject_dir)
            data = data.replace(str(output_dir), '#%#')
            data = data.replace(str(subject_dir), '#$#')
            data = data.replace(str(subject_timecourse), '#!#')
        fin.close()

        fin = open(profile, "wt")
        fin.write(data)
        fin.close()

    def clear_dir(self,dir_path):
        [Path.unlink(e) for e in dir_path.iterdir()]

    def clear_frame(self,frame):
        for widget in frame.winfo_children():
           widget.destroy()

    def threader(self,queue):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.process_commands, queue)

    def process_commands(self, command):
        for f in command:
            print(f)
            subprocess.run(f)

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

class roi_funcs:
    def __init__(self,master,roi_path, roi_search, roi_tree):
        self.master = master
        self.er = Elements(self.master)
        self.roi_path = roi_path
        self.roi_search = roi_search
        self.roi_tree = roi_tree

    def atlas_based(self):
        # Threshold
        self.thr_low = self.er.textField('Threshhold (low)',10,1,1)
        self.thr_high = self.er.textField('Threshhold (high)', 10, 3, 1)
        # Binarize button
        self.er.button('Binarize',self.binarize,'',1,2,'w',1)

        command = ['fsleyes','-std']
        # subprocess.run(command)



    def binarize(self):
        roi_path = self.roi_tree.file_path
        roi = self.roi_tree.selection_name
        output = roi+ '_bin'
        low = self.thr_low.get()
        high = self.thr_high.get()
        # threshold
        command = ['fslmaths',Path(roi_path)/roi]
        if low: command += ['-thr',low]
        if high:command += ['-uthr', high]
        if low or high:
            command += [Path(roi_path)/output]
            print(command)
            subprocess.run(command)
            input = output
        else:
            input = roi
        # Binarize
        command = ['fslmaths', Path(roi_path)/input, '-bin',Path(roi_path)/output]
        subprocess.run(command)

    def peak_group(self):
        self.er.button('Select image', self.cluster_select, '', 0, 1, 'w', 1)
        self.er.button('Extract', self.cluster_extract, '', 0, 2, 'w', 1)
        print('Peak Group')

    def peak_individual(self):
        print('Peak Individual')

    def group_differences(self):
        print('Group Differences')

    def geometry_based(self):
        # self.FSLDIR = os.environ['FSLDIR']
        self.FSLDIR = '/usr/local/fsl/'

        self.x_c = self.er.textField(f'x:', '3', 4, 1)
        self.y_c = self.er.textField(f'y:', '3', 7, 1)
        self.z_c = self.er.textField(f'z:', '3', 10, 1)
        self.roi_name = self.er.textField(f'ROI Name: ', '20', 15, 1)
        # Size of ROI
        self.roi_size = self.er.textField(f'Size (mm): ', '5', 12, 1)
        self.er.button('Generate ROI', self.geometry_process, '', 20, 1, 'w', 1)
        # self.er.button('Generate ROI', appFuncs.thread, (self.master, self.geometry_process,True), 20, 1, 'w', 1)

        # Standard image
        standard_search = Path(f'{self.FSLDIR}data/standard').glob('*.nii.gz')
        self.standard_list =[e.name for e in standard_search]
        self.standard_list.sort()
        self.image_var = tk.StringVar(self.master)

        self.std_image_options = self.er.popupMenu(self.image_var,self.standard_list,1,1,25,'w')
        self.image_var.set(self.standard_list[22])

        # Geometry options
        self.option_var =tk.StringVar(self.master)
        self.geometries = ['sphere','box','gauss']
        self.geometry_options = self.er.popupMenu(self.option_var,self.geometries,1,2,10,'w')
        self.option_var.set(self.geometries[0])

    def geometry_process(self):
        self.master.update_idletasks()
        point_name = Path(self.roi_path) / f'{str(self.roi_name.get())}_point.nii.gz'
        roi_name_unbin = Path(self.roi_path) / f'{self.roi_name.get()}_unbin.nii.gz'
        roi_name = Path(self.roi_path) / f'{self.roi_name.get()}.nii.gz'
        template = f'{self.FSLDIR}data/standard/{self.image_var.get()}'

        # Generate a point for the seed region
        command = ['fslmaths', template, '-mul', '0', '-add', '1', '-roi', str(self.x_c.get()), '1', str(self.y_c.get()), '1',
                   str(self.z_c.get()), '1', '0', '1', str(point_name), '-odt', 'float']
        subprocess.run(command)
        # Generate an ROI around the point
        command = ['fslmaths', point_name, '-kernel', self.option_var.get(), str(self.roi_size.get()), '-fmean', roi_name_unbin,  '-odt', 'float']
        subprocess.run(command)
        # Binarize the ROI mask
        command = ['fslmaths', roi_name_unbin, '-bin', roi_name]
        subprocess.run(command)
        # Delete point and non-binarized files
        Path(point_name).unlink()
        Path(roi_name_unbin).unlink()

        self.roi_search()

    def cluster_select(self):
        self.var = appFuncs.select_file('Select image file')
        self.cluster_num()
        self.cluster = self.er.textField(f'Cluster Number (0-{self.cluster_indexes[0]})', '10', 1, 1)

    def cluster_extract(self):
        cluster = str(self.cluster.get())
        mask_name = Path(self.roi_path)/f'extracted_cluster_{cluster}.nii.gz'
        command = ['fslmaths','-dt','int', self.var, '-thr', cluster, '-uthr', cluster, '-bin', mask_name]
        subprocess.run(command)
        print('Extraction complete!')

    def cluster_num(self):
        self.cluster_indexes =[]
        file_dir = Path(self.var).parent
        file_name = Path(Path(self.var).stem).stem

        file_name = str(file_name)
        m = re.search('zstat(.+?)', file_name)
        if m:
            name = Path(file_dir)/f'cluster_zstat{m.group(1)}_std.txt'
            print(str(name))
            if Path(name).is_file():
                # read and extract data
                with open(name) as f:
                    i = 0
                    for line in f:
                        if i == 0:
                            break
                    data = [r.split() for r in f]
                    for r in data:
                        print(f'{r[0]}     {r[1]}')
                        self.cluster_indexes.append(r[0])
                f.close()

    def blank(self):
        pass


class appFuncs:
    @staticmethod
    def thread(*args):
        n=0
        for i in args:
            if n==0:
               self = i
            if n==1:
                command = i
            if n==2:
                is_daemon = i
            n+=1
        # self.update_idletasks()
        x = threading.Thread(target=subprocess.run, args=(command))
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