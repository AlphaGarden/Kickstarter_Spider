import scrapy,json
from scrapy.selector import Selector
from scrapy.exceptions import CloseSpider
from DailyKickstarter.items import ProjectInfo
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.kickstarter.com/discover/advanced?state=live&category_id=12&woe_id=23424977&sort=popularity&seed=2572311&page=%d"

class DailystarterSpider(scrapy.Spider):
    name = "dailykickstarter"
    allowed_domains = ["kickstarter.com"]
    start_urls = [URL % 1]

    def __init__(self):
        self.popularity = 0
        self.page_number = 0

    def formatStr(self, input):
        return str(input.encode('utf-8')).strip()

    def formatNum(self, input):
        return str(input).strip()

    def formatList(self, input):
        return map(str.strip, [x.encode('ascii', 'ignore').decode('ISO-8859-1').encode('utf-8') for x in input])


    def parse(self, response):
        self.page_number += 1
        print self.page_number
        print "----------"
        sel = Selector(response)
        base = '//div[@id="projects_list"]/div[contains(@class, "grid-row")]/div[contains(@class, "js-react-proj-card")]/'
        project = sel.xpath(base + '@data-project').extract()
        if not project:
            raise CloseSpider('No more pages')

        self.popularity = 0
        for p in project:
            pStr = "{" + str(p.encode('utf-8'))[1: -1] + "}"
            projectJson = json.loads(pStr)

            projectInfo = ProjectInfo()
            projectInfo["ProjectTitle"] = self.formatStr(projectJson['name'])
            projectInfo["ProjectDescription"] = self.formatStr(projectJson['blurb'])
            projectInfo["CreatedBy"] = self.formatStr(projectJson['creator']['name'])

            projectInfo["AmountAsked"] = self.formatNum(projectJson['goal'])
            projectInfo["AmountPledged"] = self.formatNum(projectJson['pledged'])
            projectInfo["Current_currency"] = self.formatStr(projectJson['current_currency'])
            projectInfo["TotalBackers"] = self.formatNum(projectJson['backers_count'])
            projectInfo["GoalFinishedPercentage"] = self.formatNum(projectJson['percent_funded'])

            project_url = str(projectJson['urls']['web']['project'].encode('utf-8'))

            projectInfo["ProjectLink"] = project_url

            self.popularity += 1

            request = scrapy.Request(project_url, callback=self.parse_project_detail)
            request.meta["projectInfo"] = projectInfo

            yield request
            curPage = response.request.url[response.request.url.index("page=")+5:]
            projectInfo["Popularity"] = 12*(int(curPage) - 1) + self.popularity

        yield scrapy.Request(URL % self.page_number)


    def parse_project_detail(self, response):
        projectInfo = response.meta['projectInfo']
        sel = Selector(response)
        projectInfo['TotalComments'] = self.formatStr(sel.xpath('//span[@class="count"]/data/@data-value').extract()[0])

        driver = webdriver.Firefox()
        driver.get(response.request.url)
        wait = WebDriverWait(driver, 5)

        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@class="ml5 ml0-lg"]/div/span[@class="block type-16 type-24-md medium soft-black"]'))
            )

            items = driver.find_elements(By.XPATH, '//div[@class="ml5 ml0-lg"]/div/span[@class="block type-16 type-24-md medium soft-black"]')
            text = items[0].text

        except Exception as e:
            print(e)
            projectInfo['TimeToGo'] = 0

        else:
            print("this is text:" + text)
            projectInfo['TimeToGo'] = self.formatNum(text)
            return projectInfo

        finally:
            driver.quit()