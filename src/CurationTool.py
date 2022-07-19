#!/usr/bin/python3

import glob
import PySimpleGUI as sg
import shutil
import os
import csv

from cv2 import blur
import detect_duplicates 
import numpy as np
import time
from datetime import datetime

from PIL import Image, ImageTk

sg.theme('DarkGrey13')

good_destination = "Good_images"
bad_destination = "Bad_images"
curated_destination = "Good_images/Curated_Images"
good_directory = ""
bad_directory = ""
pre_curate_done = False


 
def pre_curation(path):
    blur_dir = os.path.join(path, 'Bad_images/blur_images')
    dupli_dir = os.path.join(path, 'Bad_images/duplicate_images')

    if os.path.isdir(blur_dir) == True or os.path.isdir(dupli_dir) == True:
        pass
    else:     
        detect_duplicates.detect_bluriness.detect_blur(path)
        detect_duplicates.duplicate_image_removal(path)
            

def parse_folder(path):
    global good_directory
    global bad_directory
    global curated_destination
    # images = sorted(glob.glob(f'{path}/*.jpg') + glob.glob(f'{path}/*.png'))
    # filtered_images = []
    good_directory = os.path.join(path, good_destination)
    bad_directory = os.path.join(path, bad_destination)
    curated_destination = os.path.join(path, curated_destination)
    images_to_be_curated = sorted(glob.glob(f'{good_directory}/*.jpg') + glob.glob(f'{good_directory}/*.png'))

    os.makedirs(curated_destination, exist_ok=True)
    os.makedirs(good_directory, exist_ok=True)
    os.makedirs(bad_directory, exist_ok=True)
    previously_curated_images = sorted(glob.glob(f'{curated_destination}/*.png')) + sorted(glob.glob(f'{bad_directory}/*.png'))

    # checks the curated folder and returns only the images that have not
    # yet been curated 
    for img in images_to_be_curated[:]:
        for element in previously_curated_images:
            try:
                if img[-10:] == element[-10:]:
                    images_to_be_curated.remove(img)
                else:
                    pass
            except:
                pass

    if images_to_be_curated == 0:
        sg.popup("This Folder Has Already Been Curated!")
    else:
        return images_to_be_curated


    
    

def load_image(path, window):
    try:
        #loads image into window, opens up pop up if image can not be open
        image = Image.open(path)
        image.thumbnail((1200, 1200))
        photo_img = ImageTk.PhotoImage(image)
        window["image"].update(data=photo_img)
    except:
        print(f"Unable to open {path}!")
        sg.popup("Unable to open image!")
        
def copy_image(img, dest):
    try:
        #take copy of image and put it in destination
        shutil.copy(img, dest)
    except:
        print(f"Unable to copy image!")
                
def save_to_good_csv(path, values):
    with open(os.path.join(path, 'curated_Good_Images.csv'), 'w+', newline='') as file:
        write = csv.writer(file)
        write.writerows(values)

def save_to_bad_csv(path, values):
    with open(os.path.join(path, 'curated_Bad_Images.csv'), 'w+', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(values)         

def update_window(window, location, images):
    #updates elements in window
    try:
        window['-START-'].update(location)
        window['-END-'].update(len(images))
        window['-TITLE-'].update(images[location])
    except:
        sg.popup("Folder has been curated!")

# def progress_bar():
#     # set len(mylist) to length of current images
#     progressbar = [
#     [sg.ProgressBar(len(mylist), orientation='h', size=(51, 10), key='progressbar')]
#     ]
    
#     layout = [
#         [sg.Frame('Progress',layout= progressbar)]
#     ]

def main():
    

    
    options_selection_column = [

        [sg.Text("Choose option")],
        [    
            sg.Radio('Good', "-OPTION-", key="-GOOD-", enable_events=True),
        ],
        [
            sg.Radio('Bad - Excessive Motion Blur',  "-OPTION-", enable_events=True, key="-Bad-Excessive Motion Blur-")
        ],
        [
            sg.Radio('Bad - Unpopulated', "-OPTION-", key="Bad - Unpopulated", enable_events=True)
        ],
        [
            sg.Radio('Bad - Occulation',  "-OPTION-", key="Bad - Occulation", enable_events=True)
        ],
        [
            sg.Radio('Bad - Duplicate',  "-OPTION-", key="Bad - Duplicate", enable_events=True)
        ],
        [
            sg.Radio('Bad - Other', "-OPTION-", key="Bad - Other", enable_events=True)
        ],
        [
            sg.Button('Submit')
        ]
    ]

    elements = [
        [sg.Image(key="image")],
        [
            sg.Text("Image Folder"),
            sg.Input(size=(25, 1), enable_events=True, key="file"),
            sg.FolderBrowse(),
        ],
        [
            sg.Button("Prev"),
            sg.Button("Next")
        ],
        [
            sg.Text("0", key="-START-"), sg.Text("out of"),
            sg.Text("0", key="-END-"),
        ],
        [
            sg.Text("", key="-TITLE-" )
        ]
        
    ]

    layout = [
        [
            sg.Column(elements, expand_x=True, expand_y=True),
            sg.VSeparator(),
            sg.Column(options_selection_column, expand_x=True, expand_y=True)
        ]
    ]

    window = sg.Window("Curation Tool", layout, resizable=True, location=(600,400))
    images = []
    good_images = []
    bad_images = []
    location = 0
    image_value = ''
    now = datetime.now()
    time_stamp = now.strftime("%d/%m/%Y %H:%M:%S")
 


    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "file":
            pre_curation(values["file"])
            images = parse_folder(values["file"])
            if images:
                load_image(images[0], window)
            update_window(window, location, images)
        elif event == "Next" and images:
            if location == len(images) - 1:
                location = 0
            else:
                location += 1
            load_image(images[location], window)
            update_window(window, location, images)
        elif event == "Prev" and images:
            if location == 0:
                location = len(images) - 1
            else:
                location -= 1
            load_image(images[location], window)
            update_window(window, location, images)
        # takes the input from the Radio chosen and saves value to image value to be passed on to csv file
        elif event == "-Bad-Excessive Motion Blur-":
            image_value = event
        elif event == "Bad - Unpopulated":
            image_value = event
        elif event == "Bad - Occulation":
            image_value = event
        elif event == "Bad - Duplicate":
            image_value = event
        elif event == "Bad - Other":
            image_value = event
        elif event == "-GOOD":
            image_value = event
        # copies current image into bad or good dest folder & increments to next photo & saves to proceeding csv file
        elif event == "Submit":
            try:
                if values["-GOOD-"] == True:
                    copy_image(images[location], curated_destination)
                    image_value = "Good"
                    good_images.append(images[location] + image_value + time_stamp)
                    location += 1
                    load_image(images[location], window)
                    save_to_good_csv(curated_destination, good_images)
                else:
                    copy_image(images[location], bad_directory)
                    location += 1
                    load_image(images[location], window)
                    bad_images.append(images[location] + image_value + time_stamp)
                    save_to_bad_csv(bad_directory, bad_images)
            except IndexError:
                sg.popup("Folder has been curated!")
            try:
                update_window(window, location, images)
                print(images[location], image_value)
            except:
                pass
        
    window.close()


if __name__ == "__main__":
    main()