import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import zipfile
import tarfile
import tempfile
import shutil
import unittest

import getfile

class DownloadTest(unittest.TestCase):

    def create_sample_text_file(self):
        """Create a basic text file for use in archives."""
        path = os.path.join(self.temp_dir, self.sample_name)
        with open(path, 'w') as f:
            f.write("sample data")
        return path

    def setUp(self):
        # test data
        self.remote_zip = r'http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_tiny_countries.zip'

        # temporary workspace
        self.temp_dir = tempfile.mkdtemp()
        self.sample_name = 'sample.txt'
        self.sample_path = os.path.join(self.temp_dir, self.sample_name)

        # create a bunch of compressed files for testing decompression
        sample_file = self.create_sample_text_file()
        with tarfile.TarFile(os.path.join(self.temp_dir, 'sample.tar'), 'w') as tar:
            tar.add(sample_file, arcname=self.sample_name)
        with zipfile.ZipFile(os.path.join(self.temp_dir, 'sample.zip'), 'w') as z:
            z.write(sample_file, self.sample_name)
        # remove the sample text file to properly test extraction
        os.unlink(sample_file)

    def tearDown(self):
        """Delete all the test data."""
        shutil.rmtree(self.temp_dir, True)

    def test_download(self):
        """Attempt to download a remote file."""
        test_file = getfile.download_file(self.remote_zip, self.temp_dir)
        self.assertTrue(os.path.exists(test_file))

    def test_decompress_zip(self):
        archive = os.path.join(self.temp_dir,'sample.zip')
        self.assertTrue(getfile.decompress(archive, self.temp_dir))
        self.assertTrue(os.path.exists(self.sample_path))

    def test_decompress_tar(self):
        archive = os.path.join(self.temp_dir,'sample.tar')
        self.assertTrue(getfile.decompress(archive, self.temp_dir))
        self.assertTrue(os.path.exists(self.sample_path))

if __name__ == '__main__':
    unittest.main()
