import xml.etree.ElementTree as ET
import plistlib
import os
import sys
from pathlib import Path
from PIL import Image

def crop_image(image, position, size):
        x, y = position
        width, height = size
        image = image.crop((x, y, x + width, y + height))
        return image

def parse_position_and_size(s):
    components = []
    tuples = []
    current_component = ""
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

class Frame:
    position = []
    size = []

class Animation:
    frames = []
    largest_size = [0, 0]
    name = ''

class SpriteDescription:
    animations = {}
    filepath = ''

    def __init__(self, filepath):
        self.filepath = filepath

    def load(self):
        with open(self.filepath, 'rb') as fp:
            pl = plistlib.load(fp)
            frames = pl["frames"]
            for key, current_animation in frames.items():
                frame = Frame()
                full_animation_name = os.path.splitext(key)[0]
                animation_name = full_animation_name[:-4]
                animation_number = int(full_animation_name[-3:])
                position_and_size = parse_position_and_size(current_animation["frame"][1:-1]) # remove wrapping brackets
                frame.position = position_and_size[0]
                frame.size = position_and_size[1]
                if animation_name not in self.animations:
                    print ("New animation: ", animation_name)
                    self.animations[animation_name] = Animation()
                self.animations[animation_name].frames.append(frame)
                # pre-compute largest frame size
                current_largest_size = self.animations[animation_name].largest_size
                self.animations[animation_name].largest_size[0] = max(current_largest_size[0], frame.size[0])
                self.animations[animation_name].largest_size[1] = max(current_largest_size[1], frame.size[1])

    def compute_size(self):
        size = [0, 0]
        for animation_name in self.animations:
            animation = self.animations[animation_name]
            size[0] = max(size[0], animation.largest_size[0] * len(animation.frames))
            size[1] = max(size[1], animation.largest_size[1])
        size[1] = size[1] * len(self.animations)
        return size

class SpriteImage:
    size = []
    filename = ''
    destination_image = None

    def __init__(self, size, filename):
        self.size = size
        self.filename = filename

    def print(self, sprite_description):
        destination_image = Image.new('RGBA', self.size)
        with Image.open(self.filename + '.png') as image:
            for animation in sprite_description.animations:
                for frame in animation:
                    sub_image = crop_image(image, frame.position, frame.size)
                    #destination_image.paste(sub_image, ( , ))

    def save(self):
        with Image.open(self.filename + '.png') as image:
            sub_image = crop_image(image, position_and_size[0], position_and_size[1])
            #destination_image.save('output/' + name + '_cg.png')

if __name__ == '__main__':
    file = sys.argv[1]
    description = SpriteDescription(file)
    description.load()
    size = description.compute_size()
    filename = os.path.splitext(file)[0]
    sprite = SpriteImage(size, Path(filename).stem)
    #sprite.save()


    # with open(filename + '.plist', 'rb') as fp:
    #     with Image.open(filename + '.png') as image:
    #         destination_image = Image.new('RGBA', (2048, 2048))
    #         pl = plistlib.load(fp)
    #         frames = pl["frames"]
    #         animation_id = {}
    #         last_y = 0
    #         last_x = 0

    #         for key, current_animation in frames.items():
    #             frame = Frame()
    #             full_animation_name = os.path.splitext(key)[0]
    #             animation_name = full_animation_name[:-4]
    #             animation_number = int(full_animation_name[-3:])
    #             position_and_size = parse_position_and_size(current_animation["frame"][1:-1]) # remove wrapping brackets
    #             frame.position = position_and_size[0]
    #             frame.size = position_and_size[1]
    #             if animation_name not in animation_id:
    #                 print ("New animation: ", animation_name, last_y)
    #                 animation_id[animation_name] = Animation()
    #                 animation_id[animation_name].frames.append(frame)




    # sub_image = crop_image(image, position_and_size[0], position_and_size[1])
    # # destination_image.paste(sub_image, ( , ))
    # sprite.save()
    # output_name = Path(filename).stem
    # destination_image.save('output/' + output_name + '_cg.png')
