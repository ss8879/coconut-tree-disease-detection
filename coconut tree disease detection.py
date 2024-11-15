import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import cv2
from glob import glob
from tqdm import tqdm
import xml.etree.ElementTree as ET

pip install ultralytics

!pip install roboflow

from roboflow import Roboflow
rf = Roboflow(api_key="pjZtbsAzjhkBsKvruel1")
project = rf.workspace("mayhoc").project("coconut-tree-disease")
version = project.version(8)
dataset = version.download("yolov8")

data_path = "/content/coconut-tree-disease-8"
image_files = glob(os.path.join(data_path, "train", "images", "*.jpg"))
label_files = glob(os.path.join(data_path, "train", "labels", "*.txt"))
print(f"Number of images: {len(image_files)}")
print(f"Number of label files: {len(label_files)}")

import glob
from IPython.display import Image, display

for image_path in glob.glob(f'/content/coconut-tree-disease-8/train/images/*.jpg')[:3]:
      display(Image(filename=image_path, width=600))
      print("\n")

import yaml
with open("/content/coconut-tree-disease-8/data.yaml") as stream:
    try:
        print(yaml.safe_load(stream))
    except yaml.YAMLError as exc:
        print(exc)

def preprocess_image(image_path, target_size=(640, 640)):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, target_size)
    image = image / 255.0
    return image
preprocessed_images = [preprocess_image(img_path) for img_path in image_files[:10]]

from ultralytics import YOLO
import os
from IPython.display import display, Image
from IPython import display
display.clear_output()
!yolo mode=checks

!pip install roboflow

import os
os.environ["DATASET_DIRECTORY"] = "/content/datasets"

from roboflow import Roboflow
rf = Roboflow(api_key="eSzt9jqUwL3SzdHp0dmr")
project = rf.workspace("mayhoc").project("coconut-tree-disease")
version = project.version(1)
dataset = version.download("yolov8")

!yolo task=detect mode=train model=yolov8n.pt data={dataset.location}/data.yaml epochs=150 imgsz=340

from IPython.display import Image
Image(filename=f'/content/runs/detect/train/confusion_matrix.png', width=600)

!yolo task=detect mode=val model=/content/runs/detect/train/weights/best.pt data={dataset.location}/data.yaml

!yolo task=detect mode=predict model=/content/runs/detect/train/weights/best.pt conf=0.5 source={dataset.location}/test/images save_txt=true save_conf=true

import glob
from IPython.display import Image, display

for image_path in glob.glob(f'/content/runs/detect/predict/*.jpg')[:2]:
      display(Image(filename=image_path, height=600))
      print("\n")

!pip install opencv-python-headless matplotlib

import numpy as np
import torch
import cv2
from matplotlib import pyplot as plt
from ultralytics import YOLO

!pip install YOLOv8-Explainer

import zipfile
import osgeo_utils
file_path = '/content/multiple_folders.zip'
with zipfile.ZipFile(file_path, 'r') as zip_ref:
    zip_ref.extractall('/content')

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from IPython.display import display, Image

model_builder = keras.applications.xception.Xception
img_size = (299, 299)
preprocess_input = keras.applications.xception.preprocess_input
decode_predictions = keras.applications.xception.decode_predictions

last_conv_layer_name = "block14_sepconv2_act"

def get_img_array(img_path, size):
    img = keras.utils.load_img(img_path, target_size=size)
    array = keras.utils.img_to_array(img)
    array = np.expand_dims(array, axis=0)
    return array

def make_gradcam_heatmap(img_array, model, last_conv_layer_name, pred_index=None):
    grad_model = keras.models.Model(
        model.inputs, [model.get_layer(last_conv_layer_name).output, model.output]
    )

    with tf.GradientTape() as tape:
        last_conv_layer_output, preds = grad_model(img_array)
        if pred_index is None:
            pred_index = tf.argmax(preds[0])
        class_channel = preds[:, pred_index]

    grads = tape.gradient(class_channel, last_conv_layer_output)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    last_conv_layer_output = last_conv_layer_output[0]
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
    return heatmap.numpy()

def display_gradcam(img_path, heatmap, alpha=0.4):
    img = keras.utils.load_img(img_path)
    img = keras.utils.img_to_array(img)

    heatmap = np.uint8(255 * heatmap)
    jet = mpl.colormaps["jet"]
    jet_colors = jet(np.arange(256))[:, :3]
    jet_heatmap = jet_colors[heatmap]

    jet_heatmap = keras.utils.array_to_img(jet_heatmap)
    jet_heatmap = jet_heatmap.resize((img.shape[1], img.shape[0]))
    jet_heatmap = keras.utils.img_to_array(jet_heatmap)

    superimposed_img = jet_heatmap * alpha + img
    superimposed_img = keras.utils.array_to_img(superimposed_img)

    display(superimposed_img)

def generate_gradcam_heatmap(img_path):
    img_array = get_img_array(img_path, img_size)
    img_array = preprocess_input(img_array)

    model = model_builder(weights='imagenet')

    heatmap = make_gradcam_heatmap(img_array, model, last_conv_layer_name)

    display_gradcam(img_path, heatmap)

img_path = "/content/coconut-tree-disease-8/test/images/StemBleeding608_jpg.rf.f85ffa250001c8917479a8507233b157.jpg"
generate_gradcam_heatmap(img_path)

img_path = "/content/coconut-tree-disease-8/test/images/GrayLeafSpot1962_jpg.rf.a3111ff5f5f22e956b84e435157eb63d.jpg"
generate_gradcam_heatmap(img_path)
