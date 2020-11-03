class PPConfig:
    def __init__(self, app_key: str = 'vsd0Rm5ph2sS2uaK', betex_region: str = 'GBR', jurisdiction: str = 'intl',
                 currency: str = 'GBP', locale: str = 'en_GB', language: str = 'en', region: str = 'UK',
                 timezone: str = 'Europe/London'):
        self.app_key = app_key
        self.betex_region = betex_region
        self.jurisdiction = jurisdiction
        self.currency = currency
        self.locale = locale
        self.language = language
        self.region = region
        self.timezone = timezone


all_sports = ['American Football', 'Australian Rules', 'Baseball', 'Basketball', 'Boxing', 'Cricket', 'Current Affairs',
              'Cycling', 'Darts', 'Esports', 'Football', 'Gaelic Games', 'Golf', 'Greyhound Racing', 'Handball',
              'Horse Racing', 'Ice Hockey', 'Lotteries', 'Mixed Martial Arts', 'Motor Sport', 'Politics', 'Pool',
              'Rugby League', 'Rugby Union', 'Snooker', 'Special Bets', 'Table Tennis', 'Tennis', 'Virtual Sports',
              'Volleyball', 'Winter Sports']
other_menu_items = ['Home', 'Search', 'In-Play']
page_id_from_text = {**{x: x.upper() for x in (all_sports + other_menu_items)},
                     'Home': 'HOMEPAGE'}
page_text_from_id = {v: k for k, v in page_id_from_text.items()}
