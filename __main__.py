import json
from libs.web_scraping import WebScraping


class Scraper(WebScraping):
    
    def __init__(self):
        
        # Start scraper
        super().__init__()
        
        # Pages
        self.home = "https://www.irp.es/?lng=es&modulo=Predicacion"
        
        # Counters and data
        self.category_index = 0
        self.categories = self.__get_categories__()
    
    def __get_categories__(self) -> list:
        """ Return a list of categories titles to be scraped """
        
        selectors = {
            "wrapper": '.Temas table',
            "category": '.TemaValorT'
        }
        
        self.set_page(self.home)
        self.refresh_selenium()
        
        categories = []
        wrappers = self.get_elems(selectors["wrapper"])
        for wrapper_id in range(len(wrappers)):
            selector_wrapper = f'{selectors["wrapper"]}:nth-child({wrapper_id + 1})'
            selector_category = f'{selector_wrapper} {selectors["category"]}'
            category = self.get_text(selector_category)
            if category:
                categories.append(category)
            
        return categories
    
    def __go_next_category__(self) -> bool:
        """ Go to the next category
        
        Return:
            bool: True if there is a next category, False otherwise
        """
                
        selectors = {
            "wrapper": '.Temas table',
        }
        
        current_category = self.categories[self.category_index]
        print(f"Scraping category: {current_category}...")
        
        self.set_page(self.home)
        
        # Find and click on the category
        selector_wrapper = f'{selectors["wrapper"]}:nth-child({self.category_index + 3})'
        self.click_js(selector_wrapper)
        self.refresh_selenium()
        
        self.category_index += 1
        
        # Validate redirect
        if self.driver.current_url == self.home:
            return False
        return True
    
    def __get_sermons_data__(self) -> list:
        """ Return a a list of dictionary with a single the sermon data
        
        Args:
            sermon_elem (WebElement): sermon element
        
        Return:
            dict: sermon data
            Structure:
            [
                {
                    "title": str,
                    "reading": str,
                    "author": str,
                    "number": int,
                    "date": str,
                    "url": str,
                },
                ...
            ]
        """
        
        selectors = {
            "sermon": '.Sermones table:not(.SermonEspacio)',
            "video": "iframe",
            "play_button": "a.MenuItemLinea",
        }
        rows = ["title", "reading", "author", "number", "date"]
        
        # Loop sermons
        sermons_data = []
        sermons = self.get_elems(selectors["sermon"])
        for sermon_index in range(len(sermons)):
            
            sermon_data = {}
            selector_sermon = f'{selectors["sermon"]}:nth-child({sermon_index + 1})'
            
            # Get sermon data
            for item in rows:
                item_index = rows.index(item)
                selector_item = f'{selector_sermon} tr:nth-child({item_index + 1}) '\
                    'td:nth-child(2)'
                value = self.get_text(selector_item)
                sermon_data[item] = value
                
            # Get youtube video
            self.click_js(selector_sermon)
            self.switch_to_tab(1)
            self.refresh_selenium(back_tab=1)
            iframe_src = self.get_attrib(selectors["video"], "src")
            sermon_data["video"] = iframe_src
            
            # Get mp3 audio
            self.click_js(selectors["play_button"])
            self.refresh_selenium(back_tab=1)
            mp3_url = self.driver.current_url
            sermon_data["mp3"] = mp3_url
            
            # Go back to the main tab
            self.close_tab()
            self.switch_to_tab(0)
            
            sermons_data.append(sermon_data)
        
        print(f"\t{len(sermons_data)} sermons scraped.")
        
        return sermons_data
            
    def autorun(self):
        """ Scrape data from all sermons in the website """
        
        # Main loop
        categories_data = {}
        more_categories = True
        while more_categories:
            
            try:
                category = self.categories[self.category_index]
            except IndexError:
                break
            
            # Extract sermons data
            more_categories = self.__go_next_category__()
            sermons_data = self.__get_sermons_data__()
            
            # Save data
            categories_data[category] = sermons_data
            
            # Save data in json in each iteration
            with open("data.json", "w") as file:
                json.dump(categories_data, file)
        
        
if __name__ == "__main__":
    scraper = Scraper()
    scraper.autorun()