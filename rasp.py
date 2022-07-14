# convert image to PDF

# from PIL import Image

# # convert image to a full page pdf
# input_img = Image.open(r'alien-storm.png')
# img = input_img.convert('RGB')
# img.save('output.pdf')

from PIL import Image, ImageOps
import img2pdf
import math
import os
import numpy as np



# constants
a4_paper_size_mm = (210, 297)
a3_paper_size_mm = (297, 420)
# a4_paper_size = (img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297))
# a3_paper_size = (img2pdf.mm_to_pt(297), img2pdf.mm_to_pt(420))
border_size_mm = 10; # 10mm

temp_dir = os.path.abspath("temp_images")



# process command line args






# enhance colours

def padded_num_string(num):
    if num < 10:
        return f"000{num}"
    if num < 100:
        return f"00{num}"
    if num < 1000:
        return f"0{num}"
    return f"{num}"

def dims_mm_to_pt(dims):
    return (img2pdf.mm_to_pt(dims[0]), img2pdf.mm_to_pt(dims[1]))

def print_image_info(filename):
    img = Image.open(filename)
    print("IMAGE INFORMATION:")
    print(f"filename: {filename}")
    print(f"format: {img.format}")
    print(f"size: {img.size}")
    print(f"mode: {img.mode}")

def make_slice_image(data, x1, y1, x_size, y_size, page_num):
    make_slice_image_array_slice(data, x1, y1, x_size, y_size, page_num)

def make_slice_image_array_slice(data, x1, y1, x_size, y_size, page_num):
    section = data[y1:y1 + y_size, x1:x1 + x_size, :]
    print(f"section shape: {section.shape}")

    # section = np.zeros([x_size, y_size, 3])
    # section[0:y_size, 0:x_size, 0:2] = data[y1:y1 + y_size, x1:x1 + x_size, :]

    # fill in empty
    if len(section) < y_size:
        n = y_size - len(section)
        print(f"... add {n} extra in Y")
        extra = np.zeros([n, len(section[0]), 3])
        extra = (extra * 255).astype(np.uint8)
        print(f"... extra shape (Y): {extra.shape}")
        section = np.concatenate([section, extra], axis=0)
        print(f"... section shape: {section.shape}")

    if len(section[0]) < x_size:
        n = x_size - len(section[0])
        print(f"... add {n} extra in X")
        extra = np.zeros([len(section), n, 3])
        extra = (extra * 255).astype(np.uint8)
        print(f"... extra shape (X): {extra.shape}")
        section = np.concatenate([section, extra], axis=1)
        print(f"... section shape: {section.shape}")

    # convert to image and save in temp dir
    print("convert array back to image")
    temp_img = Image.fromarray(section)
    print(f"temp_img.size: {temp_img.size}")
    page_num_str = padded_num_string(page_num)
    temp_img.save(os.path.join(temp_dir, f"temp{page_num_str}.png"))

def make_slice_image_for_loop(data, x1, y1, x_size, y_size, page_num):

    # section = np.zeros([x_size, y_size, 3])
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
    # temp_img = Image.fromarray(section)
    temp_img = Image.fromarray((section * 255).astype(np.uint8))
    # temp_img = Image.fromarray(section.astype(np.uint8))
    page_num_str = padded_num_string(page_num)
    temp_img.save(os.path.join(temp_dir, f"temp{page_num_str}.png"))
    print(f"temp_img.size: {temp_img.size}")

