from selenium import webdriver
import argparse
import time

class instagramAccount():

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.followers = []
        self.followings = []

    def login(self, igdriver):

        # Login
        self.followers = igdriver.login(self.username, self.password)

    def retrieveFollowers(self, igdriver):

        # Get Followers
        self.followers = igdriver.getList(self.username, 'followers')

    def retrieveFollowings(self, igdriver):

        # Get Followings
        self.followings = igdriver.getList(self.username, 'following')


class IGWebDriver():



    def __init__(self):
        self.mydriver = webdriver.Chrome()
        self.mydriver.maximize_window()

        self.login_url = 'https://www.instagram.com/accounts/login/'
        self.popup_class = '_gs38e'
        self.f_class = '_6e4x5'
        self.name_class = '_9mmn5'
        self.uname_class = '_2g7d5 notranslate _o5iw8'
        self.unfollow_class = '_qv64e _t78yp _r9b8f _njrw0'

        self.xpaths = { 'usernameTxtBox' : "//input[@name='username']",
                        'passwordTxtBox' : "//input[@name='password']",
                        'submitButton' :   "//*[@id='react-root']/section/main/div/article/div/div[1]/div/form/span/button"
                      }


    def login(self, username, password):
        self.mydriver.get(self.login_url)

        #Enter Username
        self.mydriver.find_element_by_xpath(self.xpaths['usernameTxtBox']).clear()
        self.mydriver.find_element_by_xpath(self.xpaths['usernameTxtBox']).send_keys(username)

        #Enter Password
        self.mydriver.find_element_by_xpath(self.xpaths['passwordTxtBox']).clear()
        self.mydriver.find_element_by_xpath(self.xpaths['passwordTxtBox']).send_keys(password)

        #Click Login button
        self.mydriver.find_element_by_xpath(self.xpaths['submitButton']).click()

        time.sleep(5)

    def naviagateToUser(self, uname):
        user_url = "https://www.instagram.com/%s/" % uname
        self.mydriver.get(user_url)
        time.sleep(3)

    def getList(self, username, type='followers'):

        self.naviagateToUser(username)

        # Open Followers/Following
        self.mydriver.find_element_by_xpath("//a[@href='/%s/%s/']" % (username,type)).click()

        time.sleep(2)

        # Scroll to Bottom
        SCROLL_PAUSE_TIME = 0.1
        i = 0
        while True:
            try:
                n = 19 * i

                # Scroll down to nth item
                self.mydriver.execute_script(
                    "document.getElementsByClassName('%s')[%d].scrollIntoView()" % (self.f_class, n))

                # Wait to load page
                time.sleep(SCROLL_PAUSE_TIME)

                i += 1
            except:
                break

        result = []

        try:
            # Get All Elements
            all_elements = self.mydriver.find_elements_by_xpath("//li[@class='%s']" % self.f_class)



            # Add to List
            for element in all_elements:
                name = element.find_element_by_xpath(".//div[@class='%s']" % self.name_class).text
                uname = element.find_element_by_xpath(".//a[@class='%s']" % self.uname_class).text
                result.append((uname, name))
        except:
            print 'Error while looking for %s' % type

        return result

    def unfollow(self, uname):

        self.naviagateToUser(uname)

        self.mydriver.find_element_by_xpath("//button[@class='%s']" % self.unfollow_class).click()

        time.sleep(3)

    def quit(self):
        self.mydriver.quit()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Unfollows people On Instagram that aren't following You back.")
    parser.add_argument('-u','--user', help='Username to Use', required=True)
    parser.add_argument('-p','--password', help='Password to Use', required=True)
    parser.add_argument('-t','--test', help='Prints List Only', required=False, action='store_true')
    parser.add_argument('-f','--force', help='Force Unfollows', required=False, action='store_true')
    args = vars(parser.parse_args())

    igdriver = IGWebDriver()

    username = args['user']
    password = args['password']

    account = instagramAccount(username, password)

    account.login(igdriver)

    account.retrieveFollowers(igdriver)
    account.retrieveFollowings(igdriver)

    print 'Followers:'
    for f in account.followers:
        print "'%s' - '%s'" % (f[0], f[1])
    print

    print 'Following:'
    for f in account.followings:
        print "'%s' - '%s'" % (f[0], f[1])
    print

    unfollow_list = []

    # Following, but not Follower
    print 'Following, but not Follower'
    for f in account.followings:
        if f not in account.followers:
            print '"%s" - "%s"' % (f[0], f[1])
            unfollow_list.append(f[0])
    print

    # Follower, but not Following
    print 'Follower, but not Following'
    for f in account.followers:
        if f not in account.followings:
            print '"%s" - "%s"' % (f[0], f[1])
    print

    if not args['test']:
        for uname in unfollow_list:
            if args['force'] or raw_input("Unfollow %s? (Y/N):" % uname) == 'Y':
                igdriver.unfollow(uname)
                print 'Unfollowed %s' % uname

    igdriver.quit()

