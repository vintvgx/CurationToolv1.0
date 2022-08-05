#Code by Raajitha Gummadi

import os
import csv
from tqdm import tqdm
import numpy as np
import shutil
import glob
from PIL import Image
import detect_bluriness

from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.preprocessing.image import img_to_array

dupli_images = "Filtering_result/duplicate_images"
image_path = "Filtering_result/sample_images"
verbose=1
ext = ['.jpg', '.jpeg', '.jfif', '.pjpeg', '.pjp', '.png', '.svg', '.webp', '.avif', '.apng'] 

model = ResNet50(
    weights='imagenet',
    include_top=False,
    pooling="avg",
    input_shape=(50, 50, 3),
)

# generates embeddings for images
def generate_embeddings(input_pil_image):
    resized_image = input_pil_image.resize((50, 50))
    x = img_to_array(resized_image)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    
    embeddings = model.predict(x).flatten().tolist()
    return embeddings

def duplicate_image_removal(path):
    global image_path
    global dupli_images
    image_path = os.path.join(path, image_path)

    images = sorted(glob.glob(f'{image_path}/*{ext}'))
    dupli_images = os.path.join(path, dupli_images)

    os.makedirs(dupli_images, exist_ok=True)

    embeddings = []
    unique_images = []
    duplicates = []
    ctr = 0
    total_num_of_images = len(images)
    print("PROCESSING ", total_num_of_images ," IMAGES & DISCARDING DUPLICATE IMAGES: ")
    for image in tqdm(images):
        current_image = os.path.join(image_path, image)
        im = Image.open(current_image).convert('RGB')
        embedding = generate_embeddings(im)
        ctr = ctr + 1
        if embeddings == []:
            embeddings.append(embedding)
            unique_images.append(current_image)
        else:
            List1 = np.array(embeddings)
            similarity_scores = List1.dot(embedding)/ (np.linalg.norm(List1, axis=1) * np.linalg.norm(embedding))
            max_similarity_idx = np.argmax(similarity_scores)
            # print (ctr, "out of", total_num_of_images, "=", similarity_scores[max_similarity_idx])
            if similarity_scores[max_similarity_idx] > 0.97:
                try:
                    duplicates.append(current_image)
                    shutil.move(current_image, dupli_images)
                except:
                    pass
            else:
                embeddings.append(embedding)
                unique_images.append(current_image)
            
            
                
    print("found ", len(unique_images), "unique images")
    print("found ", len(duplicates), " duplicate images")

    with open(os.path.join(path, 'Filtering_result/unique_images.csv'), 'w+', newline ='') as file:    
        write = csv.writer(file)
        for item in unique_images:
            write.writerow([item])

    with open(os.path.join(path,'Filtering_result/duplicates.csv'), 'w+', newline ='') as file:    
        write = csv.writer(file)
        for item in duplicates:
            write.writerow([item])



'''
Proper csv export unfixed code

unique_path = path + '/Filtering_result/unique_images.csv'
    dupli_path = path + '/Filtering_result/duplicates.csv'

    headerList = ['Original File Path', 'Status']
    with open(unique_path, 'w+', newline ='') as file:    
        dw = csv.DictWriter(file, delimiter=',', fieldnames=headerList)
        dw.writeheader()
        
        df_unique_files= pd.read_csv(unique_path)
        for item in unique_images:
            df_unique_files = df_unique_files.append(dict(zip(df_unique_files.columns,[item, "unique"])), ignore_index=True)
            df_unique_files.to_csv(unique_path, index=False)

    with open(dupli_path, 'w+', newline ='') as file:
        dw = csv.DictWriter(file, delimiter=',', fieldnames=headerList)
        dw.writeheader()
        
        df_dupli_files= pd.read_csv(dupli_path)    
        for item in dupli_images:
            df_dupli_files = df_dupli_files.append(dict(zip(df_dupli_files.columns,[item, "unique"])), ignore_index=True)
            df_dupli_files.to_csv(dupli_path, index=False)

duplicate_image_removal('/home/ksaygbe/Pictures/example_470')

'''