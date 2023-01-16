
import xml.etree.ElementTree as ET
import plistlib
import os
from PIL import Image

def crop_image(image_path, position, size):
    with Image.open(image_path) as im:
        x, y = position
        width, height = size
        im = im.crop((x, y, x + width, y + height))
        return im


def parse_string(s):
    # Initialize an empty list to store the tuples
    components = []
    tuples = []
    # Initialize an empty string to store the current component
    current_component = ""
    # Iterate through each character in the input string
    for c in s:
        # If we see a comma, add the current component to the tuple as an integer
        if c == ",":
            components.append(current_component)
            current_component = ""
        # If we see a close curly brace, add the current component to the tuple as an integer
        # and append the tuple to the list of tuples
        elif c == "}":
            components.append(current_component)
            current_component = ""
            my_tuple = [int(components[0]), int(components[1])]
            tuples.append(my_tuple)
        # If we see an open curly brace, initialize the list of components
        elif c == "{":
            components = []
        # Otherwise, add the character to the current component
        else:
            current_component += c
    return tuples

class Animation:
    size = []
    y = 0

if __name__ == '__main__':
    with open('C:/Users/tom/Pictures/duelyst_tests/f1_general_skinroguelegacy.plist', 'rb') as fp:
        destination_image = Image.new('RGBA', (2048, 2048))
        pl = plistlib.load(fp)
        frames = pl["frames"]
        animation_id = {}
        last_y = 0
        last_x = 0
        for key, frame in frames.items():
            full_animation_name = os.path.splitext(key)[0]
            animation_name = full_animation_name[:-4]
            animation_number = int(full_animation_name[-3:])
            if animation_name not in animation_id:
                print ("New animation: ", animation_name, last_y)
                animation_id[animation_name] = last_y
                last_y += 100
                last_x = 0
            for key, value in frame.items():
                if key == "frame" :
                    sliced_value = value[1:-1]
                    components = parse_string(sliced_value)
                    sub_image = crop_image('C:/Users/tom/Pictures/duelyst_tests/f1_general_skinroguelegacy.png', components[0], components[1])
                    last_x += 100
                    destination_image.paste(sub_image, (last_x, last_y))
        destination_image.save('C:/Users/tom/Pictures/duelyst_tests/foo.png')
