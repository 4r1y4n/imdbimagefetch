'''
Created on Sep 22, 2013

@author: 4r1y4n

'''

from urlparse import urlparse
from bs4 import BeautifulSoup
import os,sys,re,urllib2,urllib,socket,datetime

def getPicInfo(url):
    o=urlparse(url);
    r=o.netloc+"/"+o.path+"/"+"mediaindex"
    return (o.scheme+"://"+re.sub("/{2,}", "/",r),o.path)

if __name__ == '__main__':
    try:
        socket.setdefaulttimeout(30)
        baseDir="./data"
        start=datetime.datetime.now().replace(microsecond=0)
        #url="http://www.imdb.com/name/nm0334441/"
        url = raw_input('Enter IMDB name or title page URL: ')
        if not re.match(r"^http://(www)?\.imdb\.com/((name)|(title))/\w+/(\?.*)?/{0,1}$", url,re.IGNORECASE) :
            print "Bad IMDB name or title page URL"
            sys.exit(1)
        (picGalleryURL,saveAddr)=getPicInfo(url)
        print "Reading Gallery ... "
        tries=0
        success=False
        links=[]
        while tries<5:
            tries+=1
            pages=1
            try:
                picpage=urllib2.urlopen(picGalleryURL)
                picpagehtml=picpage.read()
                soup=BeautifulSoup(picpagehtml)
                
                sys.stdout.write("Reading Title: ")
                sys.stdout.flush()
                itemtitle=soup.find(attrs={"itemprop":"name"}).find('a',{'itemprop':'url'}).text
                saveAddr=saveAddr.rstrip("/")+" - "+itemtitle+"/"
                print itemtitle
                
                pagesoup=soup.find("span", {"class":"page_list"})
                if pagesoup is not None:
                    try:
                        pages=int(pagesoup.find_all("a")[-1].text)
                    except:
                        pages=1
                print "Pages: %d" % pages
                sys.stdout.write("Reading pages: ")
                sys.stdout.flush()
                for i in range(1,pages+1):
                    ptries=0
                    psuccess=False
                    while ptries<5:
                        try:
                            tries+=1
                            sys.stdout.write("%d " % i)
                            sys.stdout.flush()
                            picpage=urllib2.urlopen(picGalleryURL+("?page=%d" % i))
                            picpagehtml=picpage.read()
                            soup=BeautifulSoup(picpagehtml)
                            if soup is None:
                                continue
                            links+=soup.find_all("a", {"itemprop":"thumbnailUrl"})
                            psuccess=True
                            break
                        except urllib2.URLError, e:
                            # For Python 2.6
                            if isinstance(e.reason, socket.timeout):
                                pass
                            else:
                                # reraise the original error
                                print (" | error: %r" % e)
                                break
                        except socket.timeout, e:
                            pass
                    if psuccess==False:
                        print "\nError reading pages."
                        print "Exiting ..."
                        raw_input("Press Enter to Exit ...")
                        sys.exit(3)
                success=True
                print " | Done"
                break
            except urllib2.URLError, e:
                # For Python 2.6
                if isinstance(e.reason, socket.timeout):
                    sys.stdout.write(" | timeout")
                    sys.stdout.flush()
                else:
                    # reraise the original error
                    print (" | error: %r" % e)
                    break
            except socket.timeout, e:
                # For Python 2.7
                sys.stdout.write(" | timeout")
                sys.stdout.flush()
        if not success:
            print "Gallery page read error; exiting ..."
            raw_input("Press Enter to Exit ...")
            sys.exit(2)
        
        print "Found %d images" % (len(links),)
        picPageList=["http://www.imdb.com"+link.get('href') for link in links]
        spath=baseDir+saveAddr
        if not os.path.exists(spath):
            print "Creating directory for page: %s" % (spath,)
            os.makedirs(spath, 0777)
        count=0
        for link in picPageList:
            count+=1
            sys.stdout.write("%d: Getting %s" % (count,os.path.basename(os.path.dirname(urlparse(link).path))))
            sys.stdout.flush()
            tries=0
            success=False
            while tries<5:
                try:
                    tries+=1
                    picopen=urllib2.urlopen(link,timeout=30)
                    pichtml=picopen.read()
                    picsoup=BeautifulSoup(pichtml,'html.parser')
                    picl=picsoup.find("img",{"id":"primary-img"})
                    if picl is None:
                        sys.stdout.write(" | no picture found! ")
                        sys.stdout.flush()
                        continue
                    picurl=picl.get("src")
                    picname=os.path.basename(picurl)
                    urllib.urlretrieve(picurl, os.path.join(spath,picname))
                    success=True
                    print " | Done"
                    break
                except urllib2.URLError, e:
                    # For Python 2.6
                    if isinstance(e.reason, socket.timeout):
                        sys.stdout.write(" | timeout")
                        sys.stdout.flush()
                    else:
                        # reraise the original error
                        print " | error: %r" % e
                        break
                except socket.timeout, e:
                    # For Python 2.7
                    sys.stdout.write(" | timeout")
                    sys.stdout.flush()
            if not success:
                print " | Skip"
        end=datetime.datetime.now().replace(microsecond=0)
        print "Finished ("+str(end-start)+")"
        raw_input("Press Enter to Exit ...")
    except KeyboardInterrupt:
        print "\nExit command recived."
        raw_input("Press Enter to Exit ...")
    except SystemExit:
        raw_input("Press Enter to Exit ...")
    except Exception as e:
        print "\nException: %r" % e
        raw_input("Press Enter to Exit ...")
