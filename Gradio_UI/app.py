import fitz  # PyMuPDF
import gradio as gr
import os
import zipfile

# Helper function to find color areas
def find_color_areas(page, target_color, tolerance=30):
    pix = page.get_pixmap()
    width, height = pix.width, pix.height
    visited = [[False for _ in range(width)] for _ in range(height)]
    rectangles = []

    def flood_fill(x, y):
        stack = [(x, y)]
        rects = []
        while stack:
            cx, cy = stack.pop()
            if visited[cy][cx]:
                continue

            visited[cy][cx] = True
            pixel_color = pix.pixel(cx, cy)
            r, g, b = pixel_color[:3]

            if (abs(r - target_color[0]) <= tolerance and
                abs(g - target_color[1]) <= tolerance and
                abs(b - target_color[2]) <= tolerance):
                rects.append(fitz.Rect(cx, cy, cx + 1, cy + 1))
                if cx > 0: stack.append((cx - 1, cy))
                if cx < width - 1: stack.append((cx + 1, cy))
                if cy > 0: stack.append((cx, cy - 1))
                if cy < height - 1: stack.append((cx, cy + 1))

        if rects:
            bbox = fitz.Rect(min([r.x0 for r in rects]),
                             min([r.y0 for r in rects]),
                             max([r.x1 for r in rects]),
                             max([r.y1 for r in rects]))
            return bbox
        return None

    for y in range(height):
        for x in range(width):
            if not visited[y][x]:
                bbox = flood_fill(x, y)
                if bbox:
                    rectangles.append(bbox)
    return rectangles

def merge_overlapping_rectangles(rectangles):
    merged_rects = []
    while rectangles:
        rect = rectangles.pop(0)
        to_merge = [rect]
        for other in rectangles[:]:
            if rect.intersects(other):
                to_merge.append(other)
                rectangles.remove(other)
        merged_rect = fitz.Rect(
            min([r.x0 for r in to_merge]),
            min([r.y0 for r in to_merge]),
            max([r.x1 for r in to_merge]),
            max([r.y1 for r in to_merge])
        )
        merged_rects.append(merged_rect)
    return merged_rects

def markup_color_regions(doc, color_comment_pair, tolerance=30):
    for page_num in range(len(doc)):
        page = doc[page_num]
        target_color = color_comment_pair['color']
        comment = color_comment_pair['comment']
        stroke_color = color_comment_pair['stroke_color']

        rectangles = find_color_areas(page, target_color, tolerance)
        if rectangles:
            merged_rectangles = merge_overlapping_rectangles(rectangles)
            for bbox in merged_rectangles:
                annot = page.add_rect_annot(bbox)
                annot.set_colors(stroke=stroke_color)
                annot.set_border(width=2)
                annot.set_info({"title": "Markup", "content": comment})
                annot.update()

def process_pdf_files(input_pdfs, color_comment_option, tolerance, custom_color, custom_comment, custom_stroke_color):
    color_comment_pairs = [
        {
            "color": (235, 128, 138),
            "comment": "Structural Slab greater than architectural slab",
            "stroke_color": (1, 0, 0)
        },
        {
            "color": (128, 253, 128),
            "comment": "Arch Slab greater than Structure",
            "stroke_color": (0, 1, 0)
        }
    ]
    
    # Add custom color-comment pair if provided
    if custom_color and custom_comment and custom_stroke_color:
        custom_color_tuple = tuple(map(int, custom_color.split(',')))  # Convert color to tuple
        custom_stroke_tuple = tuple(map(int, custom_stroke_color.split(',')))  # Convert stroke to tuple
        color_comment_pairs.append({
            "color": custom_color_tuple,
            "comment": custom_comment,
            "stroke_color": custom_stroke_tuple
        })

    # Check if the option is valid
    if isinstance(color_comment_option, int) and 0 <= color_comment_option < len(color_comment_pairs):
        selected_color_comment = color_comment_pairs[color_comment_option]
    else:
        raise ValueError("Invalid selection for color-comment pair")

    # Create a directory to store the modified PDFs
    output_dir = "modified_pdfs"
    os.makedirs(output_dir, exist_ok=True)

    # List to keep track of all modified PDF file paths
    modified_files = []

    # Process each input PDF file
    for pdf_file in input_pdfs:
        with open(pdf_file.name, "rb") as file_stream:
            doc = fitz.open(stream=file_stream.read(), filetype="pdf")
            markup_color_regions(doc, selected_color_comment, tolerance)

            # Save the modified PDF
            output_pdf_path = os.path.join(output_dir, os.path.basename(pdf_file.name))
            doc.save(output_pdf_path)
            doc.close()
            modified_files.append(output_pdf_path)

    # Create a zip file containing all modified PDFs
    zip_filename = "modified_pdfs.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in modified_files:
            zipf.write(file, os.path.basename(file))
    
    return zip_filename

# Define the Gradio interface
interface = gr.Interface(
    fn=process_pdf_files,
    inputs=[
        gr.Files(label="Input PDF Files", file_types=[".pdf"]),
        gr.Dropdown(label="Color-Comment Pair", choices=["Structural Slab vs Arch Slab", "Arch Slab vs Structural Slab", "Custom Option"], type="index"),
        gr.Slider(label="Tolerance", minimum=0, maximum=100, step=1, value=30),
        gr.Textbox(label="Custom Color (R,G,B)", placeholder="Enter custom color in RGB format, e.g., 255,0,0"),
        gr.Textbox(label="Custom Comment", placeholder="Enter custom comment for this color"),
        gr.Textbox(label="Custom Stroke Color (R,G,B)", placeholder="Enter stroke color in RGB format, e.g., 0,0,255")
    ],
    outputs=gr.File(label="Download Modified PDFs as ZIP"),
    title="PDF Color Region Markup"
)

# Launch the Gradio app
interface.launch()
