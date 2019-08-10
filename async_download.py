#异步下载android系统源码
#下载地址https://www.androidos.net.cn/android/9.0.0_r8/xref

import time,os,shutil
import asyncio
from requests_html import AsyncHTMLSession
import aiohttp,aiofiles

asession = AsyncHTMLSession()
client_session = aiohttp.ClientSession()

#将一个页面的下载列表解析出来，包含文件夹、文件
async def get_content_list(url,semaphore,index,total):
    print("get content list,index:",index,"total:",total)

    async with semaphore:
        url_list = []
        url_str = "".join(url)
        try:
            response = await asession.get(url_str)
            table = response.html.find('table.filelist', first=True)
            if table is None:
                print("is file", url_str)
                return url_list
            tr_list = table.find("tr")
            if tr_list is None:
                return url_list

            for tr in tr_list:
                td = tr.find("td.content", first=True)
                if not td is None:
                    link = td.find("a", first=True)
                    text = link.full_text
                    content_url = link.absolute_links
                    if text != "..":
                        url_list.append("".join(content_url))
        except Exception as e:
            url_list.append(url_str)
            print("get content list excetpion:",e)
        return url_list

async def write_file(url,semaphore,index,total):
    async with semaphore:
        try:
            print("write file,current index:",index,"total:",total)
            faile_file_list = []
            url_str = "".join(url)
            file_name = url_str.replace(url_prex, "")
            dir_path = file_name
            file_name = file_name.replace("/", "_")
            response = await asession.get(url_str)
            # content = await response.text(encoding="utf-8")
            async with aiofiles.open(file_name, "wb") as f:
                await f.write(response.content)
            f.close()
            shutil.move(file_name, dir_path)
        except Exception as e:
            faile_file_list.append(url_str)
            print("write file exception:",e)
        finally:
            return faile_file_list

def parse_html(url,loop):
    dir_list = [url]
    file_list = []
    max_cout = 512
    semaphore =  asyncio.Semaphore(max_cout)
    while len(dir_list) > 0:
        index = 0
        tasks = []
        total = len(dir_list)
        while len(dir_list) > 0:
            index += 1
            if index > max_cout:
                break
            dir_url = dir_list.pop()
            url_str = "".join(dir_url)
            task = asyncio.ensure_future(get_content_list(url_str,semaphore,index,total))
            tasks.append(task)
        result = loop.run_until_complete(asyncio.gather(*tasks))
        for items in result:
            for u in items:
                if is_file(u):
                    if is_support_download_file(u):
                        file_list.append(u)
                else:
                    if not is_invalid_file(u):
                        dir_list.append(u)
    return file_list

def download_file(list_data,loop):
    #避免pycharm同步文件，将文件写到上一级目录
    os.chdir("..")

    max_cout = 512
    semaphore = asyncio.Semaphore(max_cout)
    total = len(list_data)
    file_index = 0
    while len(list_data) > 0:
        tasks = []
        index = 0
        while len(list_data) > 0:
            index += 1
            file_index += 1
            if index > max_cout:
                break
            file_url = list_data.pop()
            url_str = "".join(file_url).replace("xref","download")
            dir_path = url_str.replace(url_prex,"")
            dir_path = dir_path[0:dir_path.rfind("/")]
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            task = asyncio.ensure_future(write_file(url_str,semaphore,file_index,total))
            tasks.append(task)
        if len(tasks) > 0:
            result = loop.run_until_complete(asyncio.gather(*tasks))
            for items in result:
                for u in items:
                    list_data.append(u)

def save_file(file_name,list_data):
    try:
        f = open(file_name, "w")
        for url in list_data:
            f.write("".join(url))
            f.write("\n")
    except Exception as e:
        print("write file exception:",e)
    finally:
        f.close()

def read_file_list(file_name):
    try:
        file_list = []
        f = open(file_name,"r")
        line = f.readline()
        while line:
            line = line.strip("\n")
            file_list.append(line)
            line = f.readline()
    except Exception as e:
        print("read file exception:",e)
    finally:
        f.close()
        return file_list

def is_file(url):
    file_name = get_file_name(url)
    return "".join(file_name).find(".") != -1

def is_support_download_file(url):
    if not is_file(url):
        return False
    file_name = get_file_name(url)
    suffix = file_name.split(".")[-1]
    valid_suffix = ["java","c","cpp","h","xml"]
    return valid_suffix.count(suffix) > 0
def get_file_name(url):
    return "".join(url).split("/")[-1]

def is_invalid_file(url):
    invalid_files = ["OWNERS","MODULE_LICENSE_APACHE2","gradlew","NOTICE","README","Doxyfile","Makefile","IN_CTS","MODULE_LICENSE_MIT",
                     "MODULE_LICENSE_BSD_OR_LGPL","MODULE_LICENSE_BSD_LIKE","MOVED","MODULE_LICENSE_CPL","LICENSE","NO_DOCS","THEMES",
                     "IGNORE_CHECKSTYLE"]
    file_name = get_file_name(url)
    return invalid_files.count(file_name) > 0

async def close_client_session():
    await client_session.close()

async def close_aession():
    await asession.close()

if __name__ == "__main__":
    start = time.time()
    root_url = "https://www.androidos.net.cn/android/9.0.0_r8/xref/frameworks"
    url_prex = "https://www.androidos.net.cn/"
    loop = asyncio.get_event_loop()
    file_name = "url_list.txt"

    #第一步，将下载的文件列表解析出来
    # file_list_url = parse_html(root_url,loop)
    # print("file list count", len(file_list_url))

    # loop.run_until_complete(close_aession())

    #第二步，保存到文件中
    # save_file(file_name,file_list_url)

    #第三步，读取文件中的下载列表
    file_list_url = read_file_list(file_name)
    print("file list count",len(file_list_url))

    #第四步，下载文件到本地
    download_file(file_list_url,loop)

    loop.run_until_complete(close_client_session())

    loop.close()
    print("complete,cost time:",time.time() - start)