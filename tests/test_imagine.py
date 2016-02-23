'''
This basic test module uses live websites for checks.
For better independence mockup websites should be used.
This would be overkill for this exercise. (In my opinion)

'''
import imagine
import pytest
import requests
import os
import requests.exceptions

def test_http_to_https_conversion():
    assert imagine.get_https_url('http://www.google.de') == 'https://www.google.de'
    assert imagine.get_https_url('http://www.imgur.com/example_image.jpg') == 'https://www.imgur.com/example_image.jpg'
    assert imagine.get_https_url(
        'http://amazon.de/very/long/path/to/success.jpg') == 'https://amazon.de/very/long/path/to/success.jpg'
    # This is not what we want, but still what we currently get
    assert imagine.get_https_url('www.google.de') == 'https:///www.google.de'

def test_https_availablity():
    with requests.Session() as s:
        assert imagine.check_https_available(s, 'http://example.com')
        assert imagine.check_https_available(s, 'https://example.com')
        with pytest.raises(requests.exceptions.SSLError) as ssle:
            imagine.check_https_available(s, 'http://test.dclabs.de')
        assert imagine.check_https_available(s, 'http://test.dclabs.de', verify=False)
        assert not imagine.check_https_available(s, 'http://stuttgarter-zeitung.de')
        with pytest.raises(requests.ConnectionError) as e:
            imagine.check_https_available(s, 'http://get2gather.com')

def test_image_type_check():
    with requests.Session() as s:
        assert imagine.check_image_type(s, 'http://i.imgur.com/7Xkl7ec.gif')
        assert not imagine.check_image_type(s, 'http://i.imgur.com/')
        assert not imagine.check_image_type(s, 'http://google.com/')

def test_image_download(tmpdir):
    with requests.Session() as s:
        dest = tmpdir.mkdir('test')
        imagine.download_file(s, 'http://i.imgur.com/7Xkl7ec.gif', destination=str(dest))
        assert len(dest.listdir()) == 1
        assert os.path.getsize(str(dest.listdir()[0])) == 2052216