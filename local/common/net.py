# coding:utf-8

import ssl
import errno
import socket
import random
import ipaddress
import logging
import OpenSSL
import urllib.request
from local.GlobalConfig import GC

NetWorkIOError = socket.error, ssl.SSLError, ssl.CertificateError, OSError
if OpenSSL:
    NetWorkIOError += OpenSSL.SSL.Error,
reset_errno = errno.ECONNRESET, errno.ENAMETOOLONG
if hasattr(errno, 'WSAENAMETOOLONG'):
    reset_errno += errno.WSAENAMETOOLONG,
closed_errno = errno.ECONNABORTED, errno.ECONNRESET, errno.EPIPE
bypass_errno = -1, *closed_errno

dchars = ['bcdfghjklmnpqrstvwxyz', 'aeiou', '0123456789']
pchars = [0, 0, 0, 1, 2, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1]
subds = [
    'www', 'img', 'pic', 'js', 'game', 'mail', 'static', 'ajax', 'video', 'lib',
    'login', 'player', 'image', 'api', 'upload', 'download', 'cdnjs', 'cc', 's',
    'book', 'v', 'service', 'web', 'forum', 'bbs', 'news', 'home', 'wiki', 'it'
    ]
gtlds = ['org', 'com', 'net', 'gov', 'edu', 'xyz','info']

def random_hostname(wildcard_host=None):
    replace_wildcard = wildcard_host and '*' in wildcard_host
    if replace_wildcard and '{' in wildcard_host:
        try:
            a = wildcard_host.find('{')
            b = wildcard_host.find('}')
            word_length = int(wildcard_host[a + 1:b])
            wildcard_host = wildcard_host[:a] + wildcard_host[b + 1:]
        except:
            pass
    else:
        word_length = random.randint(5, 12)
    maxcl = word_length * 2 // 3 or 1
    maxcv = word_length // 2 or 1
    maxd = word_length // 6
    chars = []
    for _ in range(word_length):
        while True:
            n = random.choice(pchars)
            if n == 0 and maxcl:
                maxcl -= 1
                break
            elif n == 1 and maxcv:
                maxcv -= 1
                break
            elif n == 2 and maxd:
                maxd -= 1
                break
        chars.append(random.choice(dchars[n]))
    random.shuffle(chars)
    if word_length > 7 and not random.randrange(3):
        if replace_wildcard:
            if '-' not in wildcard_host:
                chars[random.randint(4, word_length - 4)] = '-'
        else:
            chars.insert(random.randint(4, word_length - 3), '-')
    sld = ''.join(chars)
    if replace_wildcard:
        return wildcard_host.replace('*', sld)
    else:
        subd = random.choice(subds)
        gtld = random.choice(gtlds)
        return '.'.join((subd, sld, gtld))

def isip(ip):
    if '.' in ip:
        return isipv4(ip)
    elif ':' in ip:
        return isipv6(ip)
    else:
        return False

def isipv4(ip, inet_aton=socket.inet_aton):
    if '.' not in ip:
        return False
    try:
        inet_aton(ip)
    except:
        return False
    else:
        return True

def isipv6(ip, AF_INET6=socket.AF_INET6, inet_pton=socket.inet_pton):
    if ':' not in ip:
        return False
    try:
        inet_pton(AF_INET6, ip)
    except:
        return False
    else:
        return True

#import re

#isipv4 = re.compile(r'^(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$').match
#isipv6 = re.compile(r'^(?!:[^:]|.*::.*::)'
#                    r'(?:[0-9a-f]{0,4}(?:(?<=::)|(?<!::):)){7}'
#                    r'([0-9a-f]{1,4}'
#                    r'|(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})$', re.I).match

def get_parent_domain(host):
    ip = isip(host)
    if not ip:
        hostsp = host.split('.')
        nhost = len(hostsp)
        if nhost > 3 or nhost == 3 and (len(hostsp[-1]) > 2 or len(hostsp[-2]) > 3):
            host = '.'.join(hostsp[1:])
    return host

def get_main_domain(host):
    ip = isip(host)
    if not ip:
        hostsp = host.split('.')
        if len(hostsp[-1]) > 2:
            host = '.'.join(hostsp[-2:])
        elif len(hostsp) > 2:
            if len(hostsp[-2]) > 3:
                host = '.'.join(hostsp[-2:])
            else:
                host = '.'.join(hostsp[-3:])
    return host

direct_opener = urllib.request.OpenerDirector()
#if GC.proxy:
#    direct_opener.add_handler(urllib.request.ProxyHandler({
#        'http': GC.proxy,
#        'https': GC.proxy
#    })
handler_names = ['UnknownHandler', 'HTTPHandler', 'HTTPSHandler',
                 'HTTPDefaultErrorHandler', 'HTTPRedirectHandler',
                 'HTTPErrorProcessor']
for handler_name in handler_names:
    klass = getattr(urllib.request, handler_name, None)
    if klass:
        direct_opener.add_handler(klass())

def get_wan_ipv4():
    if GC.DNS_IP_API:
        apis = list(GC.DNS_IP_API)
        random.shuffle(apis)
        for url in apis:
            response = None
            try:
                response = direct_opener.open(url, timeout=10)
                content = response.read().decode().strip()
                if isip(content):
                    logging.test('当前 IPv4 公网出口 IP 是：%s', content)
                    return content
            except:
                pass
            finally:
                if response:
                    response.close()
    logging.warning('获取 IPv4 公网出口 IP 失败，请增加更多的 IP-API')

def get_wan_ipv6():
    sock = None
    try:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        sock.connect(('2001:4860:4860::8888', 80))
        addr6 = ipaddress.IPv6Address(sock.getsockname()[0])
        if addr6.is_global or addr6.teredo:
            return addr6
    except:
        pass
    finally:
        if sock:
            sock.close()
