import sys, os, mimetypes, time

import requests

from pyquery import PyQuery as pq

from IPython import embed

def grab_links(url, limit=5, found_links=None, retries=0):

    limit -= 1

    if not found_links:
        found_links = []

    time.sleep(3)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.74.9 (KHTML, like Gecko) Version/7.0.2 Safari/537.74.9'
    }

    r = requests.get(url, headers=headers)

    if "<title>Too Many Requests</title>" in r.text and retries < 5:
        print "retrying"
        time.sleep(30)
        limit += 1
        retries += 1
        grab_links(url, limit, found_links, retries)

    page = pq(r.text)

    links = page("a.title")

    for link in links:

        found_links.append(link.attrib["href"])

    next_links = page("a[rel*='next']")

    if len(next_links) > 0 and limit > 0:

        found_links + grab_links(next_links[0].attrib["href"], limit, found_links)

    return found_links


def get_and_filter_pages(link_list, user_path):

    image_types = ['jpeg', 'gif', 'png', 'bmp', 'jpg', 'jfif', 'tiff']

    for link in link_list:

        if "imgur" not in link:
            continue

        time.sleep(1)

        file_type = mimetypes.guess_type(link)[0]

        if file_type:

            file_type = file_type[file_type.rfind("/")+1:]

            if file_type in image_types:

                download_image(link, user_path, file_type)

        else:

            parse_page_for_images(link, user_path)


def parse_page_for_images(link, user_path):

    time.sleep(1)

    r = requests.get(link)

    page = pq(r.text)

    #check for a single imgur image

    album_images = page(".album-image")

    header = page("#image-title")

    if header and not album_images:

        try:
            
            image_q = page("div#image div a")

            if len(image_q) < 1:
                image_q = page("div#image div img")
                image = image_q[0]
                image_url = image.attrib["src"]

            else:
                image = image_q[0]
                image_url = image.attrib["href"]

            download_image(image_url, user_path)

        except:

            print link

    else:

        images = page("a.zoom")

        try:

            if len(images) > 0:

                for image in images:
                    if not "watch" in image.attrib["href"]:
                        download_image(image.attrib["href"], user_path)

            else:

                images = page(".image img")

                for image in images:
                    if not "watch" in image.attrib["src"]:
                        download_image(image.attrib["src"], user_path)

        except:

            print link




def download_image(url, path, file_type=None):

    if url[0:2] == "//":
        url = "http:" + url

    r = requests.get(url, stream=True)

    file_name = url[url.rfind("/")+1:]

    file_name = file_name.replace("?1","")

    if "." not in file_name:
        return

    file_path = path + os.sep + file_name

    if file_type:

        file_path + file_type

    if r.status_code == 200:    

        with open(file_path, 'wb') as f:

            for chunk in r.iter_content(1024):

                f.write(chunk)


def prep_ground(username_or_url, limit):

    root_path = os.getcwd() + "/static/r_gifs"

    if "reddit.com/" not in username_or_url:
        user_path = root_path + os.sep + username_or_url
        url = "http://www.reddit.com/user/%s/submitted" % username_or_url
    else:
        #folder = "r_%s" % username_or_url[username_or_url.rfind("/")+1:]
        user_path = root_path #+ os.sep + folder
        url = username_or_url

    if not os.path.exists(user_path):

        os.makedirs(user_path)

    links = grab_links(url, limit)
    
    get_and_filter_pages(links, user_path)


if __name__ == "__main__":

    try:
        limit = sys.argv[2]
    except:
        limit = 5

    print prep_ground(sys.argv[1], limit)
