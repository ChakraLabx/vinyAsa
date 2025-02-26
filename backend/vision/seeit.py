import os
import PIL
from PIL import ImageDraw

def save_results(image_list, results, labels, output_dir='output/', threshold=0.5):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for idx, im in enumerate(image_list):
        im = draw_box(im, results[idx], labels, threshold=threshold)

        out_path = os.path.join(output_dir, f"{idx}.jpg")
        im.save(out_path, quality=95)
        print("save result to: " + out_path)

def draw_box_recog(im, result, lables, threshold=0.5):
    draw_thickness = min(im.size) // 320
    draw = ImageDraw.Draw(im)
    color_list = get_color_map_list(len(lables))
    clsid2color = {n.lower():color_list[i] for i,n in enumerate(lables)}
    result = [r for r in result if r["score"] >= threshold]

    for dt in result:
        color = tuple(clsid2color[dt["type"]])
        xmin, ymin, xmax, ymax = dt["bbox"]
        draw.line(
            [(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin),
             (xmin, ymin)],
            width=draw_thickness,
            fill=color)

        # draw label
        text = "{} {:.4f}".format(dt["type"], dt["score"])
        tw, th = imagedraw_textsize_c(draw, text)
        draw.rectangle(
            [(xmin + 1, ymin - th), (xmin + tw + 1, ymin)], fill=color)
        draw.text((xmin + 1, ymin - th), text, fill=(255, 255, 255))
    return im

def draw_box(im, result, labels, threshold=0.1):
    draw_thickness = min(im.size) // 320
    draw = ImageDraw.Draw(im)
    color_list = get_color_map_list(len(labels))
    clsid2color = {n.lower():color_list[i] for i,n in enumerate(labels)}
    result = [r for r in result if "score" not in r or r["score"] >= threshold]

    for item in result:
        color = tuple(clsid2color[item['type'].lower()])
        xmin, ymin, xmax, ymax = item['x0'], item['top'], item['x1'], item['bottom']
        draw.line(
            [(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin),
                (xmin, ymin)],
            width=draw_thickness,
            fill=color)

        # draw label
        text = "{} {:.4f}".format(item['type'], item['score'])
        tw, th = imagedraw_textsize_c(draw, text)
        draw.rectangle(
            [(xmin + 1, ymin - th), (xmin + tw + 1, ymin)], fill=color)
        draw.text((xmin + 1, ymin - th), text, fill=(255, 255, 255))

    return im

def get_color_map_list(num_classes):
    """
    Args:
        num_classes (int): number of classes
    Returns:
        color_map (list): RGB color list
    """
    # Custom colors for specific classes
    custom_colors = {
        'header': [168, 68, 1],   
        'text': [104, 138, 232],   
        'table': [128, 0, 128],  
    }

    color_map = []
    for i in range(num_classes):
        if i == 7:  # Header
            color_map.append(custom_colors['header'])
        elif i == 1:  # Text
            color_map.append(custom_colors['text'])
        elif i == 5:  # Table
            color_map.append(custom_colors['table'])
        else:
            # Generate a unique color based on index
            r = (i * 100 + 50) % 255
            g = (i * 150 + 50) % 255
            b = (i * 200 + 50) % 255
            color_map.append([r, g, b])
    
    return color_map

def imagedraw_textsize_c(draw, text):
    if int(PIL.__version__.split('.')[0]) < 10:
        tw, th = draw.textsize(text)
    else:
        left, top, right, bottom = draw.textbbox((0, 0), text)
        tw, th = right - left, bottom - top

    return tw, th
