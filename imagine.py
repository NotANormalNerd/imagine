'''

'''

import logging
import logging.config
import os.path
import shutil
import sys
import uuid
from urllib.parse import urlparse, urlunparse

import click
import requests
import requests.exceptions

logger = logging.getLogger(__name__)


def get_https_url(url):
    '''
    Replace whatever protocol we currently have with HTTPS.

    :param url: Source URL
    :return: Source URL with HTTPS as protocol
    '''
    parse_result = list(urlparse(url))
    logger.debug("URLPARSE Result: {}".format(parse_result))
    parse_result[0] = 'https'
    return urlunparse(parse_result)


def check_https_available(session, url, verify=True):
    '''
    Make a HEAD call against the URL to see if the server supports HTTPS.
    Wait for some seconds before failing.
    Check if server is available for http if https fails.
    Raises requests.ConnectionError if no server is available.

    :param session: The requests session or object
    :param url: The URL to be called
    :param verify: Verify the HTTPS certificate
    :return: The new HTTPS URL or False if failing
    '''
    try:
        response = session.head(get_https_url(url), verify=verify, allow_redirects=True, timeout=(1.0, 5.0))
        return response.url
    except requests.ConnectionError as e:
        session.head(url, verify=verify, allow_redirects=True, timeout=(1.0,5.0))
        return False


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
    Does not overwrite existing images by prefixing image names.

    :param session: The requests session or object
    :param url: The URL to be called
    :param verify: Verify the HTTPS certificate
    :param destination: Destination file path to save the image to.
    '''
    response = session.get(url,
                           verify=verify,
                           stream=True)
    unique_filename = "-".join((uuid.uuid4().hex[:6], os.path.basename(url)))
    with open(os.path.join(destination, unique_filename), 'w+b') as image_file:
        shutil.copyfileobj(response.raw, image_file)
    logger.info("Successfully downloaded image to {}".format(os.path.join(destination, unique_filename)))


@click.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.option('--ignore-cert', is_flag=True, help="Don't check certificate validity")
@click.option('--ignore-content-type', is_flag=True, help="Don't check for image/* content-type")
@click.option('--destination', '-d', type=click.Path(exists=True, file_okay=False, resolve_path=True, writable=True),
              default=os.getcwd(), help="Save images to this directory, defaults to CWD")
@click.option('--dry-run', is_flag=True, help="Don't download any images. Just check for availability.")
def main(filename, ignore_cert, ignore_content_type, destination, dry_run):
    '''
    This was not written in TDD style development. Test have been added after the code has been basically finished.

    First we check if we can use https (yay security), then we check if the server at least tries to sell us images.
    At last we download the content of the url from the server and put it into the destination folder.
    '''
    if os.environ.get("IMAGINE_LOGGING", None):
        logging.config.fileConfig(os.environ.get("IMAGINE_LOGGING"))
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    with open(filename, 'r') as url_list:
        for image_url in url_list:
            with requests.Session() as sess:
                image_url = image_url.strip()

                try:
                    https_url = check_https_available(session=sess, url=image_url, verify=(not ignore_cert))

                    if https_url:
                        image_url = https_url

                    content_type_check = True if ignore_content_type \
                        else check_image_type(session=sess, url=image_url, verify=(not ignore_cert))
                except requests.ConnectionError as e:
                    logger.warning("Server was not found. Will skip download for: {url}".format(url=image_url))
                    continue
                except requests.exceptions.InvalidURL as e:
                    logger.warning("Invalid URL was encountered: {url} "
                                   "URL must be in format http(s)://domain.tld/path_to_image". format(url=image_url))
                    continue


                if content_type_check and not dry_run:
                    try:
                        download_file(session=sess, url=image_url, verify=(not ignore_cert), destination=destination)
                    except requests.ConnectionError as e:
                        logger.warning("Something went wrong while downloading the file. "
                                       "Will skip download for: {url} "
                                       "Reason: {reason}".format(url=image_url, reason=e.strerror))
                else:
                    logger.warning("Non image content-type detected. "
                                   "Will skip download for: {url}".format(url=image_url))


if __name__ == '__main__':
    main()
