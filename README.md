CURATION TOOL

The purpose of this tool is :

-extract insights from the database of images for all ML tasks
-follow the curation guides defined for all ML tasks
-identify and cluster image duplicates and similar images from a dataset
-reduce the curation time taken by a human for each data collection

How to use:
1. Mount to Kiwi Data Storage in order to access data on your local machine
Open Terminal and enter 
sudo apt-get update
sudo apt-get upgrade
sudo apt install nfs-common
sudo mkdir /mnt/kiwi_transfer && sudo mount -t nfs -o vers=3 172.20.6.68:/mnt/KiwiPool/KiwiData/old/kiwi_transfer /mnt/KiwiFTP/kiwi_transfer

2. Download the Curation Tool file

3. Running Curation Tool
(Ensure you have python3 installed on your system. Steps to install python3  https://docs.python-guide.org/starting/install3/linux/)

Open Terminal & enter

/usr/bin/python3 {path to where Curation Tool is saved/CurationTool.py}

e.g. ( /usr/bin/python3 /home/ksaygbe/Documents/CurationTool/src/CurationTool.py )

4. Browse to specified directory
mnt → KiwiFTP → kiwi_transfer → rawImageData → KETR_Number → SPECIFIED FOLDER 
(Browse only displays directories so ensure you are located in the correct specified folder and press OK)

5. Allow pre-curation processes to run.
Pre-Curation Blur Detection (First Process). Identifies images that are blurry and moves them to the Bad Images → Blurred Images directory in the active directory.
Pre-Curation Duplicate Detection (Second Process). Identifies images that are similar and moves them to the Bad Images → Duplicate Images directory in the active directory. 
(Curation Tool will remain blank until pre-process is complete. Pre-process duration depends on the amount of images being analyzed. Pre-process tests took 5 minutes per 1000 images)

6. CURATE AWAY.
“Good” → Sends to Curated_Images Directory in Good_Images (Curated_Images is the destined folder  to be uploaded for annotation)
“Bad .etc” → sends to Bad_Images Directory

Additional Notes:
- Keep terminal open while curating, its the ENGINE
- Curation Tool tracks your progress and skips the pre-process if it has already been ran. Just reload folder in case you need to pick up where you left off
