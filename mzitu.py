#爬取妹子图网站(https://www.mzitu.com)图片
from requests_html import AsyncHTMLSession,HTMLSession
import os,shutil,time,sys
import asyncio
import requests

asession = AsyncHTMLSession()
session = HTMLSession()

def get_first_item(root_url):
    try:
        response = session.get(root_url)
        ul = response.html.find("#pins", first=True)
        if ul is None:
            print("get first item,ul not found")
            return None
        lis = ul.find("li")
        if lis is None:
            print("lis not found")
            return None
        # 解析到第一个item就可以了
        # 第二个item可以根据第一个item获取
        li = lis[0]
        span = li.find("span", first=True)
        if span is None:
            print("span not found")
            return None
        link = span.find("a", first=True)
        if link is None:
            print("link not found")
        link_url = link.absolute_links
        return link_url
    except Exception as e:
        return None
        print("get first item exception:",e)

#获取item的信息，包括图片的地址，图片的数量,页面地址
def get_item_info(index,url):
    try:
        url_str = "".join(url)
        response = session.get(url_str)
        div_image = response.html.find("div.main-image", first=True)
        if div_image is None:
            print("div image not found",url_str)
            return None
        img = div_image.find("img", first=True)
        if img is None:
            print("img not found",url_str)
            return None

        img_alt = img.attrs["alt"]
        img_url = img.attrs["src"]
        div_navi = response.html.find("div.pagenavi", first=True)
        if div_navi is None:
            print("div nav not found",url_str)
            return None
        last_link = div_navi.find("a")[-2]
        if last_link is None:
            print("last link not found",url_str)
            return None
        span = last_link.find("span", first=True)
        img_count = span.full_text
        info = [img_alt, img_url, img_count, url_str]
        print(index,info)
        return info
    except Exception as e:
        return None
        print("get item info exception:",e)

def get_next_item_url(url):
    try:
        response = session.get("".join(url))
        div_navi = response.html.find("div.pagenavi", first=True)
        if div_navi is None:
            print("get next item url,div navi not found")
            return None
        last_link = div_navi.find("a")[-1]
        return last_link.attrs["href"]
    except Exception as e:
        return None
        print("get next item url exception:",e)

def download_item(start,item_info):
    max_download_count = sys.maxsize
    index = start
    while index < max_download_count and not item_info is None:
        # 图片描述
        image_alt = item_info[0]
        image_url = item_info[1]
        image_count = int(item_info[2])
        page_url = item_info[-1]

        dir_seq = "{:0>5d}".format(index)
        dir_path = "../mzitu/" + dir_seq + "_" + image_alt
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        image_prefix = image_url[0:len(image_url) - 6]
        image_suffix = image_url[-4:]
        for i in range(image_count):
            seq = "{:0>2d}".format(i + 1)
            url = image_prefix + seq + image_suffix
            write_file(url,dir_path,image_count)
            # time.sleep(0.1)
        index += 1
        if index < max_download_count:
            last_image_url = page_url + "/" + str(image_count)
            next_item_url = get_next_item_url(last_image_url)
            if next_item_url is None:
                retry_count = 5
                while retry_count > 0 and next_item_url is None:
                    time.sleep(2)
                    retry_count -= 1
                    next_item_url = get_next_item_url(last_image_url)
            item_info = get_item_info(index,next_item_url)
            if item_info is None:
                retry_count = 5
                while retry_count > 0 and item_info is None:
                    time.sleep(2)
                    retry_count -= 1
                    item_info = get_item_info(index, next_item_url)

def write_file(url,dir_path,total):
    try:
        file_name = "".join(url).replace(url_prefix, "")
        file_name = file_name.replace("/", "_")
        file_name = str(total) + "_" + file_name
        full_path = dir_path + "/" + file_name
        if os.path.exists(full_path):
            print("file exist",full_path)
            return
        # 不设置头信息会导致403错误
        response = rsession.get("".join(url), headers=headers)
        if response.status_code != 200:
            print("get image data failed:",response.status_code)
            return
        image_data = response.content
        image_size = len(image_data)
        if image_size == 0:
            print("no image data:",url,response.status_code)
            return
        f = open(file_name,"wb")
        f.write(response.content)
        f.close()
        shutil.move(file_name, dir_path)
    except Exception as e:
        faile_file.append(["".join(url),dir_path,total])
        print("wirtie file exception:", e)

def retry_write_file(datas):
    while len(datas) > 0:
        item = datas.pop()
        url = item[0]
        dir_path = item[1]
        image_count = item[2]
        write_file("".join(url),"".join(dir_path),image_count)

if __name__ == "__main__":
    requests.adapters.DEFAULT_RETRIES = 5
    rsession = requests.session()
    rsession.proxies={"https":"123.117.33.156:9000","https":"125.62.27.53:3128","https":"106.12.197.44:3128","https":"210.22.5.117:3128","https":"112.109.198.106:3128",
                      "https":"112.109.198.106:3128","https":"183.216.183.67:3128","http":"121.17.174.121:9797"}
    loop = asyncio.get_event_loop()
    faile_file = []
    root_url = "https://www.mzitu.com/xinggan/"
    url_prefix = "https://i.meizitu.net/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',"Referer": "https://www.baidu.com"}
    first_item_url = get_first_item(root_url)
    first_item_url = "https://www.mzitu.com/70318"
    if not first_item_url is None:
        info = get_item_info(2438,first_item_url)
        download_item(2438,info)
    print("retry write file:",len(faile_file))
    retry_write_file(faile_file)
    session.close()
    loop.close()