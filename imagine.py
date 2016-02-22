import logging
import logging.config
import os.path
import shutil
import sys
from urllib.parse import urlparse, urlunparse

import click
import requests

logger = logging.getLogger(__name__)


def get_https_url(url):
    '''
    Replace whatever protocol we currently have with HTTPS.

    :param url: Source URL
    :return: Source URL with HTTPS as protocol
    '''
    parse_result = list(urlparse(url))
    parse_result[0] = 'https'
    return urlunparse(parse_result)


def check_https_available(session, url, verify):
    '''
    Make a HEAD call against the URL to see if the server supports HTTPS.
    Wait for some seconds before failing.

    :param session: The requests session or object
    :param url: The URL to be called
    :param verify: Verify the HTTPS certificate
    :return: The new HTTPS URL or False if failing
    '''
    try:
        response = session.head(get_https_url(url), verify=verify, allow_redirects=True, timeout=(1.0, 5.0))
        return response.url
    except requests.ConnectionError as e:
        return False
    except requests.URLRequired as e:
        logger.warning()


def check_image_type(session, url, verify=True):
    '''
    Make a HEAD HTTP request and see if the content-type send by the server is image/*

    :param session: The requests session or object
    :param url: The URL to be called
    :param verify: Verify the HTTPS certificate
    :return: True if content-type is a image, false if not
    '''
    response = session.head(url, verify=verify)
    return "image/" in response.headers.get('content-type', '')


def download_file(session, url, destination, verify=True):
    '''
    Download the image and save it to disk.

    :param session: The requests session or object
    :param url: The URL to be called
    :param verify: Verify the HTTPS certificate
    :param destination: Destination file path to save the image to.
    '''
    response = session.get(url,
                           verify=verify,
                           stream=True)
    with open(os.path.join(destination, os.path.basename(url)), 'w+b') as image_file:
        shutil.copyfileobj(response.raw, image_file)


@click.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.option('--ignore-cert', is_flag=True, help="Don't check certificate validity")
@click.option('--ignore-content-type', is_flag=True, help="Don't check for image/* content-type")
@click.option('--destination', '-d', type=click.Path(exists=True, file_okay=False, resolve_path=True, writable=True),
              default=os.getcwd(), help="Save images to this directory, defaults to CWD")
def main(filename, ignore_cert, ignore_content_type, destination):
    if os.environ.get("IMAGINE_LOGGING", None):
        logging.config.fileConfig(os.environ.get("IMAGINE_LOGGING"))
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    with open(filename, 'r') as url_list:
        for image_url in url_list:
            with requests.Session() as sess:
                image_url = image_url.strip()
                https_url = check_https_available(session=sess, url=image_url, verify=(not ignore_cert))

                if https_url:
                    image_url = https_url

                content_type_check = True if ignore_content_type \
                    else check_image_type(session=sess, url=image_url, verify=(not ignore_cert))

                if content_type_check:
                    download_file(session=sess, url=image_url, verify=(not ignore_cert), destination=destination)
                else:
                    logger.warning("Non image content-type detected. "
                                   "Will skip download for: {url}".format(url=image_url))


if __name__ == '__main__':
    main()
