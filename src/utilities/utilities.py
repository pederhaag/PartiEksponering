from pathlib import Path
from PIL import Image
import numpy as np

def make_mask(picture):
    file = Path(__file__).resolve()
    source_folder = str(file.parents[0]) + "\\partylogos\\"
    source_image = np.array(Image.open(source_folder + picture +".png").convert("L"))

    # Transformation
    mask = np.ndarray((source_image.shape[0],source_image.shape[1]), dtype=np.uint8)
    for r, row in enumerate(source_image):
        transform = lambda x: 255 if x >= 200 else 0
        mask[r] = np.array([transform(x) for x in row])
    
    return mask

if __name__ == "__main__":
    mask = make_mask("V")
    img = Image.fromarray(mask)
    img.show()