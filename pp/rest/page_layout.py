import json
import time
from pathlib import Path
from random import uniform
from typing import Any, Union
from urllib.parse import urlencode

import requests

from pp.config import PPConfig


class PageLayout:
    def __init__(self, tabs: list[dict[str, Union[str, int, list[int]]]], default_tab: int,
                 page_info: dict[str, Union[str, int]], cards: dict[int, dict[Any]]):
        self.tabs = tabs
        self.default_tab = default_tab
        self.page_info = page_info
        self.cards = cards


def load_mocked_page(page: str) -> dict:
    if page == 'HOMEPAGE':
        file = 'homepage.json'
    elif page == 'IN-PLAY':
        file = 'in-play.json'
    elif page == 'FOOTBALL':
        file = 'football.json'
    else:
        raise Exception('Tried to load unknown mocked page: ' + page)
    with open(Path(__file__).parent / 'mock_data' / file, 'r') as f:
        json_data = json.load(f)
    time.sleep(uniform(0.045, 0.2))

    return json_data


config = PPConfig()
default_strands_keys = {
    '_ak': config.app_key,
    'betexRegion': config.betex_region,
    'capiJurisdiction': config.jurisdiction,
    'currencyCode': config.currency,
    'language': config.language,
    'regionCode': config.region,
    'timezone': config.timezone,
    'exchangeLocale': config.locale
}


def query_string_ified(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return str(value).lower()
    else:
        return str(value)


def make_strands_request(slug: str, custom_options: dict[str, Any]) -> dict:
    clean = {key: query_string_ified(value) for key, value in {**default_strands_keys, **custom_options}.items()}
    query_string = urlencode(clean)
    response = requests.get(
        headers={'User-Agent': None, 'Accept': 'application/json'},
        url="https://strands.paddypower.com/sdspp/" + slug + "/v3?" + query_string
    ).json()
    return response


def load_real_page(page: str) -> dict:
    if page == 'HOMEPAGE':
        custom_options = {
            'cardsLimit': 1,
            'includeMarketBlurbs': True,
            'includePrices': True,
            'includeRaceCards': True,
            'includeStaticCards': True,
            'nextRacesMarketsLimit': 3,
            'page': page,
            'priceHistory': 3
        }
        return make_strands_request('content-managed-page', custom_options)
    if page == 'IN-PLAY':
        custom_options = {
            'comingUpTimeRange': 360_000,
            'includeStaticCards': True,
            'includeTabs': True
        }
        return make_strands_request('in-play', custom_options)
    if page == 'FOOTBALL':
        custom_options = {
            'cardsLimit': 1,
            'eventTypeId': 1,
            'includeMarketBlurbs': True,
            'includePrices': True,
            'includeRaceCards': True,
            'includeStaticCards': True,
            'nextRacesMarketsLimit': 3,
            'page': 'SPORT',
            'priceHistory': 3
        }
        return make_strands_request('content-managed-page', custom_options)
    else:
        raise Exception('Tried to load an unknown page: ' + page)


def build_tab(cards, coupons, tab):
    tab_cards = [cards[int(x['id'])] for x in tab['cards']
                 if isinstance(x['id'], int) and int(x['id']) in cards.keys()]

    tab_coupons = {coupon['id']: coupons[coupon['id']] for sublist in
                   [card['coupons'] for card in tab_cards] for coupon in sublist}

    return {'title': tab['title'],
            'id': int(tab['id']),
            'cards': tab_cards,
            'coupons': tab_coupons}


def load_page(page: str, mocked: bool = True) -> PageLayout:
    if mocked:
        json_data = load_mocked_page(page)
    else:
        json_data = load_real_page(page)

    cards = {int(card_id): x for card_id, x in json_data['layout']['cards'].items() if x['type'] == 'COUPON'}
    coupons = {int(coupon_id): x for coupon_id, x in json_data['layout']['coupons'].items()} \
        if 'coupons' in json_data['layout'] else {}

    tabs_with_ids = [build_tab(cards, coupons, json_data['layout']['tabs'][str(tab_id)])
                     for tab_id in json_data['layout']['tabsDisplayOrder']
                     if 'type' not in json_data['layout']['tabs'][str(tab_id)].keys() or
                     json_data['layout']['tabs'][str(tab_id)]['type'] == 'TAB']

    layout = PageLayout(tabs=tabs_with_ids, default_tab=json_data['layout']['defaultTab'],
                        page_info=json_data['layout']['page'], cards=cards)
    return layout
