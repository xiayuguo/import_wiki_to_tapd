import os
import time
import asyncio
import argparse

from tqdm import tqdm
from pyppeteer import launch


UserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) " \
            "AppleWebKit/537.36 (KHTML, like Gecko) " \
            "Chrome/78.0.3904.97 Safari/537.36"

VERSION = "0.0.1"


async def login(page, username, password):
    await page.goto('https://www.tapd.cn/cloud_logins/login')
    await page.focus('#username')
    await page.keyboard.type(username)
    await page.focus('#password_input')
    await page.keyboard.type(password)
    await page.click('#tcloud_login_button')
    await page.waitForNavigation()
    success, fail = "#new_nav_avatar_div > a", '#error-tips'
    try:
        await page.waitForSelector(success, dict(timeout=5000))
        nick_name = await page.querySelectorEval(success, '(e => e.title)')
        print(f"登录成功: {nick_name}")
        return page
    except Exception:
        print("没有获取到登录成功的标志，检查失败原因")
        try:
            await page.waitForSelector(fail, dict(timeout=3000))
            error_tips = await page.querySelectorEval(fail, '(e => e.innerText)')
            raise Exception(f"登录失败: {error_tips}")
        except Exception:
            raise


async def create_wiki(page, create_wiki_url, title, reader, file_size, parent_name=None, remarks=""):
    await page.goto(create_wiki_url)
    await page.waitForSelector('#WikiName')
    await page.focus('#WikiName')
    await page.keyboard.type(title)
    await page.focus('#input')
    with tqdm(total=file_size, desc=f"import title {title}") as pbar:
        while 1:
            data = reader.read(1024)
            if len(data) == 0:
                break
            else:
                await page.keyboard.type(data)
            pbar.update(len(data))

    # 回滚到页面底部
    await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
    await page.waitForSelector('#WikiNote', )
    await page.focus('#WikiNote')
    await page.keyboard.type(remarks)
    if parent_name:
        await page.focus('#Markdown_wikiParentName')
        await page.keyboard.type(parent_name)
    await page.click('#wiki_btn_submit')
    await page.waitForNavigation()


async def main(params):
    browser = await launch(headless=False)
    await browser.newPage()
    page = await browser.newPage()
    await page.setUserAgent(UserAgent)
    # 登录开始
    await login(page, params.username, params.password)
    # 登录结束
    # 进入 wiki 页面
    wiki_url = await page.querySelectorEval('#myprojects-list > li:nth-child(2) > a', '(e => e.href)')
    create_wiki_url = f"{wiki_url.split('?')[0]}wikis/add?parent_wiki="
    # 批量创建 wiki
    for p in params.import_list:
        with open(p, "r") as f:
            parent_name = os.path.dirname(p).split('/')[-1]
            title = f"{parent_name}_{os.path.splitext(os.path.basename(p))[0]}"
            print(f"import local file: {p}")
            start = time.time()
            await create_wiki(page, create_wiki_url, title=title,
                              reader=f, file_size=os.stat(p).st_size)
            cost = time.time() - start
            print(f"import local file: {p}, cost: {cost} seconds")
    await browser.close()

if __name__ == "__main__":
    username = os.getenv("TAPD_USERNAME", "")
    password = os.getenv("TAPD_PASSWORD", "")
    parser = argparse.ArgumentParser(description='Import Wiki to Tapd.')
    parser.add_argument('-u', '--username', metavar='xxx@mail.com', type=str,
                        default=username, required=not bool(username),
                        help='username for tapd')
    parser.add_argument('-p', '--password', metavar='******', type=str,
                        default=password, required=not bool(password),
                        help='password for tapd')
    parser.add_argument('-F', '--folder', metavar='/home/hugo/project',
                        type=str, help='folder path of import files')
    parser.add_argument('-f', '--file', metavar='/home/hugo/project/home.md',
                        type=str, help='file path of import files')
    parser.add_argument('-g', '--git', type=str, help="git repository url (Not supported yet)")
    parser.add_argument('-c', '--classify', type=str, help='wiki parent name (Not supported yet)')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {VERSION}')
    params = parser.parse_args()
    import_list = []
    if params.folder:
        if not os.path.isdir(params.folder):
            raise Exception(f"{params.folder} is not directory.")
        for filename in os.listdir(params.folder):
            if filename.endswith(".md") or filename.endswith(".markdown"):
                import_list.append(os.path.join(params.folder, filename))
    if params.file:
        if not os.path.isfile(params.file):
            raise Exception(f"{params.file} is not file.")
        if params.file.endswith(".md") or params.file.endswith(".markdown"):
            import_list.append(params.file)

    if not import_list:
        raise Exception("Select at least one for file and folder.")
    setattr(params, "import_list", import_list)
    asyncio.get_event_loop().run_until_complete(main(params))
