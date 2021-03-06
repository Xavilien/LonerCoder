import numpy as np
import sys
import tensorflow as tf
import cv2
from threading import Thread
from time import sleep


class FaceDetection(Thread):
    cap = cv2.VideoCapture(0)

    path = "/Users/xavilien/Desktop/School/1Secondary/2018/Non-Core/CEP/Hack&Roll/LonerCoder"

    # This is needed since the notebook is stored in the object_detection folder.
    sys.path.append("..")
    sys.path.append("data")
    sys.path.append(path + "models/research/object_detection")
    sys.path.append(path + "models/research/")
    # print(sys.path)

    # ## Object detection imports
    # Here are the imports from the object detection module.
    from utils import label_map_util

    # # Model preparation

    # ## Variables
    #
    # Any model exported using the `export_inference_graph.py` tool can be loaded here simply by changing `PATH_TO_CKPT` to
    # point to a new .pb file.
    #
    # By default we use an "SSD with Mobilenet" model here. See the
    # [detection model zoo](https://github.com/tensorflow/models/blob/master/object_detection/g3doc/detection_model_zoo.md)
    # for a list of other models that can be run out-of-the-box with varying speeds and accuracies.

    # What model to download.
    # MODEL_FILE = MODEL_NAME + '.tar.gz'
    # DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'
    MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'

    # Path to frozen detection graph. This is the actual model that is used for the object detection.
    PATH_TO_CKPT = path + '/models/research/object_detection/' + MODEL_NAME + '/frozen_inference_graph.pb'

    # List of the strings that is used to add correct label for each box.
    PATH_TO_LABELS = path + '/models/research/object_detection/data/mscoco_label_map.pbtxt'

    NUM_CLASSES = 90

    # ## Load a (frozen) Tensorflow model into memory.
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

    # ## Loading label map
    # Label maps map indices to category names, so that when our convolution network predicts `5`, we know that this
    # corresponds to `airplane`.  Here we use internal utility functions, but anything that returns a dictionary mapping
    # integers to appropriate string labels would be fine

    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)

    x = None

    def __init__(self, event):
        super(FaceDetection, self).__init__()
        self.event = event  # Allow us to stop the thread when app is quit

    def run(self):
        self.capture()

    def capture(self):
        # Detection
        with self.detection_graph.as_default():
            with tf.Session(graph=self.detection_graph) as sess:
                while self.event.is_set():
                    ret, image_np = self.cap.read()
                    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                    image_np_expanded = np.expand_dims(image_np, axis=0)
                    image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')

                    # Each box represents a part of the image where a particular object was detected.
                    boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')

                    # Each score represent how level of confidence for each of the objects.
                    # Score is shown on the result image, together with the class label.
                    scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
                    classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
                    num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

                    # Actual detection.
                    (boxes, scores, classes, num_detections) = sess.run(
                        [boxes, scores, classes, num_detections],
                        feed_dict={image_tensor: image_np_expanded})

                    # Get only the people in the frame
                    _, person_elements = np.where(classes == 1)

                    # Get the x-coordinate of the person by taking the average x-coordinate of two corners
                    person = boxes[0][person_elements[0]]
                    self.x = (person[1] + person[3]) / 2
                    # print(self.x)

                    sleep(0.1)
