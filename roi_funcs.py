## Functions for ROI generation related tasks

import tkinter as tk
import functions as fn
from pathlib import Path
import subprocess, os, re
import numpy as np


class roif:
    def __init__(self,master,roi_path, roi_search, roi_tree, roi_name):
        self.master = master
        self.er = fn.Elements(self.master)
        self.roi_path = roi_path
        self.roi_search = roi_search
        self.roi_tree = roi_tree
        self.roi_name = roi_name

    def atlas_based(self):
        # Threshold
        self.thr_low = self.er.textField('Threshhold (low)',10,1,1)
        self.thr_high = self.er.textField('Threshhold (high)', 10, 3, 1)
        # Binarize button
        self.er.button('Binarize', self.threshold, '', 1, 2, 'w', 1)
        # Localize button
        self.er.button('Localize', self.localize, '', 1, 3, 'w', 1)

        command = ['fsleyes','-std']
        # subprocess.run(command)

    def threshold(self):
        roi_path = self.roi_tree.file_path
        roi = self.roi_tree.selection_name
        self.roi = roi
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
        self.binarize(Path(roi_path)/input, Path(roi_path)/output)

    def binarize(self, image_in, image_out):
        command = ['fslmaths', image_in, '-bin',image_out]
        subprocess.run(command)

    def localize(self):
        roi = self.roi_tree.selection
        # generate temporary binarized version of anatomical cluster
        anatomical_cluster = fn.appFuncs.select_file('Select Anatomical Cluster')
        anatomical_cluster_bin = Path(anatomical_cluster).parent/f'bin_{Path(anatomical_cluster).name}'
        self.binarize(anatomical_cluster, anatomical_cluster_bin)
        # naming of new ROI
        new_roi_name = self.roi_name.get()
        if new_roi_name == '':
            new_roi_name = f'{self.roi_tree.selection_name}_{Path(Path(anatomical_cluster).stem).stem}'

        # actual localization
        roi_localized = Path(roi).parent/new_roi_name
        command = ['fslmaths',roi,'-mul',anatomical_cluster_bin,roi_localized]
        subprocess.run(command)

        # delete binarized mask file
        Path(anatomical_cluster_bin).unlink()


    def group(self):
        self.er.button('Select image', self.cluster_select, '', 0, 1, 'w', 1)
        self.er.button('Extract', self.cluster_extract, '', 0, 2, 'w', 1)
        print('Peak Group')

    def cluster_select(self):
        self.var = fn.appFuncs.select_file('Select image file')
        self.cluster_num()
        self.cluster = self.er.textField(f'Cluster Number (1-{self.cluster_indexes[0]})', '10', 1, 1)

    def cluster_num(self):
        self.cluster_indexes = []
        self.cluster_mni =[]
        file_dir = Path(self.var).parent
        file_name = Path(Path(self.var).stem).stem

        file_name = str(file_name)
        m = re.search('zstat(.+?)', file_name)
        if m:
            name = Path(file_dir) / f'cluster_zstat{m.group(1)}_std.txt'
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
                        mni = [int(i) for i in r[5:8]]
                        self.cluster_indexes.append(r[0])
                        self.cluster_mni.append(mni)
                        print(f'{r[0]}     {r[1]}   MNI :  {mni}')
                f.close()

    def cluster_extract(self):
        cluster = str(self.cluster.get())
        mask_name = Path(self.roi_path) / f'{str(self.roi_name.get())}_{cluster}.nii.gz'
        command = ['fslmaths', '-dt', 'int', self.var, '-thr', cluster, '-uthr', cluster, '-bin', mask_name]
        subprocess.run(command)
        print('Extraction complete!')

    def geometry_based(self):
        self.FSLDIR = os.environ['FSLDIR']

        self.x_c = self.er.textField(f'x:', '3', 4, 1)
        self.y_c = self.er.textField(f'y:', '3', 7, 1)
        self.z_c = self.er.textField(f'z:', '3', 10, 1)
        # self.roi_name = self.er.textField(f'ROI Name: ', '20', 15, 1)
        # Size of ROI
        self.roi_size = self.er.textField(f'Size (mm): ', '5', 12, 1)
        self.er.button('Generate ROI', self.geometry_process, '', 20, 1, 'w', 1)
        # self.er.button('Generate ROI', fn.appFuncs.thread, (self.master, self.geometry_process,True), 20, 1, 'w', 1)

        # Standard image
        standard_search = Path(f'{self.FSLDIR}data/standard').glob('*.nii.gz')
        self.standard_list =[e.name for e in standard_search]
        self.standard_list.sort()
        self.image_var = tk.StringVar(self.master)

        self.std_image_options = self.er.popupMenu(self.image_var, self.standard_list, 1, 1, 25, 'w')
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

    def peak_individual(self):
        print('Peak Individual')

    @staticmethod
    def mni_2_voxel(inp):
        origin = np.array([45, 63, 36])
        transf = np.array([-1, 1, 1])
        mni = np.array(inp)
        vox = np.round(origin + mni*transf/2)
        return vox

    def blank(self):
        pass