def resize_and_split(input_image, target_width_mm, paper_size_mm):
    print("RESIZING AND SPLITTING IMAGE:")
    input_img = Image.open(input_image)
    img = input_img.convert('RGB')
    print(f"input image size (pixels): {img.size}")
    target_size_mm = (target_width_mm, target_width_mm * (img.size[0] / img.size[1]))
    print(f"target size (mm): {target_size_mm}")
    print(f"paper size (mm): {paper_size_mm}")
    page_size_mm = (paper_size_mm[0] - (2 * border_size_mm),
                    paper_size_mm[1] - (2 * border_size_mm))
    print(f"page size (printable area) (mm): {page_size_mm}")
    # num_pages_horiz = (int) (target_size_mm[0] / page_size_mm[0])
    # num_pages_vert = (int) (target_size_mm[1] / page_size_mm[1])
    num_pages_horiz = target_size_mm[0] / page_size_mm[0]
    num_pages_vert = target_size_mm[1] / page_size_mm[1]
    print(f"num pages: horiz={num_pages_horiz}, vert={num_pages_vert}")
    print(f"fractional pages: horiz={math.modf(num_pages_horiz)[0]}, vert={math.modf(num_pages_vert)[0]}")
    print(f"modf(num pages): horiz={math.modf(num_pages_horiz)}, vert={math.modf(num_pages_vert)}")
    print(type(num_pages_vert))
    print(type(int(num_pages_vert)))

    # fraction of image to take per page
    img_page_frac_x = page_size_mm[0] / target_size_mm[0]
    img_page_frac_y = page_size_mm[1] / target_size_mm[1]
    img_page_pixels_x = img.size[0] * img_page_frac_x
    img_page_pixels_y = img.size[1] * img_page_frac_y
    print(f"fraction of image per page: horiz={img_page_frac_x}, vert={img_page_frac_y}")
    print(f"pixels of image per page: horiz={img_page_pixels_x}, vert={img_page_pixels_y}")

    # input_size = img.size
    # scale = width / img.size[0] # target width divided by current width
    # height = img.size[1] * scale
    # print(f"scale image by {scale}")
    # print(f"current size: {img.size}")
    # print(f"target size: {width}, {height}")

    print("deleting exiting files in temp dir...")
    num_deleted = 0
    for f in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, f))
        num_deleted += 1
    print(f"... deleted {num_deleted} files")

    print("converting image to numpy array")
    data = np.asarray(img)
    print(f"... numpy array dimensions: {data.shape}")
    print(f"... element data[0] = {data[0]}")
    print(f"... element data[0][0] = {data[0][0]}")
    print(f"... data.size: {data.size}")
    print(f"... data[0:190, 0:443, :].shape: {data[0:190, 0:443, :].shape}")
    print(f"... data[190:380, 443:453, :].shape: {data[190:380, 443:453, :].shape}")

    # print("the following images will be created:")
    # page_num = 0
    # px_rem_x = img.size[0]
    # px_rem_y = img.size[1]
    # # start and end points for slices
    # w1 = 0
    # w2 = 0
    # h1 = 0
    # h2 = 0
    # for y in range(int(num_pages_vert + 1)):
    # # for y in range(5):
    #     print(f"row {y + 1}")
    #     h = page_size_mm[1]
    #     if y >= int(num_pages_vert):
    #         h = page_size_mm[1] * math.modf(num_pages_vert)[0]
    #     # get pixels (height)
    #     pxh = img.size[1]
    #     px_rem_y -= img_page_pixels_y
    #     h2 = h1 + int(img_page_pixels_y)
    #     if px_rem_y < img_page_pixels_y:
    #         pxh = px_rem_y
    #         h2 = data.shape[1] - 1
    #     #w1 = 0
    #     for x in range(int(num_pages_horiz + 1)):
    #     # for x in range(2):
    #         page_num += 1
    #         w = page_size_mm[0]
    #         if x >= int(num_pages_horiz):
    #             w = page_size_mm[0] * math.modf(num_pages_horiz)[0]
    #         # get pixels (height)
    #         pxw = img.size[0]
    #         px_rem_x -= img_page_pixels_x
    #         w2 = w1 + int(img_page_pixels_x)
    #         if px_rem_x < img_page_pixels_x:
    #             pxw = px_rem_x
    #             w2 = data.shape[0] - 1

    #         print(f"p{page_num}({w}x{h}mm, {pxw}x{pxh} pixels, w={w1}-{w2}, h={h1}-{h2})")

    #         # print("slice section out of data array")
    #         section = data[w1:w2, h1:h2, :]
    #         print(f"section shape: {section.shape}")

    #         # convert to image and save in temp dir
    #         if x == 0 and y == 0:
    #             temp_img = Image.fromarray(section)
    #             page_num_str = padded_num_string(page_num)
    #             temp_img.save(os.path.join(temp_dir, f"temp{page_num_str}.png"))

    #         w1 = w2
    #         w2 = 0
    #     h1 = h2
    #     h2 = 0

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
            print(f"... p{page_num}(r{row}, c{col})")
            # page_num_str = padded_num_string(page_num)
            # make_slice_image(data, 0, 0, int(img_page_pixels_x), int(img_page_pixels_y), page_num)
            make_slice_image(data,
                             col * int(img_page_pixels_x),
                             row * int(img_page_pixels_y),
                             int(img_page_pixels_x), int(img_page_pixels_y), page_num)





# add border to image
# why does this convert to B&W?
def add_border(input_img):
    img = Image.open(input_img)
    border = (10, 50, 100, 200) # (left, top, right, bottom)
    img_with_border = ImageOps.expand(img, border=border, fill='rgb(255, 255, 255)')
    img_with_border.save('with_border.png')

# make pdf
def make_pdf(input_img):
    # paper_size = a4_paper_size
    paper_size = dims_mm_to_pt(a4_paper_size_mm)
    layout_fun = img2pdf.get_layout_fun(paper_size)
    with open("output.pdf", "wb") as f:
        f.write(img2pdf.convert(input_img, layout_fun=layout_fun))

def make_pdf_from_temp_images():
    print("make pdf document from images in temp dir...")
    files = os.listdir(temp_dir)
    print(f"... found {len(files)} files")





if __name__ == '__main__':
    img = 'alien-storm.png'
    print()
    print_image_info(img)
    print()
    resize_and_split(img, 500, a4_paper_size_mm)
    print()
    make_pdf_from_temp_images()
    # add_border(img)
