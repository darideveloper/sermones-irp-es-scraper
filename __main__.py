from libs.web_scraping import WebScraping


class Scraper(WebScraping):
    
    def __init__(self):
        
        # Start scraper
        super().__init__()
    
    def __get_categories__(self) -> list:
        """ Return a list of categories titles to be scraped """
        
        selectors = {
            "wrapper": '[class="Temas"] table',
            "category": '.TemaValorT'
        }
        
        self.set_page("https://www.irp.es/?lng=es&modulo=Predicacion")
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
    
    def __get_sermon_data__(self) -> dict:
        """ Return a dictionary with a single the sermon data
        
        Return:
            dict: sermon data
            Structure:
            {
                "title": str,
                "reading": str,
                "author": str,
                "number": int,
                "date": str,
                "url": str,
            }
        """
        pass
    
    def autorun(self):
        """ Scrape data from all sermons in the website """
        
        categories = self.__get_categories__()
        print(categories)
        
        
if __name__ == "__main__":
    scraper = Scraper()
    scraper.autorun()