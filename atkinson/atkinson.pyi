from typing import SupportsIndex


def atk(w: SupportsIndex, h: SupportsIndex, pixels: bytes, /) -> bytes:
    """
    Dither an image using Atkinson dithering algorithm

    Args:
        w (SupportsIndex): Width of the image
        h (SupportsIndex): Height of the image
        pixels (bytes): Raw grayscale pixel data as bytes

    Returns:
        image_bytes (bytes): Dithered image as bytes
    """
    
    ...
