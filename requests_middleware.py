import requests
from bs4 import BeautifulSoup


def make_soup(html, decompose=''):
    soup = BeautifulSoup(html, 'html5lib')

    names = decompose.split(',') if isinstance(decompose, str) else list(decompose)
    [tag.decompose() for name in names for tag in soup.find_all(name)]

    return soup


class ResponseMiddleware(object):
    
    def __init__(self,):
        self.response = None
        self._soup = None
    
    @classmethod
    def callback(self, r, *args, **kwargs):
        r = self.init_soup(r)
    
    @classmethod
    def init_soup(self,r):
        self._soup = None
        self.response = r
        
        r.soup=self.soup
        r.select_one=self.select_one
        r.select=self.select
        r.find=self.find
        r.find_all=self.find_all
        return r
    
        
    @classmethod
    def soup(self):
        if not self._soup:
            self._soup = make_soup(self.response.text)
        return self._soup
    
    @classmethod
    def select_one(self, css_path):
        return self.soup().select_one(css_path)
    
    @classmethod
    def select(self, css_path):
        return self.soup().select(css_path)
    
    @classmethod
    def find(self,tag,**kwargs):
        return self.soup().find(tag, **kwargs)
    
    @classmethod
    def find_all(self,tag,**kwargs):
        return self.soup().find_all(tag, **kwargs)

    
class RequestMiddleware(requests.Session):
    
    def __init__(self,*args,**kwargs):
        super(RequestMiddleware, self).__init__(*args, **kwargs)
        self.init_plugins()
        
        self._worker = None
        self.page = None
        
    def init_plugins(self):
        self.init_hook()
        self.update_user_agent()
        
    def update_user_agent(self,):
        default_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:64.0) Gecko/20100101 Firefox/64.0'
        self.headers.update({'User-Agent': default_agent})
        
    def init_hook(self,):
        self.hooks['response'].append(ResponseMiddleware.callback)
                            
    def worker(self,func):
        self._worker = func
        return func
        

class Session(RequestMiddleware):
    def __init__(self,*args, **kwargs):
        super(Session, self).__init__(*args, **kwargs)   
   
if __name__ == '__main__':
    client = Session()
    res = client.get('https://github.com/')
    desc = res.select_one('[class="lead-mktg mb-4"]').text
    print(desc)
