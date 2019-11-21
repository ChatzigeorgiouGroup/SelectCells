#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 09:40:41 2019

@author: daniel
"""
import tifffile
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
from skimage import filters
from skimage import exposure

class Main:
    def __init__(self, path = "./"):
        
        self.current_image = 0
        self.path = path
        
        self.result_dir = os.path.join(self.path, "cell_locations")
        if not os.path.exists(self.result_dir):
            os.mkdir(self.result_dir)
        
        
        self.images = self.get_images(self.path)
        self.select_cells()
        

    def get_images(self, path = "./"):
        present_results = os.listdir(self.result_dir)
        data = glob.glob(os.path.join(path, "**/**.tif"), recursive = True)
        data = [x for x in data if os.path.split(x)[-1].rstrip(".tif") not in present_results]
        return data
    
    def load_image(self):
        path = self.images[self.current_image]
        self.savedir = os.path.join(self.result_dir, os.path.split(path)[-1].rstrip(".tif"))
        print(f"Loading image {os.path.split(path)[-1]}")
        img = tifffile.imread(path).T
        img = np.max(img[0], axis = 0)
        return img
        
    def next_image(self, step = 1):
        self.current_image += step
        self.select_cells()
        
    def select_cells(self):
        self.image = self.load_image()
        self.clicker = Clicker(self, self.image)
        
    def save_results(self, locations, fig):
        if not os.path.exists(self.savedir):
            os.mkdir(self.savedir)
        fig.savefig(os.path.join(self.savedir, "locations.png"))
        locations = np.vstack(locations)
        np.save(os.path.join(self.savedir, "locations.npy"), locations)
        print(f"saved results to {self.savedir}")

class Clicker:
    def __init__(self, parent, image):     
        self.fig, self.ax = plt.subplots(figsize = (8,8))
        self.original = image
        self.image = image
        self.parent = parent
        self.image_canvas = self.ax.imshow(self.image, cmap = "gray")
        self.fig.canvas.mpl_connect("button_press_event", self.mouseclick)
        self.fig.canvas.mpl_connect("key_press_event", self.keypress)
        self.locations = {}
        self.cell_number = 1
        self.ax.set_title(f"Next Cell Number: {self.cell_number}")
        plt.show()
        
    def mouseclick(self, event):
        if event.xdata:
            x = int(event.xdata)
            y = int(event.ydata)
            if event.button == 1:
                self.locations[self.cell_number] = np.array([x,y])
                self.cell_number += 1
           
            elif event.button == 3:
                cursor = np.array([x,y])
                for loc in self.locations.keys():
                    if np.linalg.norm(self.locations[loc] - cursor) < 5:
                        self.locations.pop(loc)
                        break
                
            self.draw_circle_artists()
            self.ax.set_title(f"Next Cell Number: {self.cell_number}")
            self.image_canvas.autoscale()
            self.fig.canvas.draw()
            self.remove_circle_artists()
    
    def update(self):
        self.image_canvas.set_array(self.image)
        self.image_canvas.autoscale()
        self.draw_circle_artists()
        self.ax.set_title(f"Next Cell Number: {self.cell_number}")
        self.fig.canvas.draw()
        self.remove_circle_artists()
        
    def draw_circle_artists(self, color = "r", fill = False):
        self.artists = []
        for loc in self.locations.keys():
            circle = plt.Circle(self.locations[loc], 5, edgecolor = color, facecolor = None, fill = fill)
            x, y = self.locations[loc]
            text = plt.text(x+10, y, s = str(loc), color = color)
            self.artists.append(circle)
            self.artists.append(text)
            self.ax.add_artist(circle)  
            
    def remove_circle_artists(self):
        for artist in self.artists:
            artist.remove()
            
    def keypress(self, event):
        if event.key == "right":
            plt.close(self.fig)
            self.parent.next_image(step = 1)
        if event.key == "left":
            plt.close(self.fig)
            self.parent.next_image(step = -1)
        if event.key == "r":
            self.locations = {}
            self.image = self.original
            self.update()
        if event.key == "1":
            self.image = filters.gaussian(self.image, sigma = 1)
            self.update()
        if event.key == "2":
            self.image = exposure.adjust_gamma(self.image, gamma = 0.9)
            self.update()
        if event.key == "3":
            self.image = exposure.adjust_gamma(self.image, gamma = 1.1)
            self.update()
        if event.key == "enter":
            self.draw_circle_artists(color = "cyan", fill = True)
            self.parent.save_results(self.locations, self.fig)
            self.remove_circle_artists()
        if event.key == "+":
            self.cell_number += 1
            self.update()
        if event.key == "-":
            self.cell_number -= 1
            self.update()

if __name__ == "__main__":
   m = Main()

