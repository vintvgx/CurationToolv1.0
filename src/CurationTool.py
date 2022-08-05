#!/usr/bin/python3
import glob
from wsgiref.validate import WriteWrapper
import PySimpleGUI as sg
import shutil
import os
import csv
import pandas as pd

from cv2 import blur
import detect_duplicates 
import numpy as np
import time
from datetime import datetime

from PIL import Image, ImageTk

sg.theme('DarkGrey13')

good_destination = "Filtering_result/sample_images"
bad_destination = "Curation_result/Bad_images"
curated_destination = "Curation_result/Good_images"
good_directory = ""
bad_directory = ""
ext = ['.jpg', '.jpeg', '.jfif', '.pjpeg', '.pjp', '.png', '.svg', '.webp', '.avif', '.apng'] 
pre_curate_done = False


 
def pre_curation(path):
    blur_dir = os.path.join(path, 'Bad_images/blur_images')
    dupli_dir = os.path.join(path, 'Filtering_result/blur_images')

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
    images_to_be_curated = sorted(glob.glob(f'{good_directory}/*{ext}'))

    os.makedirs(curated_destination, exist_ok=True)
    os.makedirs(good_directory, exist_ok=True)
    os.makedirs(bad_directory, exist_ok=True)
    previously_curated_images = sorted(glob.glob(f'{curated_destination}/*{ext}')) + sorted(glob.glob(f'{bad_directory}/*{ext}'))

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
    header = ['File Name', 'Status', 'Time']
    with open(os.path.join(path, 'curated_Good_Images.csv'), 'w+', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for item in values:
            writer.writerow([item])


def save_to_bad_csv(path, values):
    header = ['File Name', 'Status', 'Time']
    with open(os.path.join(path, 'curated_Bad_Images.csv'), 'w+', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for item in values:
            writer.writerow([item])        

def create_csv(path):
    now = datetime.now()
    time_stamp = now.strftime("%d%m%Y")

    curated_path = path + '/Curation_result/curated'+ time_stamp + '.csv'
    # curate_files.to_csv(curated_path, index=False) #creates csv
    headerList = ['Original File Path', 'Good_Or_Bad', 'Curated Path', 'Time Stamp']
    with open(curated_path, 'w') as file:
        dw = csv.DictWriter(file, delimiter=',', fieldnames=headerList)
        dw.writeheader()
    
    return curated_path

def save_csv(curated_path, location, image, image_value, destination, time_stamp):
    
    df_curate_files= pd.read_csv(curated_path) # loads csv into pd
    df_curate_files = df_curate_files.append(dict(zip(df_curate_files.columns,[image, image_value, destination, time_stamp])), ignore_index=True)                                                                           
    # df_curate_files.loc[location, 'Original File Path'] = image
    # df_curate_files.loc[location, 'Good_Or_Bad'] = image_value
    # df_curate_files.loc[location, 'Curated Path'] = destination
    # # df_curate_files.loc[df_curate_files['Good_or_Bad'].notnull() & df_curate_files['Timestamp'].isnull(), 'Timestamp'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    # df_curate_files.loc[location, 'Time Stamp'] = time_stamp
    # ({image, image_value, destination, time_stamp})

    df_curate_files.to_csv(curated_path, index=False)

def update_window(window, location, images):
    #updates elements in window
    try:
        window['-START-'].update(location)
        window['-END-'].update(len(images))
        window['-TITLE-'].update(images[location])
    except:
        sg.popup("Folder has been curated!")


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
            print(values["file"])
            images = []
            good_images = []
            bad_images = []
            location = 0
            pre_curation(values["file"])
            images = parse_folder(values["file"])
            curated_path = create_csv(values["file"])
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
                    good_images.append(images[location] + " , " + image_value + " , " + time_stamp)
                    location += 1
                    load_image(images[location], window)
                    save_csv(curated_path, location, images[location], image_value, curated_destination, time_stamp)
                else:
                    copy_image(images[location], bad_directory)
                    location += 1
                    load_image(images[location], window)
                    bad_images.append(images[location] + " , " +  image_value + " , " +  time_stamp)
                    save_csv(curated_path, location, images[location], image_value, bad_directory, time_stamp)
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