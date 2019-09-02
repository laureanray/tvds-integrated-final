import numpy as np
import tensorflow as tf
import cv2 as cv

cap = cv.VideoCapture('test_images/vid.mp4')

# Read the graph.
with tf.gfile.FastGFile('cars_inference_graph/frozen_inference_graph2.pb', 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())

with tf.Session() as sess:
    # Restore session
    sess.graph.as_default()
    tf.import_graph_def(graph_def, name='')

    while True:
        ret, frame = cap.read()    
        # Read and preprocess an image.
        img = cv.resize(frame, (960, 540))
        rows = img.shape[0]
        cols = img.shape[1]
        inp = cv.resize(img, (300, 300))
        inp = inp[:, :, [2, 1, 0]]  # BGR2RGB

        # Run the model
        out = sess.run([sess.graph.get_tensor_by_name('num_detections:0'),
                        sess.graph.get_tensor_by_name('detection_scores:0'),
                        sess.graph.get_tensor_by_name('detection_boxes:0'),
                        sess.graph.get_tensor_by_name('detection_classes:0')],
                    feed_dict={'image_tensor:0': inp.reshape(1, inp.shape[0], inp.shape[1], 3)})

        # Visualize detected bounding boxes.
        num_detections = int(out[0][0])
        for i in range(num_detections):
            classId = int(out[3][0][i])
            score = float(out[1][0][i])
            
           
            bbox = [float(v) for v in out[2][0][i]]
            if score > 0.3:
                x = bbox[1] * cols
                y = bbox[0] * rows
                right = bbox[3] * cols
                bottom = bbox[2] * rows
                print(classId)
                if classId == 1:
                    print('Car')
                elif classId == 2:
                    print('Plate')
                else:
                    print('Truck')
                
                # print(score * 100)
                cv.rectangle(img, (int(x), int(y)), (int(right),
                                                    int(bottom)), (125, 255, 51), thickness=2)

        cv.imshow('TensorFlow MobileNet-SSD', img)
    
        # cv.waitKey(0)
        if cv.waitKey(0) & 0xFF == ord('q'):
            break

    cv.destroyAllWindows()
    cap.release()