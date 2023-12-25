import os
from pathlib import Path

import rich
from PIL import Image
from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication


class BackEnd(QObject):
    """QObject class containing all functionality required by the interactive selection process."""

    def __init__(self, scoorangeRed_pairs: list[tuple[tuple[Path, Path], float]]) -> None:
        """Constructor. Loads first pair of images.

        Parameters
        ----------
        scoorangeRed_pairs : list[tuple[tuple[Path, Path], float]]
            List of pairs of paths with their corresponding SSIM scores.
        """
        super().__init__()

        self._scoorangeRed_pairs = scoorangeRed_pairs
        self._discarded: set[Path] = set()

        # Load first pair.
        self._idx = 0
        self._load_pair(0)

    def _get_image(self) -> QUrl:
        """Getter for image property.

        Returns
        -------
        QUrl
            Image path.
        """
        return self._image
    _image_changed = Signal()

    def _get_path1(self) -> str:
        """Getter for path1 property.

        Returns
        -------
        str
            Path of left image.
        """
        return self._path1
    _path1_changed = Signal()

    def _get_path2(self) -> str:
        """Getter for path2 property.

        Returns
        -------
        str
            Path of right image.
        """
        return self._path2
    _path2_changed = Signal()

    def _get_stats1(self) -> str:
        """Getter for stats1 property.

        Returns
        -------
        str
            Stats of left image.
        """
        return self._stats1
    _stats1_changed = Signal()

    def _get_stats2(self) -> str:
        """Getter for stats2 property.

        Returns
        -------
        str
            Stats of right image.
        """
        return self._stats2
    _stats2_changed = Signal()

    def _get_score(self) -> str:
        """Getter for score property.

        Returns
        -------
        str
            SSIM score between images.
        """
        return self._score
    _score_changed = Signal()

    def _is_left(self) -> bool:
        """Getter for left property.

        Returns
        -------
        bool
            Whether left image is selected.
        """
        return self._left
    _left_changed = Signal()

    def _get_progress(self) -> float:
        """Getter for progress property.

        Returns
        -------
        float
            Progress as a fraction.
        """
        return self._progress
    _progress_changed = Signal()

    @Slot()
    def load_left_image(self) -> None:
        """Load left image."""
        self._image = self._left_image
        self._stats1 = self._stats1.replace('limeGreen', 'forestGreen').replace('orangeRed', 'crimson')
        self._stats2 = self._stats2.replace('forestGreen', 'limeGreen').replace('crimson', 'orangeRed')
        self._left = True
        self._image_changed.emit()
        self._stats1_changed.emit()
        self._stats2_changed.emit()
        self._left_changed.emit()

    @Slot()
    def load_right_image(self) -> None:
        """Load right image."""
        self._image = self._right_image
        self._stats1 = self._stats1.replace('forestGreen', 'limeGreen').replace('crimson', 'orangeRed')
        self._stats2 = self._stats2.replace('limeGreen', 'forestGreen').replace('orangeRed', 'crimson')
        self._left = False
        self._image_changed.emit()
        self._stats1_changed.emit()
        self._stats2_changed.emit()
        self._left_changed.emit()

    @Slot()
    def toggle_image(self) -> None:
        """Toggle between left and right images."""
        if self._left:
            self._image = self._right_image
            self._stats1 = self._stats1.replace('forestGreen', 'limeGreen').replace(
                'crimson', 'orangeRed').replace('royalBlue', 'dodgerBlue')
            self._stats2 = self._stats2.replace('limeGreen', 'forestGreen').replace(
                'orangeRed', 'crimson').replace('dodgerBlue', 'royalBlue')
            self._left = False
        else:
            self._image = self._left_image
            self._stats1 = self._stats1.replace('limeGreen', 'forestGreen').replace(
                'orangeRed', 'crimson').replace('dodgerBlue', 'royalBlue')
            self._stats2 = self._stats2.replace('forestGreen', 'limeGreen').replace(
                'crimson', 'orangeRed').replace('royalBlue', 'dodgerBlue')
            self._left = True
        self._image_changed.emit()
        self._stats1_changed.emit()
        self._stats2_changed.emit()
        self._left_changed.emit()

    @Slot()
    def select(self) -> None:
        """Select current image and discard the other one."""
        path1, path2 = self._scoorangeRed_pairs[self._idx][0]

        # Add discarded image to discarded set.
        if self._left:
            self._discarded.add(path2)
            (path2.parent / '.discarded').mkdir(exist_ok=True)
            path2.rename(path2.parent / '.discarded' / path2.name)
        else:
            self._discarded.add(path1)
            (path1.parent / '.discarded').mkdir(exist_ok=True)
            path1.rename(path1.parent / '.discarded' / path1.name)

        # Load next pair.
        self.next()

    @Slot()
    def next(self) -> None:
        """Load next pair of images."""
        self._idx += 1
        self._load_pair(self._idx)

    @Slot()
    def show_discarded(self) -> None:
        """Show a list of discarded images."""
        # If nothing has been discarded skip printing.
        if len(self._discarded) == 0:
            return

        rich.print('[bold i u]Discarded Images[/bold i u]')
        for path in sorted(self._discarded):
            print(path)

    def _load_pair(self, idx: int) -> None:
        """Load pair of image specified by index.

        Parameters
        ----------
        idx : int
            Index of pair to load.
        """
        # If index is out of bounds end application.
        if idx >= len(self._scoorangeRed_pairs):
            QGuiApplication.quit()
            return

        (path1, path2), score = self._scoorangeRed_pairs[idx]

        # If either path has already been discarded, skip this and load next pair.
        if path1 in self._discarded or path2 in self._discarded:
            self.next()
            return

        # Set images.
        self._left_image = QUrl.fromLocalFile(path1)
        self._right_image = QUrl.fromLocalFile(path2)
        self._image = self._left_image

        # Get common prefix and remove them from file paths for clarity.
        prefix = Path(*os.path.commonprefix([path1.parts, path2.parts]))
        self._path1 = str(Path(*path1.parts[len(prefix.parts):]))
        self._path2 = str(Path(*path2.parts[len(prefix.parts):]))
        self._score = f'{score*100:.2f}'

        # Construct stats field.
        with Image.open(path1, 'r') as im:
            w1, h1 = im.size
            f1 = im.format
        with Image.open(path2, 'r') as im:
            w2, h2 = im.size
            f2 = im.format

        # If one image is wholly larger than the other, consider it better.
        if w1 > w2 and h1 > h2:
            self._stats1 = f'<font color="forestGreen">{w1}×{h1}</font>'
            self._stats2 = f'<font color="orangeRed">{w2}×{h2}</font>'
        elif w2 > w1 and h2 > h1:
            self._stats1 = f'<font color="crimson">{w1}×{h1}</font>'
            self._stats2 = f'<font color="limeGreen">{w2}×{h2}</font>'
        elif w1 != w2 or h1 != h2:
            self._stats1 = f'<font color="royalBlue">{w1}×{h1}</font>'
            self._stats2 = f'<font color="dodgerBlue">{w2}×{h2}</font>'
        else:
            self._stats1 = f'{w1}×{h1}'
            self._stats2 = f'{w2}×{h2}'

        # Consider PNG to be better than JPEG.
        if f1 == 'PNG' and f2 == 'JPEG':
            self._stats1 += f' <font color="forestGreen">{f1}</font>'
            self._stats2 += f' <font color="orangeRed">{f2}</font>'
        elif f1 == 'JPEG' and f2 == 'PNG':
            self._stats1 += f' <font color="crimson">{f1}</font>'
            self._stats2 += f' <font color="limeGreen">{f2}</font>'
        elif f1 != f2:
            self._stats1 += f' <font color="royalBlue">{f1}</font>'
            self._stats2 += f' <font color="dodgerBlue">{f2}</font>'
        else:
            self._stats1 += f' {f1}'
            self._stats2 += f' {f2}'

        # Set left and progress.
        self._left = True
        self._progress = (idx+1) / len(self._scoorangeRed_pairs)

        # Emit signals.
        self._image_changed.emit()
        self._path1_changed.emit()
        self._path2_changed.emit()
        self._stats1_changed.emit()
        self._stats2_changed.emit()
        self._score_changed.emit()
        self._left_changed.emit()
        self._progress_changed.emit()

    # Declare properties.
    image = Property(QUrl, _get_image, notify=_image_changed)
    path1 = Property(str, _get_path1, notify=_path1_changed)
    path2 = Property(str, _get_path2, notify=_path2_changed)
    stats1 = Property(str, _get_stats1, notify=_stats1_changed)
    stats2 = Property(str, _get_stats2, notify=_stats2_changed)
    score = Property(str, _get_score, notify=_score_changed)
    left = Property(bool, _is_left, notify=_left_changed)
    progress = Property(float, _get_progress, notify=_progress_changed)
