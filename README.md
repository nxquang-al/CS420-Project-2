# CS420-Project-2
## 1. INTRODUCTION
This is our solution for Project 2, course CS420 - Artificial Intelligence.
## 2. SETUP ENVIRONMENT
### Install via conda
```bash
# Create and activate a virtual environment
$ conda create -n treasure-island python=3.10 -y
$ conda activate treasure-island

# Install dependencies
$ pip install -r requirements.txt
```
## 3. RUN
We provides 2 modes to run the game: read map from text file or automatically generate a new map.
### Read input from text file
To run the game with provided map, you have to turn on the flag `-r, --read`.

Argument:
 * `file_path`: Path to the input file 

Here is a sample command:

```bash
$ python src/visualization.py -r data/input/MAP_01.txt
```
### Generate a new map with map shape
In this case, the flag `-g, --generate` must be turned on.

Argument
 * `width, height`: The expected width and height of the map

Sample command:

```bash
$ python src/visualization.py -g 64 64
```
## 4. VISUALIZATION
![CS418_demo_img1](https://user-images.githubusercontent.com/79528257/211090130-ea4785c9-22c4-461a-97bc-b0f77059fe8e.png)
![CS418_demo_img2](https://user-images.githubusercontent.com/79528257/211090225-271e5280-2eeb-4ede-95ee-ff4f72cab0a9.png)
