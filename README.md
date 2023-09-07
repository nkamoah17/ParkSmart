Parking Space Detection
This project uses deep learning to detect open parking spaces from camera footage. The model is trained to identify empty and occupied parking spots.

Getting Started
To use this project's parking space detection:

Clone this repository
Install dependencies: pip install -r requirements.txt
Prepare your camera footage:
Video should show a clear top-down view of a parking lot
Save footage as MP4, AVI, or other common video file format
Place video files in the input folder
Run parking spot detection: python detect.py
View output with parking spot overlays in the output folder
Training Your Own Model
To train the parking space detection model on new data:

Annotate parking spots in footage using the annotate.py script
Split annotated data into train and test sets
Update config.json with your dataset paths
Run python train.py to train a new model
Evaluate model performance on the test set
Contributing
Contributions to improve the parking space detection model are welcome! See CONTRIBUTING.md for more info.

License
This project is licensed under the MIT License - see the LICENSE file for details.