# -*- coding: utf-8 -*-
#from pyvirtualdisplay import Display
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common import exceptions
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import re
import requests
import json
import sys
import traceback
from bs4 import BeautifulSoup
import sqlite3
import sys
reload(sys)
sys.setdefaultencoding('utf8')
#from cn.localhost01.util.str_util import print_msg

# 对于py2，将ascii改为utf8
#reload(sys)
#sys.setdefaultencoding('utf8')
class TaobaoClimber:
    def __init__(self, username, password):
        self.__session = requests.Session()
        self.__username = username
        self.__password = password

    driver = None
    action = None
    shop_home=""
    nickname="风筝雷尔"
    # 是否登录
    __is_logined = False

    # 淘宝账户
    __username = ""
    # 登录密码
    __password = ""
    # 登陆URL
    __login_url = "https://login.taobao.com/member/login.jhtml"
    # 卖家待发货订单URL
    __orders_url = "https://trade.taobao.com/trade/itemlist/list_sold_items.htm?action=itemlist/SoldQueryAction&event_submit_do_query=1&auctionStatus=PAID&tabCode=waitSend"
    # 卖家正出售宝贝URL
    __auction_url = "https://sell.taobao.com/auction/merchandise/auction_list.htm"
    # 卖家仓库中宝贝URL
    __repository_url = "https://sell.taobao.com/auction/merchandise/auction_list.htm?type=1"
    # 卖家确认发货URL
    __deliver_url = "https://wuliu.taobao.com/user/consign.htm?trade_id="
    # 卖家退款URL
    __refunding_url = "https://trade.taobao.com/trade/itemlist/list_sold_items.htm?action=itemlist/SoldQueryAction&event_submit_do_query=1&auctionStatus=REFUNDING&tabCode=refunding"
    # 请求留言URL
    __message_url = "https://trade.taobao.com/trade/json/getMessage.htm?archive=false&biz_order_id="
    # requests会话
    __session = None

    def __login(self):

        # 1.登陆
        try:
            self.driver.get(self.__login_url)
        except exceptions.TimeoutException:  # 当页面加载时间超过设定时间，JS来停止加载
            
            self.driver.execute_script('window.stop()')

        count = 0
        while count < 5:  # 重试5次
            count += 1
            if self.__login_one() is True:
                break
        if count == 5:
            return False

        # 2.保存cookies
        # driver.switch_to_default_content() #需要返回主页面，不然获取的cookies不是登陆后cookies
        list_cookies = self.driver.get_cookies()
        cookies = {}
        for s in list_cookies:
            cookies[s['name']] = s['value']
            requests.utils.add_dict_to_cookiejar(self.__session.cookies, cookies)  # 将获取的cookies设置到session
        return True

    def __login_one(self):
        '''try:
            # 1.点击密码登录，切换到密码登录模式 默认是二维码登录
            username_login_btn = self.driver.find_element_by_xpath("//a[@class='forget-pwd J_Quick2Static']")
            if username_login_btn.is_displayed() is True:
                username_login_btn.click()
        except exceptions.ElementNotInteractableException:
            pass

        # 2.获取账户、密码输入框
        username_input = self.driver.find_element_by_id("TPL_username_1")
        password_input = self.driver.find_element_by_id("TPL_password_1")
        # 3.为账户、密码赋值
        username_input.clear()
        username_input.send_keys(self.__username)
        password_input.send_keys(self.__password)
        self.driver.find_element_by_id("J_Quick2Static").click()
        '''
        # 4.滑块判断
        #self.__slide_login()

        # 5.获取登陆按钮，并点击登录
        #submit_btn = self.driver.find_element_by_id("J_SubmitStatic")
        #submit_btn.click()
        while True:
            QRCodeImg = self.driver.find_element_by_id("J_QRCodeImg")
            if QRCodeImg.is_displayed() is False:
                continue
            else:
                break
        QRCodeImg_src = QRCodeImg.find_element_by_tag_name("img")
        print (QRCodeImg_src.get_attribute("src"))
        QRCodeImg_err = self.driver.find_elements_by_class_name("msg_err")
        QRCodeImg_err_text = self.driver.find_element_by_xpath("// *[ @id='J_QRCodeLogin']/div[3]/div[1]/div[3]/h6").text
        print (QRCodeImg_err_text)
        if (QRCodeImg_err_text == u"二维码已失效"):
            print("需要刷新")
        # 6.根据提示判断是否登录成功
        count = 0
        while True:
            url  = self.driver.current_url
            if url == "https://www.taobao.com/" or url=="https://world.taobao.com/":
                print (u"登录 成功！")
                break
            elif url !="https://login.taobao.com/member/login.jhtml":
                iframe = self.driver.find_elements_by_tag_name("iframe")[0]
                self.driver.switch_to_frame(iframe)
                print(url)
                while True:
                    try:
                        btn = self.driver.find_element_by_xpath("//*[@id='J_Phone']/ul/li[3]/input[1]")
                        break
                    except:
                        pass

                btn.click()
                code = input("输入验证码:\n")
                m_input = self.driver.find_element_by_xpath("//*[@id='J_Phone']/ul/li[5]/input")
                m_input.click()
                m_input.send_keys(code)
                self.driver.find_element_by_xpath("//*[@id='J_FooterSubmitBtn']").click()
            time.sleep(5)
            count += 1
            if (count > 12 * 5):
                print (u"登录超时")
                return False


        '''
        try:
            message = self.driver.find_element_by_id("J_Message").find_element_by_class_name("error")
            if message.text == u"为了你的账户安全，请拖动滑块完成验证":
                self.driver.execute_script(
                    "document.getElementById('J_Message').children[1].innerText='发货机器人：请滑动滑块，协助完成验证！';")
                return False
        except exceptions.NoSuchElementException:
            pass

        # 7.有时检测当前环境是否异常，此时休眠一段时间让它检测
        while True:
            try:
                self.driver.find_element_by_id("J_SiteNav")
                break
            except exceptions.NoSuchElementException:
                time.sleep(1)
	'''
        return True

    def __slide_login(self):
        # 取得滑块所在div，判断是否display 一般首次登陆不需要滑块验证
        slide_div = self.driver.find_element_by_id("nocaptcha")
        if slide_div.is_displayed() is True:
            self.driver.execute_script(
                "document.getElementById('J_Message').children[1].innerText='发货机器人：请滑动滑块，协助完成验证！';")
            while True:
                try:
                    text = self.driver.find_element_by_id("nc_1__scale_text").text
                    if text == '验证通过':
                        break
                    time.sleep(0.5)
                except exceptions.NoSuchElementException:  # 此时处于刷新按钮状态
                    pass

    def __get_orders_page(self):
        # 1.bs4将资源转html
        html = BeautifulSoup(self.driver.page_source, "html5lib")
        # 2.取得所有的订单div
        order_div_list = html.find_all("div", {"class": "item-mod__trade-order___2LnGB trade-order-main"})
        # 3.遍历每个订单div，获取数据
        data_array = []
        for index, order_div in enumerate(order_div_list):
            order_id = order_div.find("input", attrs={"name": "orderid"}).attrs["value"]
            order_date = order_div.find("span",
                                        attrs={"data-reactid": re.compile(r"\.0\.5\.3:.+\.0\.1\.0\.0\.0\.6")}).text
            order_buyer = order_div.find("a", attrs={"class": "buyer-mod__name___S9vit"}).text
            # 4.根据订单id组合url，请求订单对应留言
            order_message = json.loads(self.__session.get(self.__message_url + order_id).text)['tip']
            data_array.append((order_id, order_date, order_buyer, order_message))
        return data_array

    def climb(self):
        # FIXME 没有真实订单的模拟测试，生产环境注释即可
        order_test = [("Test_1548615412315", "2018-08-07 15:00:03", "疯狂的石头",u"留言: test@qq.com  http://download.csdn.net/download/lqkitten/10113904")]
        return order_test

        # 切换回淘宝窗口
        self.driver.switch_to_window(self.driver.window_handles[0])

        result = []

        if self.__is_logined is False:
            if self.__login() is False:
                return result
            else:
                self.__is_logined = True

        # 1.进入待发货订单页面
        self.driver.get(self.__orders_url)
        while True:
            # 2.获取当前页面的订单信息
            time.sleep(2)  # 两秒等待页面加载
            _orders = self.__get_orders_page()
            result.extend(_orders)
            try:
                # 3.获取下一页按钮
                next_page_li = self.driver.find_element_by_class_name("pagination-next")
                # 4.判断按钮是否可点击，否则退出循环
                next_page_li.get_attribute("class").index("pagination-disabled")
                # 到达最后一页
                break
            except ValueError:
                # 跳转到下一页
                print(next_page_li.find_element_by_tag_name("a").text)
                next_page_li.click()
                time.sleep(1)
            except exceptions.NoSuchElementException:
                pass
        return result

    def unshelve(self):
        # 切换回淘宝窗口
        self.driver.switch_to_window(self.driver.window_handles[0])

        if self.__is_logined is False:
            if self.__login() is False:
                return False
            else:
                self.__is_logined = True

        try:
            # 1.进入正出售宝贝页面
            self.driver.get(self.__auction_url)
            # 2.点击下架
            choose_checkbox = self.driver.find_element_by_xpath(
                "//*[@id='J_DataTable']/table/tbody[1]/tr[1]/td/input[1]")
            choose_checkbox.click()
            unshelve_btn = self.driver.find_element_by_xpath(
                "//*[@id='J_DataTable']/div[2]/table/thead/tr[2]/td/div/button[2]")
            unshelve_btn.click()
            return True
        except:
            return False

    def shelve(self):
        # 切换回淘宝窗口
        try:
            self.driver.switch_to_window(self.driver.window_handles[0])
        except exceptions:
            print (exceptions)

        if self.__is_logined is False:
            if self.__login() is False:
                return False
            else:
                self.__is_logined = True

        '''# 1.进入仓库宝贝页面
        self.driver.get(self.__repository_url)
        # 2.点击上架
        try:
            choose_checkbox = self.driver.find_element_by_xpath("//*[@id='J_DataTable']/table/tbody[1]/tr[1]/td/input")
            choose_checkbox.click()
            shelve_btn = self.driver.find_element_by_xpath(
                "//*[@id='J_DataTable']/div[3]/table/tbody/tr/td/div/button[2]")
            shelve_btn.click()
        except exceptions.NoSuchElementException:
            pass
        '''
    def delivered(self, orderId):
        # 切换回淘宝窗口
        self.driver.switch_to_window(self.driver.window_handles[0])

        if self.__is_logined is False:
            if self.__login() is False:
                return False
            else:
                self.__is_logined = True
        try:
            # 1.进入确认发货页面
            self.driver.get(self.__deliver_url + orderId)
            no_need_logistics_a = self.driver.find_element_by_xpath("//*[@id='dummyTab']/a")
            no_need_logistics_a.click()
            self.driver.find_element_by_id("logis:noLogis").click()
            time.sleep(1)
            return True
        except:
            return False

    def exists_refunding(self):
        # 切换回淘宝窗口
        self.driver.switch_to_window(self.driver.window_handles[0])

        if self.__is_logined is False:
            if self.__login() is False:
                return False
            else:
                self.__is_logined = True
        try:
            # 1.进入退款页面
            self.driver.get(self.__refunding_url)
            self.driver.find_element_by_class_name("item-mod__trade-order___2LnGB trade-order-main")
            return True
        except exceptions.NoSuchElementException:
            return False

    def webww_login(self):
            try:
                    WebDriverWait(self.driver, 20, 0.1).until(lambda x: x.find_element_by_xpath("//*[@id='tstart-plugin-tdog']"))
                    webww_base = self.driver.find_element_by_xpath("//*[@id='tstart-plugin-tdog']")
                    webww_base.click()
                    #print(u"点击旺旺图标")
            except :
                return
            
            js = "window.scrollTo(document.body.scrollWidth,document.body.scrollHeight)" 
            self.driver.execute_script(js)
            #self.driver.execute_script("arguments[0].click()",webww_base)
            try:
                    WebDriverWait(self.driver, 2, 0.1).until(lambda x: x.find_elements_by_class_name("use-webww-btn"))
                    select_ww = self.driver.find_elements_by_class_name("use-webww-btn")
                    for select in select_ww:
                        if select.text == u"继续使用网页版":
                            if select.is_displayed() is True:
                                self.action.click(select).perform()
                    try:
                            WebDriverWait(self.driver, 2, 0.1).until(lambda x: x.find_elements_by_class_name("tstart-item-tips-btn"))
                            confirm = self.driver.find_elements_by_class_name("tstart-item-tips-btn")
                            if confirm[0].is_displayed():
                                    if confirm[0].text == u"确定":
                                         confirm[0].click()
                                    else:
                                        confirm[1].click()
                                       
                    except Exception :
                        #print(traceback.print_exc())
                        pass
            except Exception :
                    pass
                    #print (u"已经登录旺旺")

            print (u"开启web旺旺成功！")
            return True
    def get_messge(self):
        global sql_user
        global conn
        messg_winds = self.driver.find_elements_by_class_name("tdog-popup")
        now_msg_flag = 0
        for user_wind in messg_winds:
            if user_wind.is_displayed():
                now_msg_flag = 1
                user = user_wind.find_elements_by_class_name("tdog-talk-username")
                msg = user_wind.find_elements_by_class_name("tdog-talk-content")
                msg_time = user_wind.find_elements_by_class_name("tdog-talk-time")
                for i in range(0, len(user), 1):
                    now_msg = msg[i].text
                    now_time = msg_time[i].text
                    now_name = user[i].text
                    msg_exist = 0
                    print ("当前用户：", user[i].text, "消息:", now_msg, "时间:", now_time)
                    if user[i].text != self.nickname:
                        if user[i].text=='':
                            continue
                        sql_user.execute("select * from user where name='%s'" % (user[i].text))
                        user_line = sql_user.fetchall()
                        for line in user_line:
                            if line[1] == now_time:
                                msg_exist = 1
                                break
                        if msg_exist == 0:
                            sql_user.execute("insert into user (name,time,msg,shop,state,shopuser)\
                                                   values ('%s','%s','%s','%s',%s,'%s')" % (
                            now_name, now_time, now_msg, 0, 0, "5oo0o0o5"))
                            conn.commit()
                user_wind.find_element_by_class_name("tdog-popup-close").click()
    def send_msg(self):
        #发送模式
        self.driver.find_element_by_xpath("//*[@id='tstart-plugin-tdog']").click()
        time.sleep(0.1)
        messg_winds = self.driver.find_elements_by_class_name("tdog-popup")
        now_msg_flag = 0
        for user_wind in messg_winds:
            if user_wind.is_displayed():
                now_msg_flag = 1
        if now_msg_flag == 1:
            self.get_messge()
            return
        n = 0
        while True:
            try:
                recentlists = self.driver.find_elements_by_class_name("tdog-recentlist-item")
                for recentlist in recentlists:

                    item = recentlist.find_element_by_class_name("tdog-user-name")
                    if item.is_displayed() == False:
                        #self.driver.find_element_by_xpath("//*[@id='tstart-plugin-tdog']").click()
                        time.sleep(0.1)
                
                    item_name = item.text
                    #item_name = item.get_attribute("id")
                    sql_user.execute("select * from user where state=0")
                    user_line = sql_user.fetchall()

                    # 从数据库中遍历没用发送的消息
                    for user in user_line:
                        if user[5] == item_name:
                            if item.is_displayed():
                                    recentlist.click()
                                    time.sleep(0.1)
                            else:
                                    return
                            #找到当前打开的发送窗口
                            messg_winds = self.driver.find_elements_by_class_name("tdog-popup")
                            for user_wind in messg_winds:
                                #谁是可见的就是 刚刚打开的发送窗口/html/body/div[6]/div[2]/div[2]/div[1]/div/div[1]/div[4]
                                if user_wind.is_displayed():
                                    input_block = user_wind.find_element_by_class_name("tdog-popup-talkinput")
                                    m_input = input_block.find_element_by_xpath("//textarea")
                                    m_input.click()
                                    time.sleep(0.1)
                                    m_input.send_keys(user[2])
                                    user_wind.find_element_by_class_name("tdog-popup-send").click()
                                    time.sleep(0.1)
                                    sql_user.execute("update user set state=1 where time='%s' and name='%s'" % (user[1],user[0]))
                                    conn.commit()
                break
            except Exception:
                print(traceback.print_exc())
                n += 1
                if n > 10:
                    break

    def get_msg(self):
        #try:
            global sql_user
            global conn
            self.webww_login()
            WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_xpath("//*[@id='tstart-plugin-tdog']"))
            self.driver.find_element_by_xpath("//*[@id='tstart-plugin-tdog']").click()
            time.sleep(0.1)
            messg_winds = self.driver.find_elements_by_class_name("tdog-popup")
            now_msg_flag = 0
            
            for user_wind in messg_winds:
                if user_wind.is_displayed():
                    now_msg_flag = 1
            if now_msg_flag == 1:
                self.get_messge()
            elif now_msg_flag == 0:
                try:
                    WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_class_name("tdog-recentlist"))
                    recentlist = self.driver.find_element_by_class_name("tdog-recentlist")
                except:
                        self.driver.get_screenshot_as_file("4.png")
                try:
                    items = recentlist.find_elements_by_class_name("tdog-recentlist-item")
                except:
                    return
                for item in items:
                    #是否有未读消息
                    try :
                        msg_count = item.find_element_by_class_name("tdog-msg-count").text
                        if len(msg_count):
                            item.click()
                            for user_wind in messg_winds:
                                if user_wind.is_displayed():
                                    self.get_messge()
                    except:
                        pass
