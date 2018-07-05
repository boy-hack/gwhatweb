import requests
import json,hashlib,sys
import gevent
from gevent import monkey
monkey.patch_all()
from gevent.queue import Queue
import time

class gwhatweb(object):
    def __init__(self,url):
        self.tasks = Queue()
        self.url = url.rstrip("/")
        fp = open('data.json')
        webdata = json.load(fp, encoding="utf-8")
        for i in webdata:
            self.tasks.put(i)
        fp.close()
        print("webdata total:%d"%len(webdata))
		
    def _GetMd5(self,body):
        m2 = hashlib.md5()
        m2.update(body.encode("utf8"))
        return m2.hexdigest()

    def _clearQueue(self):
        while not self.tasks.empty():
            self.tasks.get()

    def _worker(self):
        data = self.tasks.get()
        test_url = self.url + data["url"]
        rtext = ''
        try:
            r = requests.get(test_url,timeout=10)
            if (r.status_code != 200):
                return
            rtext = r.text
            if rtext is None:
                return
        except:
            rtext = ''

        if data["re"]:
            if (rtext.find(data["re"]) != -1):
                result = data["name"]
                print("CMS:%s Judge:%s re:%s" % (result, test_url, data["re"]))
                self._clearQueue()
                return True
        else:
            md5 = self._GetMd5(rtext)
            if (md5 == data["md5"]):
                result = data["name"]
                print("CMS:%s Judge:%s md5:%s" % (result, test_url, data["md5"]))
                self._clearQueue()
                return True


    def _boss(self):
        while not self.tasks.empty():
            self._worker()

    def whatweb(self,maxsize=100):
        start = time.clock()
        allr = [gevent.spawn(self._boss) for i in range(maxsize)]
        gevent.joinall(allr)
        end = time.clock()
        print ("cost: %f s" % (end - start))

if __name__ == '__main__':
	if len(sys.argv) < 2:
			print("usag:python gwhatweb.py http://www.xxx.com")
	else:
		url = sys.argv[1]
		g = gwhatweb(url)
		g.whatweb(1000)
