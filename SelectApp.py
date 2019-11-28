#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 09:40:41 2019

@author: daniel
"""
import tifffile
import numpy as np
import glob
import os
import pandas as pd
from SelectionTools import CellSelector, ContourFinder

class SelectApp:
    def __init__(self, path = "./"):
        
        self.current_image = 0
        self.path = path
        
        self.result_dir = os.path.join(self.path, "cell_locations")
        self.images = self.get_images(self.path)
        if len(self.images)>0:
            print(f"Found {len(self.images)} to annotate\n")
            self.state = input("Select NotochordCells [n] or Contours [c]: ")
            if self.state.lower() == "n":
                self.state = 0
                self.f = CellSelector
            elif self.state.lower() == "c":
                self.state = 1
                self.f = ContourFinder
            else:
                print("invalid option specified.")
            self.select_cells()
        else:
            print("\nNo valid files in path")
        

    def get_images(self, path = "./"):
        data = glob.glob(os.path.join(path, "**/**.tif"), recursive = True)
        if os.path.exists(self.result_dir):
            present_results = os.listdir(self.result_dir)
            data = [x for x in data if os.path.split(x)[-1].rstrip(".tif") not in present_results]
        return data
    
    def load_image(self):
        path = self.images[self.current_image]
        self.savedir = os.path.join(self.result_dir, os.path.split(path)[-1].rstrip(".tif"))
        print(f"Loading image {os.path.split(path)[-1]}")
        img = tifffile.imread(path).T
        img = np.max(img[self.state], axis = 0)
        return img
        
    def next_image(self, step = 1):
        self.current_image += step
        self.select_cells()
        
    def select_cells(self):
        self.image = self.load_image()
        self.clicker = self.f(self, self.image)
        
    def save_results(self, locations, fig):
        if not os.path.exists(self.result_dir):
            os.mkdir(self.result_dir)       
        if not os.path.exists(self.savedir):
            os.mkdir(self.savedir)
        fig.savefig(os.path.join(self.savedir, "locations.png"))
        df = pd.DataFrame.from_dict(locations, columns = ["x", "y"], orient = "index")
        df.to_csv(os.path.join(self.savedir, "locations.txt"), sep = "\t")
        print(f"saved results to {self.savedir}")



if __name__ == "__main__":
#    path = input("Path to tiffs:")
    path = "/home/daniel/Documents/Projects/Skeletonizing_Notochord/"
    app = SelectApp(path)