if __name__ == '__main__':
    # 初始化
    chrome_options = webdriver.ChromeOptions()
    #chrome_options = webdriver.FirefoxOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    conn = sqlite3.connect('msg_user.db')
    sql_user = conn.cursor()
    
    #dis = Display(visible=0,size=(1920,1080))
    #dis.start()
    climber = TaobaoClimber("18349236980","ys940330")
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    #从USER_AGENTS列表中随机选一个浏览器头，伪装浏览器
    dcap['Chrome.page.settings.userAgent'] = ('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36')
    #dcap["phantomjs.page.settings.userAgent"] = (random.choice(USER_AGENTS))
    # 不载入图片，爬页面速度会快很多
    #dcap["phantomjs.page.settings.loadImages"] = False
    # 设置代理
    #service_args = ['--proxy=127.0.0.1:9999','--proxy-type=socks5']
    #打开带配置信息的phantomJS浏览器
    #TaobaoClimber.driver = webdriver.Chrome()
    TaobaoClimber.driver = webdriver.Chrome(options = chrome_options)
    #TaobaoClimber.driver = webdriver.PhantomJS(desired_capabilities=dcap,service_args=['--ignore-ssl-errors=true'])
    #TaobaoClimber.driver = webdriver.PhantomJS(desired_capabilities=dcap,service_args=service_args)                
    # 隐式等待5秒，可以自己调节
    #TaobaoClimber.driver.implicitly_wait(5)
    # 设置10秒页面超时返回，类似于requests.get()的timeout选项，driver.get()没有timeout选项
    # 以前遇到过driver.get(url)一直不返回，但也不报错的问题，这时程序会卡住，设置超时选项能解决这个问题。
    #TaobaoClimber.driver.set_page_load_timeout(10)
    # 设置10秒脚本超时时间
    #TaobaoClimber.driver.set_script_timeout(10)
    #TaobaoClimber.driver = webdriver.Chrome(chrome_options=chrome_options)  # 应将浏览器驱动放于python根目录下，且python已配置path环境变量
    #webdriver.support.wait.WebDriverWait(TaobaoClimber.driver, 10, poll_frequency=0.5, ignored_exceptions=None)
    #cd = driver.find_element_by_class_name("ss")
    #cd.send_keys()
    TaobaoClimber.action = ActionChains(TaobaoClimber.driver)
    TaobaoClimber.driver.maximize_window()  # 浏览器最大化
    #TaobaoClimber.driver.execute_script("window.open('')")
    TaobaoClimber.shop_home = "https://shop150536661.taobao.com/shop/view_shop.htm?spm=a211vu.server-web-home.category.d53.64f02d583cnC94&mytmenu=mdianpu&user_number_id=2291133898"
    #climber.shelve()
    climber.driver.get(climber.shop_home)
    with open("cookies.txt", "r") as fp:
        cookies = json.load(fp)
        for cookie in cookies:
            # cookie.pop('domain')  # 如果报domain无效的错误
            climber.driver.add_cookie(cookie)
    climber.driver.get(climber.shop_home)
    climber.webww_login()
    while True:
        climber.get_msg()
        time.sleep(0.5)
        climber.send_msg()
        with open("cookies.txt", "w") as fp:
            json.dump(cookies, fp)
        time.sleep(0.5)
    #cookies = climber.driver.get_cookies()
    '''while True:
        # 循环爬取订单
        orders = climber.climb()
        for order in orders:
            print("淘宝订单产生：订单号：%s\t订单日期：%s \t买家：%s\t备注：%s" % order)
        # 每30秒抓一次
        time.sleep(30)
	'''
