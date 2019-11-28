#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 10:08:59 2019

@author: daniel
"""

import matplotlib.pyplot as plt
import numpy as np
from skimage import filters, exposure
from skimage.measure import find_contours

class CellSelector:
    def __init__(self, parent, image, *args, **kwargs):     
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
            self.cell_number = 1
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
            
class ContourFinder:
    def __init__(self, parent, image, *args, **kwargs):
        self.fig, self.ax = plt.subplots()
        self.original = image
        self.image = image
        self.parent = parent
        self.image_canvas = self.ax.imshow(self.image, cmap = "gray")
        self.fig.canvas.mpl_connect("button_press_event", self.mouseclick)
        self.fig.canvas.mpl_connect("key_press_event", self.keypress)
        self.skeleton = {}
        self.contours = {}
        self.selected_contours = []
        self.closest_ind = -1
        plt.show()
    
    def keypress(self, event):
        if event.key == "right":
            plt.close(self.fig)
            self.parent.next_image(step = 1)
        if event.key == "left":
            plt.close(self.fig)
            self.parent.next_image(step = -1)
        if event.key == "r":
            self.image = self.original
            self.contours = {}
            self.update()
        if event.key == "c":
            self.find_contours()
            self.update()
        if event.key == "t":
            self.image = self.image > filters.threshold_li(self.image)
            self.update()
        if event.key == "1":
            self.image = filters.gaussian(self.image, sigma = 10)
            self.update()
        if event.key == "2":
            self.image = exposure.adjust_gamma(self.image, gamma = 0.2)
            self.update()
        if event.key == "3":
            self.image = exposure.adjust_gamma(self.image, gamma = 1.5)
            self.update()
#        if event.key == "enter":
#            self.parent.save_results(self.contours, self.fig)
#    
    def mouseclick(self, event):
        if event.xdata:
            x = int(event.xdata)
            y = int(event.ydata)
            dists = []
            if len(self.contours.keys()) > 0:
                for loc in self.contours.keys():
                    dists.append(np.linalg.norm(self.contours[loc] - np.array([y,x]), axis = 1).min())
                self.closest_ind = np.argmin(dists)
            if event.button == 1:
                self.selected_contours.append(self.closest_ind)
            if event.button == 3:
                if self.closest_ind in self.selected_contours:
                    self.selected_contours.remove(self.closest_ind)
            self.update()
                    
                    
    def update(self):
        self.ax.clear()
        self.image_canvas = self.ax.imshow(self.image, cmap = "gray")
        self.draw_contours()
        if self.closest_ind != -1:
            self.ax.set_title(f"Selected Skeleton: {self.closest_ind}")
        self.fig.canvas.draw()
  
    def find_contours(self, level = 0.8):
#        imt = self.image > filters.threshold_li(self.image)
#        image = exposure.adjust_gamma(self.image, 0.2)
#        image = filters.gaussian(image, 10)
        image = self.image > filters.threshold_li(self.image)
        contours = find_contours(image, 0.8)
        for i, c in enumerate(contours):
            self.contours[i] = c
        
    def draw_contours(self):
        for loc in self.contours.keys():
            if loc in self.selected_contours:
                ls = "solid"
                alpha = .9
            else:
                ls = "dotted"
                alpha = .6
            contour = self.contours[loc]
            self.ax.plot(contour[:,1], contour[:,0], label = loc, alpha = alpha, ls = ls)
        self.ax.legend()           