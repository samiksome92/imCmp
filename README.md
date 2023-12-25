# imCmp

A small application to compare images with each other interactively, while keeping some and discarding others. Compares among images in a directory or across directories using structural similarity and starts an interactive selection session starting with most similar pairs found. Discarded images are moved inside a `.discarded` directory within its original parent.

## Requirements
- `numpy`
- `opencv-python`
- `Pillow`
- `PySide6`
- `rich`
- `scikit-image`

## Usage
    main.py [-h] [-x] [-t TOLERANCE] [-r RESOLUTION] dirs [dirs ...]

positional arguments:

    dirs                  Directories to compare

options:

    -h, --help            show this help message and exit
    -x, --cross           Only cross compare across directories
    -t TOLERANCE, --tolerance TOLERANCE
                          Aspect ratio tolerance
    -r RESOLUTION, --resolution RESOLUTION
                          Resolution at which to compute SSIM

If `--cross` is specified images within the same directory are not considered for comparison. Image pairs whose aspect ratios differ less than `--tolerance` are also skipped. Default tolerance is `0.1`. `--resolution` specifies the resolution at which structural similarity is computed. Images are resized with their largest edge matching this value before comparison. Default value is `100`, higher resolutions result in slower computation.

Once the interactive session is started. A screen as shown below is presented.
![](example/imCmp%20Screenshot.png)
(Image courtesy of [Unsplash](https://unsplash.com/))

The status bar at the bottom shows which image is currently selected, what is the resolution, format and the similarity score. Pressing `SPACE` toggles between the two images, `ENTER` selects an image to keep, while discarding the other and `N` skips this pair and continues to the next. A very thin progress bar (in green) is also shown at the very bottom.

The resolution and format may be highlighted in green or red indicating that one is better or worse than the other (Larger images are considered better than smaller ones and PNGs and considered better than JPEGs). It may also be highlighted in blue which indicates that the images have differing resolution/format but neither is strictly better than the other.