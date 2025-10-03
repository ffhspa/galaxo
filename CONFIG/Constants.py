import os
from CONFIG.LogLevel import LogLevel
from LOGGER.Logger import Logger

class Constants:
    
    LOG_LEVEL = LogLevel.ERROR  #INFO, ERROR,DEBUG,WARNING
    #Logger
    BASE_PATH = __import__('pathlib').Path(__file__).resolve().parents[1]  
    LOG_PATH =   os.path.join(BASE_PATH,'')
    LOG_FILE_NAME = "galaxo.log"
    CACHE_DIR_IMAGES = os.path.join(BASE_PATH,'Images') 
    LOGGER = Logger(LOG_PATH,LOG_FILE_NAME,LOG_LEVEL).get_logger()
    JSON_PATH = os.path.join(BASE_PATH, "galaxo_data.json")
    JSON_BACKUP_PATH = os.path.join(BASE_PATH,'Backup')
    JSON_BACKUP_FILE_NAMES = "galaxo_data_backup_"

    #GUI
    TITLE="Galaxus/Digitec Produkte"
    IMAGE_SIZE =(250, 250)
    ITEM_WIDTH = 460
    ITEM_HEIGHT = 420
    CHAR_LIMIT = 40
    WRAPLENGTH = 240
    NUM_COLUMNS = 4
    PADDING_X = 10
    PADDING_Y = 10
    BG_COLOR = "#F0F0F0"
    DEFAULT_BORDER_COLOR = "#a6a2a1"
    REACHED_MIN_BORDER_COLOR = "#1EDD1A"
    REACHED_MAX_PRICE_COLOR = "#FF6B6B"
    CHANGED_PRICE_BORDER_COLOR = "#b134eb"
    CHANGED_STOCK_BORDER_COLOR = "#F4C35A"
    CHANGED_BOTH_BORDER_COLOR = "#cc33a6"
    PRODUCT_NOT_AVAILABLE_COLOR = "#000000"
    SELECTED_COLOR = "#CCE5FF"
    FONT = "Arial"
    FONT_SIZE_VERY_SMALL = 9
    FONT_SIZE_SMALL = 11
    FONT_SIZE_MEDIUM = 14
    FONT_SIZE_LARGE = 15
    FONT_SIZE_XL = 20
    FONT_SIZE_XXL = 21
    CATEGORY_DEFAULT = 'Alle Kategorien'
    THEME = 'clam' # alt, clam, classic, default
    
    #GUI Product Info
    PRODUCT_INFO_CURRENT_PRICE=''
    PRODUCT_INFO_BRAND_NAME=''
    PRODUCT_INFO_PRODUCT_NAME =''
    PRODUCT_INFO_MIN_PRICE='Min'
    PRODUCT_INFO_MAX_PRICE='Max'
    PRODUCT_INFO_PREISVERLUST_PERCENTAGE='Verlust'
    PRODUCT_INFO_STOCK_COUNT='Lager'
    #PRODUCT_INFO_OLD_STOCK_COUNT='Lagerbestand Alt'
    PRODUCT_INFO_STOCK_COUNT_CHANGE='Lageränderung'
    PRODUCT_INFO_PRICE_CHANGE='Preisänderung'
    PRODUCT_INFO_OLD_PRICE='Vorheriger Preis'
    PRODUCT_INFO_OLD_PRICE_PERCENTAGE="Änderung"
    PRODUCT_INFO_CATEGORY_NAME =''
    PRODUCT_INFO_PERCENTAGE_ITEMS = {'preisverlust_percentage'}
    PRODUCT_INFO_LABEL_CONTEXT_ITEMS = {'current_price','old_price','min_price','max_price','preisverlust_percentage','price_change'}
    
    PRODUCT_PERCENTAGE_CHANGE = 2
    
    #API
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
        'Accept': '*/*',
        'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://www.digitec.ch',
        'Content-Type': 'application/json',
        'x-dg-language': 'de-CH',
        'x-dg-scrumteam': 'Isotopes',
        'x-dg-routename': '/productDetail',
        'x-dg-portal': '22',
        'Origin': 'https://www.digitec.ch',
        'DNT': '1',
        'Connection': 'keep-alive'
    }
    BASE_URL = 'https://www.galaxus.ch/api/graphql'
    BASE_URL_HISTORY = "https://www.galaxus.ch/graphql/o/690220b748da1f61bfd7e73d7bf89b53/priceChartQuery" # kann sich ändern
                                    
    
    #Sort
    SORT_PRICE_UP = "Preis aufsteigend"
    SORT_PRICE_DOWN = "Preis absteigend"
    SORT_TIME = "Zeit absteigend"
    SORT_VERLUST = "Verlust absteigend"
    
    SORT_DEFAULT = SORT_PRICE_UP
            
    PRODUCT_FIELD_CONFIG = {
            'base': {
                'current_price':         (PRODUCT_INFO_CURRENT_PRICE, FONT_SIZE_XXL, "bold"),
                'brand_name':            (PRODUCT_INFO_BRAND_NAME, FONT_SIZE_XL, "bold"),
                'product_name':          (PRODUCT_INFO_PRODUCT_NAME, FONT_SIZE_LARGE, None),
                'min_price':             (PRODUCT_INFO_MIN_PRICE, FONT_SIZE_MEDIUM, None),
                'max_price':             (PRODUCT_INFO_MAX_PRICE, FONT_SIZE_MEDIUM, None),
                'preisverlust_percentage': (PRODUCT_INFO_PREISVERLUST_PERCENTAGE, FONT_SIZE_MEDIUM, None),
                'stock_count':           (PRODUCT_INFO_STOCK_COUNT, FONT_SIZE_MEDIUM, None),
                'category_name':         (PRODUCT_INFO_CATEGORY_NAME, FONT_SIZE_SMALL, None),
            },
            'price_change': {
                'current_price':         (PRODUCT_INFO_CURRENT_PRICE, FONT_SIZE_XXL, "bold"),
                'brand_name':            (PRODUCT_INFO_BRAND_NAME, FONT_SIZE_XL, "bold"),
                'product_name':          (PRODUCT_INFO_PRODUCT_NAME, FONT_SIZE_MEDIUM, None),
                'min_price':             (PRODUCT_INFO_MIN_PRICE, FONT_SIZE_SMALL, None),
                'max_price':             (PRODUCT_INFO_MAX_PRICE, FONT_SIZE_SMALL, None),
                'preisverlust_percentage': (PRODUCT_INFO_PREISVERLUST_PERCENTAGE, FONT_SIZE_SMALL, None),                                            
                'price_change':          (PRODUCT_INFO_PRICE_CHANGE, FONT_SIZE_SMALL, None),
                'old_price':             (PRODUCT_INFO_OLD_PRICE, FONT_SIZE_SMALL, None),
                'old_price_percentage':  (PRODUCT_INFO_OLD_PRICE_PERCENTAGE, FONT_SIZE_SMALL, None),
                'stock_count':           (PRODUCT_INFO_STOCK_COUNT, FONT_SIZE_SMALL, None),    
                'category_name':         (PRODUCT_INFO_CATEGORY_NAME, FONT_SIZE_VERY_SMALL, None),                
            },
            'stock_change': {
                'current_price':         (PRODUCT_INFO_CURRENT_PRICE, FONT_SIZE_XXL, "bold"),
                'brand_name':            (PRODUCT_INFO_BRAND_NAME, FONT_SIZE_XL, "bold"),
                'product_name':          (PRODUCT_INFO_PRODUCT_NAME, FONT_SIZE_LARGE, None),
                'min_price':             (PRODUCT_INFO_MIN_PRICE, FONT_SIZE_MEDIUM, None),
                'max_price':             (PRODUCT_INFO_MAX_PRICE, FONT_SIZE_MEDIUM, None),
                'preisverlust_percentage': (PRODUCT_INFO_PREISVERLUST_PERCENTAGE, FONT_SIZE_MEDIUM, None),
                'stock_count_change':    (PRODUCT_INFO_STOCK_COUNT, FONT_SIZE_MEDIUM, None),
                'category_name':         (PRODUCT_INFO_CATEGORY_NAME, FONT_SIZE_SMALL, None),
            },
            'both': {
                'current_price':         (PRODUCT_INFO_CURRENT_PRICE, FONT_SIZE_XL, "bold"),
                'brand_name':            (PRODUCT_INFO_BRAND_NAME, FONT_SIZE_MEDIUM, "bold"),
                'product_name':          (PRODUCT_INFO_PRODUCT_NAME, FONT_SIZE_SMALL, None),
                'min_price':             (PRODUCT_INFO_MIN_PRICE, FONT_SIZE_SMALL, None),
                'max_price':             (PRODUCT_INFO_MAX_PRICE, FONT_SIZE_SMALL, None),
                'preisverlust_percentage': (PRODUCT_INFO_PREISVERLUST_PERCENTAGE, FONT_SIZE_SMALL, None),
                'price_change':          (PRODUCT_INFO_PRICE_CHANGE, FONT_SIZE_VERY_SMALL, None),
                'old_price':             (PRODUCT_INFO_OLD_PRICE, FONT_SIZE_VERY_SMALL, None),
                'old_price_percentage':  (PRODUCT_INFO_OLD_PRICE_PERCENTAGE, FONT_SIZE_VERY_SMALL, None),
                'stock_count_change':    (PRODUCT_INFO_STOCK_COUNT, FONT_SIZE_VERY_SMALL, None),                                                               
                'category_name':         (PRODUCT_INFO_CATEGORY_NAME, FONT_SIZE_VERY_SMALL, None),                
            }
        }
