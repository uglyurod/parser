"""HeadHunter Researcher

Description   :
    HeadHunter (hh.ru) main research script.

    1. Get data from hh.ru by user request (i.e. 'Machine learning')
    2. Collect all vacancies.
    3. Parse JSON and get useful values: salary, experience, name,
    skills, employer name etc.
    4. Calculate some statistics: average salary, median, std, variance.

"""

import os
from typing import Optional

from src.analyzer import Analyzer
from src.currency_exchange import Exchanger
from src.data_collector import DataCollector
from src.parser import Settings
from src.predictor import Predictor
from src.gui import GUI

CACHE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "cache")
SETTINGS_PATH = "settings.json"


class ResearcherHH:
    """Main class for searching vacancies and analyze them."""

    def __init__(self, config_path: str = SETTINGS_PATH, no_parse: bool = False):
        self.settings = Settings(config_path, no_parse=no_parse)
        self.exchanger = Exchanger(config_path)
        self.collector: Optional[DataCollector] = None
        self.analyzer: Optional[Analyzer] = None
        self.predictor = Predictor()
        self.gui = GUI()

    def update(self, **kwargs):
        self.settings.update_params(**kwargs)
        if not any(self.settings.rates.values()) or self.settings.update:
            print("[INFO]: Trying to get exchange rates from remote server...")
            self.exchanger.update_exchange_rates(self.settings.rates)
            self.exchanger.save_rates(self.settings.rates)

        print(f"[INFO]: Get exchange rates: {self.settings.rates}")
        self.collector = DataCollector(self.settings.rates)
        self.analyzer = Analyzer(self.settings.save_result)

    def __call__(self):
        print("[INFO]: Collect data from JSON. Create list of vacancies...")
        vacancies = self.collector.collect_vacancies(
            query=self.settings.options, refresh=self.settings.refresh, max_workers=self.settings.max_workers
        )
        print("[INFO]: Prepare dataframe...")
        df = self.analyzer.prepare_df(vacancies)
        print("\n[INFO]: Analyze dataframe...")
        self.analyzer.analyze_df(df)
        print("\n[INFO]: Predict None salaries...")
        # total_df = self.predictor.predict(df)
        # self.predictor.plot_results(total_df)
        print("[INFO]: Done! Exit()")


if __name__ == "__main__":
    hh_analyzer = ResearcherHH()
    hh_analyzer.update()
    hh_analyzer()
