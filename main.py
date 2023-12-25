import argparse
import itertools
import sys
from pathlib import Path

import cv2
import numpy as np
import skimage.metrics
from PIL import Image
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn

from backend import BackEnd

IMAGE_EXTENSIONS = ['.jpg', '.png', '.gif', '.webp']


def get_images(dirs: list[Path]) -> list[Path]:
    """Retrieve a list of all images across directories using extensions for filtering.

    Parameters
    ----------
    dirs : list[Path]
        List of directories.

    Returns
    -------
    images : list[list[Path]]
        List of images found.
    """
    images: list[Path] = []
    for dir in dirs:
        # Only keep files which end with pre-defined extensions.
        images += sorted([f for f in dir.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS])

    return images


def get_pairs(images: list[Path], cross: bool = False, tolerance: float = 0.1) -> list[tuple[Path, Path]]:
    """Generate pairs of images to compare.

    If cross is specified images from the same directory are not compared; only images across directories are compared.
    Images are also skipped from comparison if difference between their aspect ratios is greater than provided tolerance
    value.

    Parameters
    ----------
    images : list[Path]
        List of images to compare.
    cross : bool, optional
        If True cross compare across directories. (default=False)
    tolerance : float, optional
        Aspect ratio tolerance. (default=0.1)

    Returns
    -------
    pairs : list[tuple[Path, Path]]
        List of pair of images to compare.
    """
    pairs: list[tuple[Path, Path]] = []
    ar_cache: dict[Path, float] = {}
    for path1, path2 in itertools.combinations(images, 2):
        # If cross is specified do not compare images from the same directory.
        if cross and path1.parent == path2.parent:
            continue

        # If not seen earlier compute aspect ratio and store it.
        if path1 not in ar_cache:
            with Image.open(path1, 'r') as im:
                ar_cache[path1] = im.size[0] / im.size[1]
        if path2 not in ar_cache:
            with Image.open(path2, 'r') as im:
                ar_cache[path2] = im.size[0] / im.size[1]

        # Check if difference between aspect ratios is within tolerance level.
        if abs(ar_cache[path1] - ar_cache[path2]) > tolerance:
            continue

        pairs.append((path1, path2))

    return pairs


def similarity(path1: Path, path2: Path, resolution: int = 100) -> float:
    """Compute structural similarity between two images.

    Parameters
    ----------
    path1 : Path
        Path to first image.
    path2 : Path
        Path to second image.
    resolution : int, optional
        Resolution at which to compute SSIM. (default=100)

    Returns
    -------
    score : float
        Computed SSIM score.
    """
    # Read images (via numpy to support unicode paths) and convert to grayscale.
    im1 = np.fromfile(path1, dtype=np.uint8)
    im2 = np.fromfile(path2, dtype=np.uint8)
    im1 = cv2.imdecode(im1, cv2.IMREAD_GRAYSCALE)
    im2 = cv2.imdecode(im2, cv2.IMREAD_GRAYSCALE)

    # Compuate average aspect ratio.
    h1, w1 = im1.shape
    h2, w2 = im2.shape
    avg_ar = (w1 / h1 + w2 / h2) / 2

    # Calculate resized width and height
    if avg_ar < 1:
        w = int(resolution * avg_ar)
        h = resolution
    else:
        w = resolution
        h = int(resolution / avg_ar)

    # Resize images and compute structural similarity score.
    im1 = cv2.resize(im1, (w, h))
    im2 = cv2.resize(im2, (w, h))
    score = skimage.metrics.structural_similarity(im1, im2)

    return score


def main() -> None:
    """Main function for script."""
    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('dirs', help='Directories to compare', nargs='+')
    parser.add_argument('-x', '--cross', help='Only cross compare across directories', action='store_true')
    parser.add_argument('-t', '--tolerance', help='Aspect ratio tolerance', type=float, default=0.1)
    parser.add_argument('-r', '--resolution', help='Resolution at which to compute SSIM', type=int, default=100)
    args = parser.parse_args()

    # Cross comparison cannot be done without two directories.
    if args.cross and len(args.dirs) < 2:
        print('Cross comparison requires at least two directories.')
        sys.exit(-1)

    # Convert directories to paths and get list of images.
    dirs = [Path(d) for d in args.dirs]
    images = get_images(dirs)

    # Generate pairs of images for comparison.
    pairs = get_pairs(images, args.cross, args.tolerance)

    # Compute similarity between pairs.
    with Progress(
        TextColumn('[progress.description]{task.description}'),
        BarColumn(),
        MofNCompleteColumn(),
    ) as pbar:
        task = pbar.add_task('Computing SSIM', total=len(pairs))

        scores: list[float] = []
        for p1, p2 in pairs:
            scores.append(similarity(p1, p2, args.resolution))
            pbar.update(task, advance=1)

    # Sort by scores and start interactive selection.
    scored_pairs = sorted(zip(pairs, scores), key=lambda x: x[1], reverse=True)

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    backend = BackEnd(scored_pairs)
    engine.rootContext().setContextProperty("backEnd", backend)

    qml_file = Path(__file__).parent / 'Main.qml'
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)
    app.exec()
    del engine


if __name__ == '__main__':
    main()
