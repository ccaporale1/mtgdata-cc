import os

import numpy as np
from tqdm import tqdm

from mtgml.scryfall import ScryfallDataset


# ========================================================================= #
# Transform                                                                 #
# ========================================================================= #


class PilResizeNumpyTransform(object):
    def __init__(self, resize=None, assert_shape=None, assert_dtype=None, transpose=True):
        self._resize = resize  # H, W
        self._assert_shape = assert_shape  # H, W, C
        self._assert_dtype = assert_dtype
        self._transpose = transpose

    def __call__(self, img):
        # resize
        if self._resize is not None:
            img = img.resize(self._resize[::-1])
        # convert to numpy
        img = np.array(img)
        if self._assert_shape is not None: assert img.shape == self._assert_shape
        if self._assert_dtype is not None: assert img.dtype == self._assert_dtype
        # transpose
        if self._transpose:
            img = np.moveaxis(img, -1, -3)
        # return values
        return img


# ========================================================================= #
# RESAVE                                                                    #
# ========================================================================= #


def make_dataset(bulk_type: str, img_type: str, resize=None, transpose=True, data_root=None, force_update=False, download_threads=64):
    data = ScryfallDataset(
        data_root=data_root,
        transform=PilResizeNumpyTransform(
            resize=resize,
            assert_dtype='uint8',
            assert_shape=ScryfallDataset.IMG_SHAPES[img_type] if (resize is None) else (*resize, 3),
            transpose=transpose,
        ),
        resize_incorrect=(resize is None),
        bulk_type=bulk_type,
        img_type=img_type,
        force_update=force_update,
        download_threads=download_threads,
    )
    return data


def resave_dataset(data: ScryfallDataset, suffix='', batch_size=64, num_workers=os.cpu_count(), img_shape=None, overwrite=False):
    """
    Re-save the given Scryfall dataset as an HDF5 file.
    - the hdf5 file will have the key `data`
    """
    import h5py
    from torch.utils.data import DataLoader
    # defaults
    if suffix is None:
        suffix = ''
    if img_shape is None:
        img_shape = data.img_shape
    path = f'data/mtg-{data.bulk_type}-{data.img_type}{suffix}.h5'
    # skip if exists
    if not overwrite:
        if os.path.exists(path):
            return path
    # open file
    with h5py.File(path, 'w', libver='earliest') as f:
        # create new dataset
        d = f.create_dataset(
            name='data',
            shape=(len(data), *img_shape),
            dtype='uint8',
            chunks=(1, *img_shape),
            compression='gzip',
            compression_opts=4,
            # non-deterministic time stamps are added to the file if this is not
            # disabled, resulting in different hash sums when the file is re-generated!
            # https://github.com/h5py/h5py/issues/225
            track_times=False,
        )
        # dataloader
        dataloader = DataLoader(data, batch_size=batch_size, num_workers=num_workers, shuffle=False, drop_last=False)
        # save data
        with tqdm(desc=f'Converting: {os.path.basename(path)}', total=len(data)) as p:
            for i, batch in enumerate(dataloader):
                d[i*batch_size:(i+1)*batch_size] = batch
                p.update(len(batch))
    # done
    return path


# ========================================================================= #
# RESAVE                                                                    #
# ========================================================================= #


# sane modes that won't use too much disk space
SANE_MODES = {
    ('all_cards', 'small'),            # ~243280 cards ~3GB
    ('default_cards', 'small'),        # ~60459 cards ~0.75GB
    ('default_cards', 'normal'),       # ~60459 cards
    ('default_cards', 'border_crop'),  # ~60459 cards
}


# ========================================================================= #
# Entry Points                                                              #
# ========================================================================= #


# ORIGINAL ASPECT RATIOS:
# 'small':       (204,  146, 3),    # ASPECT: 1,397260274  | PRIME FACTORS: 2*2*3*17, 2*73         | GCF: 2
# 'border_crop': (680,  480, 3),    # ASPECT: 1,4166666667 | PRIME FACTORS: 2**3*5*17, 2**5*3*5    | GCF: 2**4
# 'normal':      (680,  488, 3),    # ASPECT: 1,393442623  | PRIME FACTORS: 2**3*5*17, 2**3*61     | GCF: 2**3
# 'large':       (936,  672, 3),    # ASPECT: 1,3928571429 | PRIME FACTORS: 2**3*3**2*13, 2**5*3*7 | GCF: 2**3*3
# 'png':         (1040, 745, 3),    # ASPECT: 1,3959731544 | PRIME FACTORS: 2**4*5*13, 5*149       | GCF: 5

