import getopt
import sys
import os
import math
from PIL import Image, ImageOps
import numpy as np
import img2pdf

# constants
a4_paper_size_mm = (210, 297)
a3_paper_size_mm = (297, 420)
temp_dir = os.path.abspath("temp_images")

def padded_num_string(num):
    if num < 10:
        return f"00{num}"
    if num < 100:
        return f"0{num}"
    return f"{num}"

def print_image_info(filename):
    img = Image.open(filename)
    print("IMAGE INFORMATION:")
    print(f"filename:      {filename}")
    print(f"format:        {img.format}")
    print(f"size (pixels): {img.size}")
    print(f"mode:          {img.mode}")

def clean_temp_dir():
    print(f"temp image dir path is {temp_dir}")
    if  not os.path.exists(temp_dir):
        print("... creating new temp dir")
        os.mkdir(temp_dir)
    if not os.path.isdir(temp_dir):
        print(f"\nERROR: {temp_dir} already exists, and is not a directory!\n")
        sys.exit(1)
    num_deleted = 0
    for f in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, f))
        num_deleted += 1
    print(f"... deleted {num_deleted} existing files in temp dir")

def make_slice_image(data, x1, y1, x_size, y_size):
    return make_slice_image_array_slice(data, x1, y1, x_size, y_size)

def make_slice_image_array_slice(data, x1, y1, x_size, y_size):
    section = data[y1:y1 + y_size, x1:x1 + x_size, :]
    # fill in empty side-strips
    if len(section) < y_size:
        n = y_size - len(section)
        extra = np.ones([n, len(section[0]), 3])
        extra = (extra * 255).astype(np.uint8)
        section = np.concatenate([section, extra], axis=0)
    if len(section[0]) < x_size:
        n = x_size - len(section[0])
        extra = np.ones([len(section), n, 3])
        extra = (extra * 255).astype(np.uint8)
        section = np.concatenate([section, extra], axis=1)
    return Image.fromarray(section)

def make_slice_image_for_loop(data, x1, y1, x_size, y_size):
    section = np.zeros([y_size, x_size, 3])
    print(f"section shape: {section.shape}")
    print(f"type={type(data[0][0][0])}")
    # print(f"section[0][0][0]={section[0][0][0]}")
    for y in range(y_size):
        for x in range(x_size):
            if x1 + x >= len(data[0]) or y1 + y >= len(data[0][0]):
            # if x >= 100 or y >= 50:
                section[x][y][0] = 1.0
                section[x][y][1] = 0.0
                section[x][y][2] = 0.0
            else:
                section[x][y][0] = data[x1 + x][y1 + y][0]
                section[x][y][1] = data[x1 + x][y1 + y][1]
                section[x][y][2] = data[x1 + x][y1 + y][2]
            #     section[y][x][0] = 1.0
            #     section[y][x][1] = 0.0
            #     section[y][x][2] = 0.0
            # else:
            #     section[y][x][0] = data[y1 + y][x1 + x][0]
            #     section[y][x][1] = data[y1 + y][x1 + x][1]
            #     section[y][x][2] = data[y1 + y][x1 + x][2]
            #     section[x][y][0] = 255
            #     section[x][y][1] = 0
            #     section[x][y][2] = 0
            # else:
            #     section[x][y][0] = data[x1 + x][y1 + y][0] * 255
            #     section[x][y][1] = data[x1 + x][y1 + y][1] * 255
            #     section[x][y][2] = data[x1 + x][y1 + y][2] * 255
    # convert to image and save in temp dir
    print("convert array back to image")
    return Image.fromarray((section * 255).astype(np.uint8))

def add_border(img, border_size_mm):
    """Add a white border of specified number of pixels."""
    # border can be a tuple of 1, 2 or 4 numbers
    border = (border_size_mm)
    return ImageOps.expand(img, border=border, fill='rgb(255, 255, 255)')

def save_temp_image(img, page_num):
    page_num_str = padded_num_string(page_num)
    img.save(os.path.join(temp_dir, f"temp{page_num_str}.png"))

