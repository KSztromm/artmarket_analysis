class ArtScrap:
    """Set of methods used to get data from ArtMarket websites"""
    def __init__(self, driver, output):
        self.driver = driver
        self.output = output


    def get(self, url):
        self.driver.get(url)


    def get_metadata(self, column_name, xpath_general, xpath_detailed, att='innerText', start=0, step=1):
        """Get specific value of all elements with same xpath on a given page"""
        elements = self.driver.find_elements_by_xpath(xpath_general)

        for i in range(start, len(elements), step):
            data = elements[i].find_element_by_xpath(xpath_detailed).get_attribute(att)

            self.output[column_name].append(data)


    def apply_to_multiple_pages(url, func, args, kwargs):
        """Walks through all existing pages of a given website location"""
        last_page = 0
        page = 0
        self.driver.get(url)

        while last_page == 0:
            page += 1
            func(*args, **kwargs)


