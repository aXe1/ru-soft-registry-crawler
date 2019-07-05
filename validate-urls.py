import urllib.request
import ssl
import json


def validate_link(url):
    url_validate = False
    resp = None
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        resp = urllib.request.urlopen(url, context=ctx)
        print('no exception')
        print(resp.code)
        print(resp.reason)
        url_validate = True
    except ValueError as e:
        print('valueerror')
        print(e)
    except TimeoutError as e:
        print('timeouterror')
        print(e)
    except urllib.error.URLError as e:
        print('urlerror')
        print(e)

    return url_validate


with open('soft-2.json', 'rb') as json_file:
    json = json.load(json_file)

for soft in json:
    url = soft['url']
    print(url)
    print(validate_link(url))
