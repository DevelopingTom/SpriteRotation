import xml.etree.ElementTree as ET
import plistlib
import os
import sys
from pathlib import Path
from PIL import Image
from string import Template

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
    def __init__(self, name):
        self.name = name
        self.frames = []

    frames = []
    largest_size = [0, 0]
    name = ''

class SpriteDescription:
    animations = {}
    filepath = ''
    animation_size = [0, 0]

    def __init__(self, filepath):
        self.filepath = filepath

    def load(self):
        current_largest_size = [0, 0]
        with open(self.filepath, 'rb') as fp:
            pl = plistlib.load(fp)
            frames_description = pl["frames"]
            for key, current_animation in frames_description.items():
                frame = Frame()
                full_animation_name = os.path.splitext(key)[0]
                animation_name = full_animation_name[:-4]
                animation_number = int(full_animation_name[-3:])
                position_and_size = parse_position_and_size(current_animation["frame"][1:-1]) # remove wrapping brackets
                frame.position = position_and_size[0]
                frame.size = position_and_size[1]
                if animation_name not in self.animations:
                    self.animations[animation_name] = Animation(animation_name)
                self.animations[animation_name].frames.append(frame)
                # pre-compute largest frame size
                current_largest_size = self.animations[animation_name].largest_size
                self.animations[animation_name].largest_size[0] = max(current_largest_size[0], frame.size[0])
                self.animations[animation_name].largest_size[1] = max(current_largest_size[1], frame.size[1])
        self.animation_size = current_largest_size

    def compute_max_frame_size(self):
        size = [0, 0]
        for animation_name in self.animations:
            animation = self.animations[animation_name]
            size[0] = max(size[0], animation.largest_size[0])
            size[1] = max(size[1], animation.largest_size[1])
        return size

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

    def draw(self, sprite_description):
        self.destination_image = Image.new('RGBA', self.size)
        with Image.open(self.filename.with_suffix('.png')) as image:
            y = 0
            max_frame_size = sprite_description.compute_max_frame_size()
            for key, animation in sprite_description.animations.items():
                x = 0
                for frame in animation.frames:
                    sub_image = crop_image(image, frame.position, frame.size)
                    gap = (max_frame_size[0] - frame.size[0], max_frame_size[1] - frame.size[1])
                    center = (x * max_frame_size[0] + gap[0] / 2, y * max_frame_size[1] + gap[1] / 2)
                    self.destination_image.paste(sub_image, (int(center[0]), int(center[1])))
                    x += 1
                y += 1

    def save(self):
        self.destination_image.save('output/foo_cg.png')

# return {
# 	origin = flat.Vector2(11, 20),
# 	size = flat.Vector2(8, 2),
# 	animations = {
# 		move = {
# 			line = 1,
# 			numFrames = 4,
# 			frameDuration = 0.1
# 		},
# 		shoot = {
# 			line = 2,
# 			numFrames = 8,
# 			frameDuration = 0.07
# 		}
# 	},
# 	attachPoints = {
# 		crossbow = flat.Vector2(22, 11)
# 	}
# }

def spritelua(sprite_description, filepath):
    meta = """return {
    origin = flat.Vector2($origin),
    size = flat.Vector2($size),
    animations = {"""
    origin = [description.animation_size[0] / 2, description.animation_size[1] / 2]
    meta_data = {'origin': origin, 'size': description.animation_size}
    meta = Template(meta).substitute(meta_data)
    animation_template = """
        $animation_name = {
            line = $line,
            numFrames = $num_frames,
            frameDuration = 0.07
        }"""
    y = 0
    for key, animation in sprite_description.animations.items():
        animation_data = {'animation_name': key, 'line': str(y), 'num_frames': str(len(animation.frames))}
        if y != 0:
            meta += ','
        meta += Template(animation_template).substitute(animation_data)
        y += 1
    meta += '\n\t}\n}'

    lua_file = open("output/foo_cg.bar", "w")
    lua_file.write(meta)
    lua_file.close()


if __name__ == '__main__':
    file = sys.argv[1]
    description = SpriteDescription(file)
    description.load()
    size = description.compute_size()
    print("Image size: ", size)
    filename = os.path.splitext(file)[0]
    sprite = SpriteImage(size, Path(filename))
    sprite.draw(description)
    sprite.save()
    spritelua(description, "")
