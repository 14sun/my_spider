import requests
from lxml import etree
from urllib.parse import quote


# 格式化输出
def my_format(str1, width, align):  # 定义函数接受三个参数：要输出的字符串(str)、总占用宽度（int）、对齐方式（str:l、r、c对应左右中）
    single = 0
    double = 0
    sep = ' '  # 定义占位符
    for i in str1:  # 统计单字宽和双字宽的数目
        if len(i.encode('gb2312')) == 1:
            single += 1
        elif len(i.encode('gb2312')) == 2:
            double += 1
    if align == 'l':
        return str1 + (width * 2 - single - double * 2) * sep
    elif align == 'r':
        return (width * 2 - single - double * 2) * sep + str1
    elif align == 'c':
        return int((width * 2 - single - double * 2) // 2) * sep + str1 + int(
            (width * 2 - single - double * 2) - (width * 2 - single - double * 2) // 2) * sep


# 自己写的一个二维列表打表的函数
def print_table(table, max1):
    x = 0
    for c in table:
        if x == 0:
            print("   ", end="|")
        else:
            print(" ", x, end="|")
        x += 1
        for i in c:
            print(my_format(i, max1, 'c'), end='|')
        print("")

# 爬虫
class spider_novel_BQG():

    def __init__(self):
        self.novel_name = ""    # 小说名
        # 笔趣阁搜索页面的url，url的查询参数如下
        self.url = f"https://www.bbiquge.net/modules/article/search.php?searchkey={quote(self.novel_name)}&submit=%CB%D1%CB%F7"
        self.User_Agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"
        # 请求头，可以自己用u-a池
        self.headers = {
            "User-Agent": self.User_Agent
        }

    # 输入小说名称，同时更新url，来到后续的搜索页面
    def input_novel_name(self):
        self.novel_name = input("请输入要爬取的小说名：")
        self.url = f"https://www.bbiquge.net/modules/article/search.php?searchkey={quote(self.novel_name, encoding='gbk')}&submit=%CB%D1%CB%F7"

    # 获取小说的总界面的url
    def get_novel_url(self):
        # table是为了预备打表，提供一些选择
        ss = "文章名称,最新章节,作者,字数,更新,状态"
        table = [[]]
        table[0] = ss.split(",")
        _max = 0    # 打表预备用
        response = requests.get(url=self.url, headers=self.headers).text
        tree = etree.HTML(response)     # 生成搜索页面的树，后续xpath定位

        # 让输出好看一点
        print()
        print(f"{self.novel_name}的搜索结果如下：")
        print()

        # 自己定义提供几个搜索结果
        for i in range(2, 12):
            data_list = tree.xpath(f'//*[@id="main"]/table/tr[{i}]//text()')    # xpath定位搜索界面的信息
            for j in data_list:
                if len(j) > _max:
                    _max = len(j)
            table.append(data_list)
        # 获得信息后打表
        print_table(table, _max)
        print()
        # 选择要爬取的书籍序号
        number = int(input("请输入你要爬取的书籍序号:"))
        self.url = tree.xpath(f'//*[@id="main"]/table/tr[{number + 1}]/td[1]/a/@href')[0]
        self.novel_name = table[number][0]  # 更新url为小说原页面的url

    # 获取小说
    def get_novel(self):
        response = requests.get(self.url)   # 请求小说原页面
        tree = etree.HTML(response.text)    # 同样生成树
        html_list = tree.xpath(".//dd//a/@*")   # 获取章节url列表
        # 遍历列表访问每一章节页面，然后提取小说内容
        for html in html_list:
            # 更新子url
            # 注意返回的是树的元素对象，所以要更新为string对象
            url_son = self.url + str(html)
            response_son = requests.get(url_son)
            # 生成子树
            tree_son = etree.HTML(response_son.text)

            # 通过xpath获取标签中的所有小说内容
            words = tree_son.xpath("./body/div[3]/div[2]//text()")

            # 创建文件，同时通过一定操作让写入内容尽量格式美观
            with open(f"{self.novel_name}.txt", 'a', encoding='utf-8') as f:
                f.write(f"{self.novel_name}\n")
                title = tree_son.xpath("./body/div[3]/h1/text()")[0]
                f.write("\n" + title + "\n")
                print(f"正在爬取章节：{title}")
                i = 0
                for word in words:
                    i += 1
                    if i < 6:
                        continue
                    if word == 'hf();':
                        break
                    word = word[5::]
                    f.write('   ' + word + '\n')
        print("爬取完毕！")


if __name__ == "__main__":
    a = spider_novel_BQG()
    a.input_novel_name()
    a.get_novel_url()
    a.get_novel()
