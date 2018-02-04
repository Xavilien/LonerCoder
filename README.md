# LonerCoder

### Your favourite retro game, played by your face against your friend. Sounds fun?

This is a remake of the ATARI game pong with two additional features:
1) The ability to control the paddle with your face
2) The ability to play with your friend on another computer to fight for the title of pong master

### How it was made

We used python, OpenCV and the almighty Tensorflow Object Detection API to track your face. For the multiplayer functionality, we used a socketserver with HTTP requests. This allows for concurrency so that you can play with your friends!

### Resources

- Tensorflow: https://www.tensorflow.org
- Object detection API: https://github.com/tensorflow/models/tree/master/research/object_detection
- OpenCV: https://opencv.org