# RESIZED ASPECT RATIOS
# (192, 128)  # ASPECT: 1.5 | PRIME FACTORS: 3*2**6, 2*2**6 | GCF: 2**6 | AREA:  24576
# (112, 80)   # ASPECT: 1.4 | PRIME FACTORS: 7*2**4, 5*2**4 | GCF: 2**4 | AREA:   8960
# (224, 160)  # ASPECT: 1.4 | PRIME FACTORS: 7*2**5, 5*2**5 | GCF: 2**5 | AREA:  35840
# (448, 320)  # ASPECT: 1.4 | PRIME FACTORS: 7*2**6, 5*2**6 | GCF: 2**6 | AREA: 143360

# SPEED TESTS:
# default_small  - inp: 599.10it/s  ~0.9GB
# default_small  - out: 1528.33it/s ~5.7GB
# default_normal - inp: 81.19it/s   ~7.1GB
# default_normal - out: 1769.92it/s ~5.2GB


if __name__ == '__main__':
    import argparse
    import logging
    from mtgml.scryfall import _data_dir
    from mtgml.util.hdf5 import PickleH5pyFile

    # parse arguments
    parser = argparse.ArgumentParser()
    # these should match scryfall.py
    parser.add_argument('-b', '--bulk_type', type=str, default='default_cards')
    parser.add_argument('-i', '--img-type', type=str, default='normal')
    parser.add_argument('-d', '--data-root', type=str, default=_data_dir(None, None))
    parser.add_argument('-f', '--force-download', action='store_true')
    parser.add_argument('-t', '--download_threads', type=int, default=os.cpu_count() * 2)
    # extra args
    parser.add_argument('-s', '--size', type=str, default='224x160')
    parser.add_argument('-c', '--channels-first', action='store_true')
    parser.add_argument('--num-workers', type=int, default=os.cpu_count())
    parser.add_argument('--batch-size', type=int, default=128)
    parser.add_argument('--no-test', action='store_false')
    parser.add_argument('--suffix', type=str, default='')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()

    # update args
    try:
        args.height, args.width = (int(v) for v in args.size.split('x'))
    except:
        raise ValueError(f'invalid size argument: {repr(args.size)}, must be of format: "<height>x<width>", eg. "224x160"')

    # check args
    if args.height / args.width != 1.4:
        logging.warning(f'Aspect ratio of height/width is not 1.4, given: {args.size} which gives {args.height/args.width}')
    if (args.bulk_type, args.img_type) not in SANE_MODES:
        logging.warning(f'Current combination of bulk and image types might generate a lot of data: {(args.bulk_type, args.img_type)} consider instead one of: {sorted(SANE_MODES)}')

    # download the dataset
    logging.basicConfig(level=logging.INFO)
    _data = make_dataset(
        bulk_type=args.bulk_type,
        img_type=args.img_type,
        data_root=args.data_root,
        force_update=args.force_download,
        download_threads=args.download_threads,
        # extra
        resize=(args.height, args.width),
        transpose=args.channels_first,
    )

    # check sizes
    if (args.height > _data.img_shape[0]) or (args.width > _data.img_shape[1]):
        logging.warning(f'images are being unscaled from input size of: {_data.img_shape[:2]} to: {(args.height, args.width)}')

    # convert the dataset
    _path = resave_dataset(
        _data,
        suffix=f'-3x{args.size}{args.suffix}' if args.channels_first else f'-{args.size}x3{args.suffix}',
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        img_shape=(3, args.height, args.width) if args.channels_first else (args.height, args.width, 3),
        overwrite=args.overwrite,
    )

    # test the datasets
    if not args.no_test:
        _hdat = PickleH5pyFile(_path, 'data')
        for i in tqdm(range(1500), desc='inp test'): item = _data[i]
        for i in tqdm(range(10000), desc='out test'): item = _hdat[i]
