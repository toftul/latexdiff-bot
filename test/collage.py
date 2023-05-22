from PIL import Image, ImageDraw, ImageFont

def add_box(img, boxcolor='red'):
    # Add a border to the image
    border_size = 50
    img_with_border = Image.new('RGB', (img.width + border_size * 2, img.height + border_size * 2), "white")
    img_with_border.paste(img, (border_size, border_size))

    # Add a box around the image
    box_width = 5
    draw = ImageDraw.Draw(img_with_border)

    shift = 15

    draw.rectangle(
        (shift, shift, img_with_border.width-1-shift, img_with_border.height-1-shift), 
        outline=boxcolor, width=box_width
    )
    
    return img_with_border


def add_text(img, text='This is a text', fontsize=40, textcolor='blue'):
    # Define the text to be added and the font
    font = ImageFont.truetype("Arial.ttf", fontsize)

    # Calculate the size of the text
    text_size = font.getbbox(text)

    # Calculate the size of the canvas to add to the image
    canvas_width = img.width
    canvas_height = text_size[3] + 10

    # Create a new image with the canvas and paste the original image onto it
    new_img = Image.new('RGB', (canvas_width, img.height + canvas_height), "white")
    new_img.paste(img, (0, canvas_height))

    # Add the text to the image
    draw = ImageDraw.Draw(new_img)
    text_x = (new_img.width - text_size[2]) // 2
    text_y = 0
    draw.text((text_x, text_y), text, font=font, fill=textcolor)
    
    return new_img


def make_collage(img_left, img_right):
    # Define the height for both images
    height = 500

    # Calculate the new width for each image
    width1 = int((float(height) / img_left.size[1]) * img_left.size[0])
    width2 = int((float(height) / img_right.size[1]) * img_right.size[0])

    # Resize both images
    img_left = img_left.resize((width1, height))
    img_right = img_right.resize((width2, height))

    # Create a new image with the appropriate dimensions
    collage = Image.new('RGB', (width1 + width2, height))

    # Paste the two images onto the new image
    collage.paste(img_left, (0, 0))
    collage.paste(img_right, (width1, 0))

    return collage

def make_diff_image(path_img_old, path_img_new, path_img_diff):
    # Load the images
    img_old = Image.open(path_img_old)
    img_new = Image.open(path_img_new)

    # add box
    img_old = add_box(img_old, boxcolor='red')
    img_new = add_box(img_new, boxcolor='blue')

    # add text
    img_old = add_text(img_old, text='Old', fontsize=50, textcolor='red')
    img_new = add_text(img_new, text='New', fontsize=50, textcolor='blue')

    collage = make_collage(img_old, img_new)

    collage.save(path_img_diff)
