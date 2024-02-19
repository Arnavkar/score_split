from pdf2image import convert_from_path
from PIL import Image, ImageOps

def read_pixels(text_file_path):
    # Open the file in read mode ('r')
    with open(text_file_path, 'r') as file:
        lines = file.readlines()

        crop_dict = {}
        for idx, line in enumerate(lines):
            if "Part: " in line:
                part = line.split("Part: ")[1].strip()
                crop_dict[idx] = {'part': part ,'first_top':None, 'first_bottom':None, 'rest_top':None, 'rest_bottom':None}

            if "Left" in line:
                #Left: 150
                left = int(line.split("Left: ")[1].strip())

            if "Right" in line:
                #Left: 150
                right = int(line.split("Right: ")[1].strip())

            if "First" in line:
                for i in range(len(crop_dict)):
                    coords = lines[idx+i+1].strip().split(' ')
                    crop_dict[i]['first_top'] = [int(x) for x in (left, coords[0], right, coords[1])]
                    crop_dict[i]['first_bottom'] = [int(x) for x in (left, coords[2], right, coords[3])]

            if "Rest" in line:
                for i in range(len(crop_dict)):
                    coords = lines[idx+i+1].strip().split(' ')
                    crop_dict[i]['rest_top'] = [int(x) for x in (left, coords[0], right, coords[1])]
                    crop_dict[i]['rest_bottom'] = [int(x) for x in (left, coords[2], right, coords[3])]
    return crop_dict

def create_stacked_image_from_pdf(pdf_path, crop_dict):
    images = convert_from_path(pdf_path)
    border_width = 1

    pg_height = images[0].size[1]
    pg_width = images[0].size[0] 

    for part in crop_dict.values():
        first_top = part['first_top']
        #convert list to tuple
        first_top = tuple(first_top)

        first_bottom = part['first_bottom']
        first_bottom = tuple(first_bottom)

        rest_top = part['rest_top']
        rest_top = tuple(rest_top)

        rest_bottom = part['rest_bottom']
        rest_bottom = tuple(rest_bottom)

        cropped_images = []

        for idx,image in enumerate(images[3:-2]):

            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            if idx == 0:
                cropped_1 = image.crop(first_top)
                cropped_2 = image.crop(first_bottom)
                cropped_1 = ImageOps.expand(cropped_1, border=border_width, fill='black')
                cropped_2 = ImageOps.expand(cropped_2, border=border_width, fill='black')

            else:
                cropped_1 = image.crop(rest_top)
                cropped_2 = image.crop(rest_bottom)
                cropped_1 = ImageOps.expand(cropped_1, border=border_width, fill='black')
                cropped_2 = ImageOps.expand(cropped_2, border=border_width, fill='black')

            cropped_images.append(cropped_1)
            cropped_images.append(cropped_2)
            print(f'Image crop count: {idx}')

        idx = 0
        page_count = 1
        current_y = 0
        
        pages = []

        page = Image.new('RGB', (pg_width, pg_height), (255, 255, 255))
        pages.append(page)

        while idx < len(cropped_images):
            img = cropped_images[idx]
            page.paste(img, (50, current_y))
            current_y += img.size[1]
            idx += 1

            if idx == len(cropped_images): break

            if current_y + cropped_images[idx].size[1]> pg_height:
                # Create a new image with the total height and max width
                page = Image.new('RGB', (pg_width, pg_height), (255, 255, 255))
                current_y = 0
                pages.append(page)
        
        part_name = part['part']
        pages[0].save(f'./{part_name}.pdf', save_all=True, append_images=pages[1:], resolution=100.0)
        print(f'Part saved: {part_name}.pdf')

            
# Example usage
pdf_path = './akiho_score.pdf'  # Replace this with the path to your PDF file
 # Replace with your desired output folder path
pixel_path = './pixels.txt'
crop_dict = read_pixels(pixel_path)
create_stacked_image_from_pdf(pdf_path, crop_dict)

