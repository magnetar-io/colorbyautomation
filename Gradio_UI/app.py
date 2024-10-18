# @title Default title text
import fitz  # PyMuPDF
import os

# Helper function to find color areas
def find_color_areas(page, target_color, tolerance=30):
    # Render page as a pixmap (image), this will allow us to inspect pixels for colors
    pix = page.get_pixmap()
    width, height = pix.width, pix.height
    visited = [[False for _ in range(width)] for _ in range(height)]
    rectangles = []

    def flood_fill(x, y):
        """Flood fill to find all adjacent pixels of the same color."""
        stack = [(x, y)]
        rects = []

        while stack:
            cx, cy = stack.pop()
            if visited[cy][cx]:
                continue

            visited[cy][cx] = True
            pixel_color = pix.pixel(cx, cy)
            r, g, b = pixel_color[:3]  # Extract RGB values

            if (abs(r - target_color[0]) <= tolerance and
                abs(g - target_color[1]) <= tolerance and
                abs(b - target_color[2]) <= tolerance):
                rects.append(fitz.Rect(cx, cy, cx + 1, cy + 1))

                # Add neighbors to stack
                if cx > 0:
                    stack.append((cx - 1, cy))
                if cx < width - 1:
                    stack.append((cx + 1, cy))
                if cy > 0:
                    stack.append((cx, cy - 1))
                if cy < height - 1:
                    stack.append((cx, cy + 1))

        if rects:
            # Merge all small rectangles into one bounding box (no buffer)
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

# Helper function to merge overlapping rectangles
def merge_overlapping_rectangles(rectangles):
    """Merge rectangles that overlap each other."""
    merged_rects = []

    while rectangles:
        rect = rectangles.pop(0)
        to_merge = [rect]

        for other in rectangles[:]:
            if rect.intersects(other):  # Check for overlap
                to_merge.append(other)
                rectangles.remove(other)

        # Merge all rectangles in the 'to_merge' list
        merged_rect = fitz.Rect(
            min([r.x0 for r in to_merge]),
            min([r.y0 for r in to_merge]),
            max([r.x1 for r in to_merge]),
            max([r.y1 for r in to_merge])
        )
        merged_rects.append(merged_rect)

    return merged_rects

# Function to markup the PDF with rectangles and annotations for multiple colors
def markup_color_regions(input_pdf_path, color_comment_pairs, output_pdf_path, tolerance=30):
    # Open the PDF
    doc = fitz.open(input_pdf_path)

    # Process the first page
    page = doc[0]

    for color_info in color_comment_pairs:
        target_color = color_info['color']
        comment = color_info['comment']
        stroke_color = color_info['stroke_color']

        # Find all regions matching the color
        rectangles = find_color_areas(page, target_color, tolerance)

        if rectangles:
            # Merge overlapping rectangles
            merged_rectangles = merge_overlapping_rectangles(rectangles)

            for bbox in merged_rectangles:
                # Add a rectangular annotation (with comment) around each found area
                annot = page.add_rect_annot(bbox)  # Create a rectangle annotation
                annot.set_colors(stroke=stroke_color)  # Set stroke color
                annot.set_border(width=2)  # Set the border width to 2pt
                annot.set_info({"title": "Markup", "content": comment})
                annot.update()

    # Save the modified PDF to a different file to avoid overwrite
    if input_pdf_path == output_pdf_path:
        output_pdf_path = input_pdf_path.replace('.pdf', '_modified.pdf')

    doc.save(output_pdf_path)
    doc.close()
    print(f"PDF saved with markup and comments at: {output_pdf_path}")

# Main function
if __name__ == "__main__":
    # Specify input and output PDF paths
    input_pdf = "/content/LEVEL 01 - Color Coordiation Floors-.pdf"  # Input PDF path
    output_pdf = os.path.join(os.path.dirname(input_pdf), "Slab vs Slab.pdf")  # Output PDF path

    # Define the colors and corresponding comments
    color_comment_pairs = [
        {
            "color": (235, 128, 138),  # Target color (RGB)
            "comment": "Structural Slab greater than architectural slab",  # Comment
            "stroke_color": (1, 0, 0)  # Red stroke color
        },
        {
            "color": (128, 253, 128),  # Second target color (RGB)
            "comment": "Arch Slab greater then Structure",  # Second comment
            "stroke_color": (0, 1, 0)  # Green stroke color
        }
    ]

    # Call the function to markup the regions with multiple colors and comments
    markup_color_regions(input_pdf, color_comment_pairs, output_pdf, tolerance=30)