def resize_and_split(input_image, target_axis, target_mm, paper_size_mm, border_size_mm):
    print("RESIZING AND SPLITTING IMAGE:")
    input_img = Image.open(input_image)
    img = input_img.convert('RGB')
    print(f"input image size (pixels): {img.size}")

    target_size_mm = (0, 0)
    if target_axis == "height":
        target_size_mm = (target_mm / (img.size[1] / img.size[0]),
                          target_mm)
    else: # target_axis == "width":
        target_size_mm = (target_mm,
                          target_mm / (img.size[0] / img.size[1]))

    print(f"target size (mm): {target_size_mm}")
    print(f"paper size (mm): {paper_size_mm}")
    page_size_mm = (paper_size_mm[0] - (2 * border_size_mm),
                    paper_size_mm[1] - (2 * border_size_mm))
    print(f"page size (printable area) (mm): {page_size_mm}")
    num_pages_horiz = target_size_mm[0] / page_size_mm[0]
    num_pages_vert = target_size_mm[1] / page_size_mm[1]
    print(f"num pages: horiz={num_pages_horiz}, vert={num_pages_vert}")
    print(f"fractional pages: horiz={math.modf(num_pages_horiz)[0]}, vert={math.modf(num_pages_vert)[0]}")
    print(f"modf(num pages): horiz={math.modf(num_pages_horiz)}, vert={math.modf(num_pages_vert)}")

    # fraction of image to take per page
    img_page_frac_x = page_size_mm[0] / target_size_mm[0]
    img_page_frac_y = page_size_mm[1] / target_size_mm[1]
    img_page_pixels_x = img.size[0] * img_page_frac_x
    img_page_pixels_y = img.size[1] * img_page_frac_y
    print(f"fraction of image per page: horiz={img_page_frac_x}, vert={img_page_frac_y}")
    print(f"pixels of image per page: horiz={img_page_pixels_x}, vert={img_page_pixels_y}")

    clean_temp_dir()

    print("converting image to numpy array")
    data = np.asarray(img)
    print(f"... numpy array dimensions: {data.shape}")
    print(f"... data.size: {data.size}")

    print("slice up image data and create new images...")
    modf_rows = math.modf(num_pages_vert)
    modf_cols = math.modf(num_pages_horiz)
    num_rows = int(modf_rows[1])
    num_cols = int(modf_cols[1])
    if modf_rows[0] > 0:
        num_rows += 1
    if modf_cols[0] > 0:
        num_cols += 1
    page_num = 0
    for row in range(num_rows):
        for col in range(num_cols):
            page_num += 1
            sub_img = make_slice_image(data,
                                       col * int(img_page_pixels_x),
                                       row * int(img_page_pixels_y),
                                       int(img_page_pixels_x), int(img_page_pixels_y))
            if border_size_mm > 0:
                sub_img = add_border(sub_img, border_size_mm)
            save_temp_image(sub_img, page_num)

def make_pdf_from_temp_images(output_fname, paper_size_mm):
    print("MAKE PDF DOCUMENT FROM IMAGES IN TEMP DIR:")
    images = []
    for fname in os.listdir(temp_dir):
        image_file = False
        if fname.endswith(".jpg"):
           image_file = True
        elif fname.endswith(".png"):
           image_file = True
        if image_file:
            images.append(os.path.join(temp_dir, fname))
    images.sort()
    print(f"... found {len(images)} image files")
    if len(images) > 0:
        paper_size_pt = (img2pdf.mm_to_pt(paper_size_mm[0]),
                         img2pdf.mm_to_pt(paper_size_mm[1]))
        layout_fun = img2pdf.get_layout_fun(paper_size_pt)
        with open(output_fname, "wb") as f:
            f.write(img2pdf.convert(images, layout_fun=layout_fun))
            print(f"... wrote file: {output_fname}")

def print_usage():
    print("\nUSAGE: python rasp.py -x [mm] [IMAGE_FILES...]")
    print()
    print("-x, --width      = target width in mm")
    print("-y, --height     = target height in mm")
    print("-p, --paper-type = (OPTIONAL) paper type (a4|a3), default is a4")
    print("-b, --border     = (OPTIONAL) border size in mm, default is 0")
    print()

def main(argv):
    target_width = -1
    target_height = -1
    target_mm = -1
    target_axis = ""
    paper_type = 'a4'
    paper_size_mm = (0, 0)
    border_mm = 0

    try:
        opts, args = getopt.getopt(argv,
                                   "hx:y:p:b:",
                                   ["width=", "height=", "paper-type=", "border="])

    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        if opt in ('-x', '--width'):
            target_width = int(arg)
        elif opt in ('-y', '--height'):
            target_height = int(arg)
        elif opt in ('-p', '--paper-type'):
            paper_type = arg
        elif opt in ('-b', '--border'):
            border_mm = int(arg)

    if target_width > 0 and target_height < 0:
        target_mm = target_width
        target_axis = "width"
    elif (target_width < 0 and target_height > 0):
        target_mm = target_height
        target_axis = "height"
    else:
        print("\nEither width or height must be set, but not both!\n")
        print_usage()
        sys.exit(2)

    if paper_type == 'a4':
        paper_size_mm = a4_paper_size_mm
    elif paper_type == 'a3':
        paper_size_mm = a3_paper_size_mm
    else:
        print(f"\nPaper size {paper_type} not recognised!\n")
        print_usage()
        sys.exit(2)

    # get input image filenames
    if len(args) < 1:
        print("\nYou must supply at least one image file!\n")
        print_usage()
        sys.exit(2)
    filenames = args

    print()
    print(f"... target size: {target_mm}mm")
    print(f"... target axis: {target_axis}")
    print(f"... paper type:  {paper_type}")
    print(f"... paper size:  {paper_size_mm} mm")
    print(f"... border size: {border_mm}mm")
    print(f"... image files: {filenames}")

    count = 0
    for fname in filenames:
        print()
        print(f"PROCESSING FILE: {count + 1}")
        print()
        print_image_info(fname)
        print()
        resize_and_split(fname, target_axis, target_mm, paper_size_mm, border_mm)
        print()
        # output filename format: fname_width_600mm_a4.pdf
        size_str = target_axis + "_" + str(target_mm) + "mm"
        output_fname = fname.split(".")[0] + "_" + size_str + "_" + paper_type + ".pdf"
        make_pdf_from_temp_images(output_fname, paper_size_mm)
        print()
        count += 1
    if count == 1:
        print("1 file processed")
    else:
        print(f"\n{count} files processed")
    print()

if __name__ == '__main__':
    main(sys.argv[1:])
