import PIL
import os.path
import PIL.ImageDraw  

def get_palette(path, rect_width, rect_height, left_margin=0, top_margin=0, right_margin=0, bottom_margin=0):
    image = PIL.Image.open(path).convert("RGB")
    color_array = []
    for x in range((image.width-left_margin-right_margin)/rect_width):
        color_array.append([])
        for y in range((image.height-top_margin-bottom_margin)/rect_height):
            color_array[x].append(image.getpixel((x*rect_width+left_margin,y*rect_height+top_margin)))
    image.close()
    return color_array

def find_palettes_from_array(palette_array, rgb):
    for i in range(len(palette_array)):
        for j in range(len(palette_array[0])):
            if palette_array[i][j] == rgb:
                return hex(16*i+j)

def find_level_palettes(path, rect_width, rect_height, left_margin=0, top_margin=0, right_margin=0, bottom_margin=0):
    level_color_array = []
    paletteArray = get_palette(os.path.join(os.getcwd(),"9.png"), 32, 32, 16, 18, 16, 2)
    image = PIL.Image.open(path).convert("RGB")
    for y in range(((image.height-top_margin-bottom_margin)/rect_height)+1):
        for x in range(((image.width-left_margin-right_margin)/rect_width)+1):
            #print image.getpixel((x*rect_width+left_margin,y*rect_height+top_margin))
            #print (x,y)
            #print "\n"
            level_color_array.append((
                find_palettes_from_array(paletteArray, image.getpixel((x*rect_width+left_margin,y*rect_height+top_margin))),
                find_palettes_from_array(paletteArray, image.getpixel((x*rect_width+left_margin+1,y*rect_height+top_margin))),
                find_palettes_from_array(paletteArray, image.getpixel((x*rect_width+left_margin+19,y*rect_height+top_margin)))
            ))
    return level_color_array

if __name__ == '__main__':
    find_level_palettes(os.path.join(os.getcwd(),"10.png"), 56, 24, 23, 18, 21, 2)