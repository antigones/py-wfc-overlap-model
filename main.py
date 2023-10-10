import numpy as np
from collections import defaultdict 
from PIL import Image
import glob
from overlap_model import OverlapModel




class Color:

    def __init__(self,r:int,g:int,b:int,a:int=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def __eq__(self, other):
        return self.r == other.r and self.g == other.g and self.b == other.b and self.a == other.a

    def __hash__(self):
        return hash((self.r, self.g, self.b, self.a))


def __image_to_color_indexed_image(input_img, color_dict):
    color_indexed_image = [[0 for x in range(len(input_img[0]))] for y in range(len(input_img)) ]
    for i in range(len(input_img)):
        for j in range(len(input_img[i])):
            # elm = input_img[i][j]
            color = Color(input_img[i][j][0],input_img[i][j][1],input_img[i][j][2])
            color_indexed_image[i][j] = color_dict[color]
    return color_indexed_image

def __load_from_tileset(tilset_src="tilesets\circuits\*.png"):
    color_indexed_tileset = list()
    color_dict = dict()
    c_idx = 0
    for img in glob.glob(tilset_src):
        im = Image.open(img)
        input_img = np.array(im)
        for elm in input_img:
            for i in elm:
                color = Color(i[0],i[1],i[2])
                if color not in color_dict.keys():
                    color_dict[color] = c_idx
                    c_idx+=1
        rotation_degrees = [0,90,180]
        for degrees in rotation_degrees:
            im_rotate = im.rotate(degrees)
            input_rotated_img = np.array(im_rotate)
            color_indexed_image = __image_to_color_indexed_image(input_img=input_rotated_img, color_dict=color_dict)
            color_indexed_tileset.append(color_indexed_image)
    color_decode = dict((v,k) for k,v in color_dict.items())
    return color_indexed_tileset, color_dict, color_decode


def __calc_adjiacencies(color_indexed_tileset):
    tile_dict = dict()
    rule_dict = defaultdict(lambda:defaultdict(lambda:set()))
    c = 0
    for color_indexed_tile in color_indexed_tileset:
        tile_dict[c] = color_indexed_tile
        c+=1

    for k,v in tile_dict.items():
        for k_other,v_other in tile_dict.items():
            if v[-1] == v_other[0]:
                # vertically overlapping
                # and a tile can overlap with itself (palindrome)
                # add to adj_dict
                rule_dict[k][(1,0)].add(k_other)
                rule_dict[k_other][(-1,0)].add(k)
            
            last_horz_item = list()
            for i in v:
                last_horz_item.append(i[-1])
            last_horz_item_other = list()
            for i in v_other:
                last_horz_item_other.append(i[0])
            if last_horz_item == last_horz_item_other:
                # horizontally overlapping
                rule_dict[k][(0,1)].add(k_other)
                rule_dict[k_other][(0,-1)].add(k)            
    return tile_dict, rule_dict

def __generate_output_img(matrix,color_decode,tass_size,out_size):
    out_img = [[[] for x in range(len(matrix[0]))] for y in range(len(matrix)) ]
    for i in range(len(matrix)):
        elm = matrix[i]
        for j in range(len(elm)):
            tile_set = matrix[i][j]
            t = tile_set.pop()
            encoded_tile = tile_dict[t]

            out_tile = [[[] for x in range(len(encoded_tile[0]))] for y in range(len(encoded_tile)) ]
            for k in range(len(encoded_tile)):
                for w in range(len(encoded_tile[k])):
                    out_color = color_decode[encoded_tile[k][w]]
                    out_tile[k][w] = [out_color.r, out_color.g, out_color.b]

            out_img[i][j] = out_tile

    img = Image.new('RGB', (tass_size*out_size, tass_size*out_size))
    x = 0
    y = 0

    tile_counter = 0
    row_counter = 0
    for tile_row in out_img:
        for tile in tile_row:
            y = TASS_SIZE*row_counter
            for tile_row in tile:
                x = TASS_SIZE*tile_counter
                
                for pixel in tile_row: 
                    r = pixel[0]
                    g = pixel[1]
                    b = pixel[2]
                    img.putpixel((x,y), (r,g,b))
                    x=x+1
                y+=1
            
            tile_counter=tile_counter+1
        x = 0
        tile_counter = 0
        row_counter = row_counter + 1
    return img

color_indexed_tileset, color_dict, color_decode = __load_from_tileset(tilset_src="tilesets\circuits\*.png")
tile_dict, rule_dict = __calc_adjiacencies(color_indexed_tileset=color_indexed_tileset)


OUT_SIZE=30
TASS_SIZE=14

model = OverlapModel(rules=rule_dict,size=OUT_SIZE)
collapsed, matrix, steps= model.solve()
img = __generate_output_img(matrix, color_decode=color_decode, tass_size=TASS_SIZE, out_size=OUT_SIZE)
img.save('out.png')