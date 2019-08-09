#爬取妹子图网站(https://www.mzitu.com)图片
from requests_html import AsyncHTMLSession,HTMLSession
import os,shutil

def get_first_item(root_url):
    response = session.get(root_url)
    ul = response.html.find("#pins",first=True)
    lis = ul.find("li")

    #解析到第一个item就可以了
    #第二个item可以根据第一个item获取
    li = lis[0]
    span = li.find("span",first=True)
    link = span.find("a",first=True)
    link_url = link.absolute_links
    return link_url

#获取item的信息，包括图片的地址，图片的数量,页面地址
def get_item_info(url):
    url_str = "".join(url)
    response = session.get(url_str)
    div_image = response.html.find("div.main-image", first=True)
    img = div_image.find("img", first=True)
    img_alt = img.attrs["alt"]
    img_url = img.attrs["src"]
    div_navi = response.html.find("div.pagenavi",first=True)
    last_link = div_navi.find("a")[-2]
    span = last_link.find("span",first=True)
    img_count = span.full_text
    info = [img_alt,img_url,img_count,url_str]
    print(info)
    return info

def get_next_item_url(url):
    response = session.get("".join(url))
    div_navi = response.html.find("div.pagenavi", first=True)
    last_link = div_navi.find("a")[-1]
    return last_link.attrs["href"]

def download_item(item_info):
    max_download_count = 15
    index = 0
    while index < max_download_count:
        # 图片描述
        image_alt = item_info[0]
        image_url = item_info[1]
        image_count = int(item_info[2])
        page_url = item_info[-1]

        dir_path = "../mzitu/" + image_alt
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        image_prefix = image_url[0:len(image_url) - 6]
        image_suffix = image_url[-4:]
        for i in range(image_count):
            seq = "{:0>2d}".format(i + 1)
            url = image_prefix + seq + image_suffix
            # 不设置头信息会导致403错误
            response = session.get(url, headers={"Referer": "https://www.baidu.com"})
            image_url = "".join(url).replace(url_prefix, "")
            image_name = image_url.replace("/", "_")
            f = open(image_name, "wb")
            f.write(response.content)
            f.close()
            shutil.move(image_name, dir_path)
        index += 1
        if index < max_download_count:
            last_image_url = page_url + "/" + str(image_count)
            next_item_url = get_next_item_url(last_image_url)
            item_info = get_item_info(next_item_url)


if __name__ == "__main__":
    session = HTMLSession()
    root_url = "https://www.mzitu.com/xinggan/"
    url_prefix = "https://i.meizitu.net/"
    first_item_url = get_first_item(root_url)
    info = get_item_info(first_item_url)
    download_item(info)