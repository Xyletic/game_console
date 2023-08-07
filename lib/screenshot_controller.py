import displayio
import os

def create_bmp_header(width, height, bpp=16):
    # BMP file header (14 bytes)
    file_header = bytearray([66, 77,           # BM
                             0, 0, 0, 0,       # File size (will fill in later)
                             0, 0,             # Reserved
                             0, 0,             # Reserved
                             54, 0, 0, 0])     # Offset to pixel data

    # DIB header (40 bytes)
    dib_header = bytearray([40, 0, 0, 0,                       # DIB header size
                            width & 0xFF, (width >> 8) & 0xFF, (width >> 16) & 0xFF, (width >> 24) & 0xFF,  # Width
                            height & 0xFF, (height >> 8) & 0xFF, (height >> 16) & 0xFF, (height >> 24) & 0xFF,  # Height
                            1, 0,                             # Color planes
                            bpp, 0,                           # Bits per pixel
                            0, 0, 0, 0,                       # No compression
                            0, 0, 0, 0,                       # Image size (will fill in later)
                            0, 0, 0, 0,                       # X pixels/meter (unspecified)
                            0, 0, 0, 0,                       # Y pixels/meter (unspecified)
                            0, 0, 0, 0,                       # Total colors (unspecified)
                            0, 0, 0, 0])                      # Important colors (unspecified)

    return file_header + dib_header

def write_bmp_header(file, width, height, bpp=16):
    # Use the given function to generate the header
    bmp_header = create_bmp_header(width, height, bpp)
    file.write(bmp_header)

def write_row_to_bmp(file, row_pixel_data):
    row = []
    for color_16bit in row_pixel_data:
        # Extract 5-6-5 components
        r_5bit = (color_16bit & 0xF800) >> 8
        g_6bit = (color_16bit & 0x07E0) >> 3
        b_5bit = (color_16bit & 0x001F) << 3
        
        # Expand to 8-bit per channel for BMP
        r = r_5bit | (r_5bit >> 5)
        g = g_6bit | (g_6bit >> 6)
        b = b_5bit | (b_5bit >> 5)
        
        row.extend([b, g, r])
    # Padding for BMP row
    while len(row) % 4 != 0:
        row.append(0)
    file.write(bytearray(row))

def capture_screenshot(bitmap):
    width, height = 160, 128
    try:
        os.mkdir("/sd/screenshots/")
    except OSError:
        pass
    with open("/sd/screenshots/screenshot.bmp", "wb") as f:
        write_bmp_header(f, width, height)
        for y in range(height):
            row_pixel_data = []
            for x in range(width):
                pixel = bitmap[x, y]
                row_pixel_data.append(pixel)

            write_row_to_bmp(f, row_pixel_data)


# def capture_screenshot(group: displayio.Group):
#     width, height = 160, 128
#     try:
#         os.mkdir("/sd/screenshots/")
#     except OSError:
#         pass
#     with open("/sd/screenshots/screenshot.bmp", "wb") as f:
#         write_bmp_header(f, width, height)
        
#         for y in range(height):
#             row_pixel_data = []
#             for x in range(width):
#                 pixel = get_pixel_from_group(group, x, y)
#                 row_pixel_data.append(pixel)

#             write_row_to_bmp(f, row_pixel_data)

def get_pixel_from_group(group, x, y):
    # Given an x, y coordinate, fetch the pixel from relevant item in the group
    for obj in group:
        # Check if it's a TileGrid (like for images)
        if isinstance(obj, displayio.TileGrid):
            adjusted_x = x - obj.x
            adjusted_y = y - obj.y
            print(f"x={x}, y={y}, obj.x={obj.x}, obj.y={obj.y}, adjusted_x={adjusted_x}, adjusted_y={adjusted_y}")
            print(f"TileGrid dimensions: {obj.width}x{obj.height}")
            if hasattr(obj, 'bitmap'):
                print(f"Backing bitmap dimensions: {obj.bitmap.width}x{obj.bitmap.height}")
            if 0 <= adjusted_x < obj.width and 0 <= adjusted_y < obj.height:
                pixel = obj[adjusted_x, adjusted_y]
                if isinstance(pixel, int) and hasattr(obj, 'palette'):
                    return obj.palette[pixel]
                else:
                    return pixel
        # Check if it's a Rect object
        elif isinstance(obj, displayio.Rect):
            if obj.x <= x < obj.x + obj.width and obj.y <= y < obj.y + obj.height:
                return obj.fill # Assuming `fill` attribute holds the color
        # If group contains other groups, handle them recursively
        elif isinstance(obj, displayio.Group):
            pixel = get_pixel_from_group(obj, x, y)
            if pixel is not None:
                return pixel
    return None  # Or some default value


# def pixel_data_to_bmp(pixel_data, width, height):
#     bmp_data = create_bmp_header(width, height, bpp=16)
    
#     # Convert 16-bit pixel data to BMP format
#     for y in range(height-1, -1, -1):  # BMP stores rows bottom-to-top
#         row = []
#         for x in range(width):
#             color_16bit = pixel_data[y * width + x]
            
#             # Extract 5-6-5 components
#             r_5bit = (color_16bit & 0xF800) >> 8
#             g_6bit = (color_16bit & 0x07E0) >> 3
#             b_5bit = (color_16bit & 0x001F) << 3
            
#             # Expand to 8-bit per channel for BMP
#             r = r_5bit | (r_5bit >> 5)
#             g = g_6bit | (g_6bit >> 6)
#             b = b_5bit | (b_5bit >> 5)
            
#             row.extend([b, g, r])
            
#         # Padding for BMP row
#         while len(row) % 4 != 0:
#             row.append(0)
#         bmp_data.extend(row)

#     # Update BMP header with image size
#     img_size = len(bmp_data) - 54
#     bmp_data[2:6] = [img_size & 0xFF, (img_size >> 8) & 0xFF, (img_size >> 16) & 0xFF, (img_size >> 24) & 0xFF]
#     bmp_data[34:38] = [img_size & 0xFF, (img_size >> 8) & 0xFF, (img_size >> 16) & 0xFF, (img_size >> 24) & 0xFF]

#     return bmp_data