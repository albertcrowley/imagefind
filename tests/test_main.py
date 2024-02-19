import main
from main import scan


import os
import tempfile
from datetime import datetime
from unittest.mock import patch
from PIL import Image
import pytest
from main import scan, FileData, Database

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    file = os.path.join(tempfile.gettempdir(), 'test.db')
    db = main.Database(file)
    db.create_table()
    yield
    os.remove(os.path.join(tempfile.gettempdir(), file))

# pytest.fixture
# def temp_dir_with_images():
#     temp_dir = tempfile.mkdtemp()
#     sample_files = ['image1.jpg', 'image2.jpg', 'image3.jpg']
#     for filename in sample_files:
#         with open(os.path.join(temp_dir, filename), 'wb') as f:
#             Image.new('RGB', (100, 100)).save(f, format='JPEG')
#     yield temp_dir
#     for filename in sample_files:
#         os.remove(os.path.join(temp_dir, filename))
#     os.rmdir(temp_dir)


def test_find_image():
    print(os.getcwd())
    file = os.path.join(tempfile.gettempdir(), 'test.db')
    db = main.Database(file)
    result = main.scan('./fixtures/files', db, parallel=3)
    print(result)
    assert result['files_processed'] > 5
    assert result['files_processed'] == result['files_updated']

    find_result = main.find_file_match(db, target='./fixtures/find.jpg')
    assert len(find_result['matches']) == 2
    match1 = find_result['matches'][0]
    match2 = find_result['matches'][1]
    assert ('al-elizabeth-engagement.jpg' in match1.filename) or ('al-elizabeth-engagement.jpg' in match2.filename)
    assert ('smaller.jpg' in match1.filename) or ('smaller.jpg' in match2.filename)


# @patch('main.logger')
# @patch('main.Database')
# @patch('main.find_jpeg_files')
# def test_scan_function(mock_find_jpeg_files, mock_database, mock_logger, temp_dir_with_images):
#     temp_dir = temp_dir_with_images
#     mock_find_jpeg_files.return_value = [os.path.join(temp_dir, 'image1.jpg'), os.path.join(temp_dir, 'image2.jpg'), os.path.join(temp_dir, 'image3.jpg')]
#     mock_db_instance = mock_database.return_value
#     mock_insert_file_info = mock_db_instance.insert_file_info
#
#     result = scan(temp_dir)
#
#     assert result['files_processed'] == 3
#     assert result['run_time'] >= 0
#
#     mock_find_jpeg_files.assert_called_once_with(temp_dir)
#     assert mock_insert_file_info.call_count == 3
#
    # expected_calls = [FileData(filename=os.path.join(temp_dir, 'image1.jpg'),
    #                             size=os.path.getsize(os.path.join(temp_dir, 'image1.jpg')),
    #                             file_last_modified=datetime.fromtimestamp(os.path.getmtime(os.path.join(temp_dir, 'image1.jpg'))).strftime('%Y-%m-%d %H:%M:%S'),
    #                             phash6='mock_image_hash'),
    #                   FileData(filename=os.path.join(temp_dir, 'image2.jpg'),
    #                             size=os.path.getsize(os.path.join(temp_dir, 'image2.jpg')),
    #                             file_last_modified=datetime.fromtimestamp(os.path.getmtime(os.path.join(temp_dir, 'image2.jpg'))).strftime('%Y-%m-%d %H:%M:%S'),
    #                             phash6='mock_image_hash'),
    #                   FileData(filename=os.path.join(temp_dir, 'image3.jpg'),
    #                             size=os.path.getsize(os.path.join(temp_dir, 'image3.jpg')),
    #                             file_last_modified=datetime.fromtimestamp(os.path.getmtime(os.path.join(temp_dir, 'image3.jpg'))).strftime('%Y-%m-%d %H:%M:%S'),
    #                             phash6='mock_image_hash')]
    #
    # mock_logger.info.assert_has_calls([patch.call(x) for x in expected_calls], any_order=True)


