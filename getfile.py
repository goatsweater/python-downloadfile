from __future__ import print_function, absolute_import
import sys
import logging
import argparse
import os
import zipfile
import tarfile

try:
    from urllib.request import urlopen, URLError
except:
    from urllib2 import urlopen, URLError

# set up the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# log formatting
formatter = logging.Formatter('%(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# inputs come from positional command line arguments
parser = argparse.ArgumentParser(description='Download a remote file.')
parser.add_argument('url', help='url to the remote file')
parser.add_argument('dest', help='path to save directory')
parser.add_argument('-e', '--expand', action='store_true', dest='decompress', help='automatically decompress archives')

def decompress(source, dest):
    """Decompress an archive into a destination folder."""
    success = False
    # do we recognize the extension?
    compressed_extensions = ('.zip', '.gz', '.bz2', '.tgz', '.tbz', '.tar')
    root, ext = os.path.splitext(local_file)

    # check if we know how to handle this file
    if ext in compressed_extensions:
        logger.debug("Checking archive integrity")
        # detect and handle the archive
        # TODO: Implement support for bz2 and gz files that aren't tar archives
        if zipfile.is_zipfile(source):
            success = decompress_zipfile(source, dest)
        elif tarfile.is_tarfile(source):
            success = decompress_tarfile(source, dest)
        else:
            logger.info("Incompatible archive format.")

        # remove the archive on success
        if success:
            logger.info("Decompress successful, removing archive.")
            os.unlink(source)
    else:
        logger.info("Invalid archive extension. Extension must be one of {0}".format(compressed_extensions.join(', ')))

    return success

def decompress_zipfile(source, dest):
    """Decompress a zip archive."""
    logger.info("Decompressing zip archive")

    with zipfile.ZipFile(source, 'r') as archive:
        archive.extractall(dest)

    return True

def decompress_tarfile(source, dest):
    """Decompress a tar archive, with optional compression applied."""
    logger.info("Decompressing tar archive")
    with tarfile.TarFile(source, 'r') as archive:
        archive.extractall(dest)

    return True

def download_file(source, dest):
    """Attempt to download a file to the destination."""
    # determine the file name
    fname = os.path.basename(source)
    local_path = os.path.join(dest, fname)

    try:
        logger.info("Downloading {0}".format(source))
        response = urlopen(source)
        with open(local_path, 'w') as dl:
            logger.debug("Writing local file {0}".format(local_path))
            dl.write(response.read())
    except URLError as err:
        logging.error(err.reason)
        local_path = None

    # let the caller know we are done
    logger.info("{0} downloaded to {1}".format(fname, dest))
    return local_path

# mainline
if __name__ == '__main__':
    args = parser.parse_args()

    # ensure the destination exists
    if not os.path.isdir(args.dest):
        logger.error("Invalid destination directory: %s" % args.dest)
        raise ValueError("Invalid destination directory")

    # very basic check to ensure a valid url was passed in
    # TODO: this should be a more robust check
    url_parts = args.url.split('://')
    if not len(url_parts) > 1:
        logger.error("Invalid remote file URL")
        raise ValueError("Invalid source URL")

    # attempt to download the file
    local_file = download_file(args.url, args.dest)

    # attempt to decompress if desired
    if args.decompress:
        logger.debug("Attempting to decompress downloaded file")
        decompress(local_file, args.dest)
