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

dupli_images = "Bad_images/duplicate_images"
image_path = "Good_images"
verbose=1

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

    images = sorted(glob.glob(f'{image_path}/*.png'))
    dupli_images = os.path.join(path, dupli_images)

    if os.path.isdir(dupli_images) == False:
        os.mkdir(dupli_images)
    else:
        pass

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
            
            
                
    print("found ", len(unique_images), " unique images")
    print("found ", len(duplicates), " duplicate images")

    with open(os.path.join(path, 'unique_images.csv'), 'w+', newline ='') as file:    
        write = csv.writer(file)
        write.writerows(unique_images)

    with open(os.path.join(path,'duplicates.csv'), 'w+', newline ='') as file:    
        write = csv.writer(file)
        write.writerows(duplicates)

