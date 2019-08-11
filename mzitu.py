#爬取妹子图网站(https://www.mzitu.com)图片
from requests_html import AsyncHTMLSession,HTMLSession
import os,shutil,sys
import asyncio,aiofiles

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

def download_item(item_info):
    max_download_count = sys.maxsize
    index = 0
    while index < max_download_count and not item_info is None:
        # 图片描述
        image_alt = item_info[0]
        image_url = item_info[1]
        image_count = int(item_info[2])
        page_url = item_info[-1]

        dir_seq = "{:0>9d}".format(index+1)
        dir_path = "../mzitu/" + dir_seq + "_" + image_alt
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        image_prefix = image_url[0:len(image_url) - 6]
        image_suffix = image_url[-4:]
        tasks = []
        for i in range(image_count):
            seq = "{:0>2d}".format(i + 1)
            url = image_prefix + seq + image_suffix
            task = asyncio.ensure_future(write_file(url,dir_path))
            tasks.append(task)
        loop.run_until_complete(asyncio.wait(tasks))
        index += 1
        if index < max_download_count:
            last_image_url = page_url + "/" + str(image_count)
            next_item_url = get_next_item_url(last_image_url)
            item_info = get_item_info(index,next_item_url)
def done_callback():
    print("done")

async def write_file(url,dir_path):
    try:
        file_name = "".join(url).replace(url_prefix, "")
        file_name = file_name.replace("/", "_")
        # 不设置头信息会导致403错误
        response = await asession.get("".join(url), headers={"Referer": "https://www.baidu.com"})
        async with aiofiles.open(file_name, "wb") as f:
            await f.write(response.content)
        f.close()
        shutil.move(file_name, dir_path)
    except Exception as e:
        print("wirtie file exception:", e)

async def close_asession():
    await asession.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    root_url = "https://www.mzitu.com/xinggan/"
    url_prefix = "https://i.meizitu.net/"
    first_item_url = get_first_item(root_url)
    if not first_item_url is None:
        info = get_item_info(0,first_item_url)
        download_item(info)

    loop.run_until_complete(close_asession())
    session.close()
    loop.close()