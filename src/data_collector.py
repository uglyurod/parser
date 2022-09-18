r"""Vacancy finder
"""

import hashlib
import os
import pickle
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional
from urllib.parse import urlencode

import requests
from tqdm import tqdm

CACHE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "cache")


class DataCollector:
    r"""Researcher parameters

    Parameters
    ----------
    exchange_rates : dict
        Dict of exchange rates: RUR, USD, EUR.

    """
    __API_BASE_URL = "https://api.hh.ru/vacancies/"
    __DICT_KEYS = (
        "Ids",
        "Employer",
        "Name",
        "Salary",
        "From",
        "To",
        "Experience",
        "Schedule",
        "Keys",
        "Description",
    )

    def __init__(self, exchange_rates: Optional[Dict]):
        self._rates = exchange_rates

    @staticmethod
    def clean_tags(html_text: str) -> str:
        """Remove HTML tags from the string

        Parameters
        ----------
        html_text: str
            Input string with tags

        Returns
        -------
        result: string
            Clean text without HTML tags

        """
        pattern = re.compile("<.*?>")
        return re.sub(pattern, "", html_text)

    @staticmethod
    def __convert_gross(is_gross: bool) -> float:
        return 0.87 if is_gross else 1

    def get_vacancy(self, vacancy_id: str):
        # Get data from URL
        url = f"{self.__API_BASE_URL}{vacancy_id}"
        vacancy = requests.api.get(url).json()

        # Extract salary
        salary = vacancy.get("salary")

        # Calculate salary:
        # Get salary into {RUB, USD, EUR} with {Gross} parameter and
        # return a new salary in RUB.
        from_to = {"from": None, "to": None}
        if salary:
            is_gross = vacancy["salary"].get("gross")
            for k, v in from_to.items():
                if vacancy["salary"][k] is not None:
                    _value = self.__convert_gross(is_gross)
                    from_to[k] = int(_value * salary[k] / self._rates[salary["currency"]])

        # Create pages tuple
        return (
            vacancy_id,
            vacancy["employer"]["name"],
            vacancy["name"],
            salary is not None,
            from_to["from"],
            from_to["to"],
            vacancy["experience"]["name"],
            vacancy["schedule"]["name"],
            [el["name"] for el in vacancy["key_skills"]],
            self.clean_tags(vacancy["description"]),
        )

    def collect_vacancies(self, query: Optional[Dict], refresh: bool = False, max_workers: int = 1) -> Dict:
        """Parse vacancy JSON: get vacancy name, salary, experience etc.

        Parameters
        ----------
        query : dict
            Search query params for GET requests.
        refresh :  bool
            Refresh cached data
        max_workers :  int
            Number of workers for threading.

        Returns
        -------
        dict
            Dict of useful arguments from vacancies

        """

        # Get cached data if exists...
        cache_name: str = query.get("text")
        cache_hash = hashlib.md5(cache_name.encode()).hexdigest()
        cache_file = os.path.join(CACHE_DIR, cache_hash)
        try:
            if not refresh:
                print(f"[INFO]: Get results from cache! Enable refresh option to update results.")
                return pickle.load(open(cache_file, "rb"))
        except (FileNotFoundError, pickle.UnpicklingError):
            pass

        # Check number of pages...
        target_url = self.__API_BASE_URL + "?" + urlencode(query)
        num_pages = requests.get(target_url).json()["pages"]

        # Collect vacancy IDs...
        ids = []
        for idx in range(num_pages + 1):
            response = requests.get(target_url, {"page": idx})
            data = response.json()
            if "items" not in data:
                break
            ids.extend(x["id"] for x in data["items"])

        # Collect vacancies...
        jobs_list = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for vacancy in tqdm(
                executor.map(self.get_vacancy, ids),
                desc="Get data via HH API",
                ncols=100,
                total=len(ids),
            ):
                jobs_list.append(vacancy)

        unzipped_list = list(zip(*jobs_list))

        result = {}
        for idx, key in enumerate(self.__DICT_KEYS):
            result[key] = unzipped_list[idx]

        pickle.dump(result, open(cache_file, "wb"))
        return result


if __name__ == "__main__":
    dc = DataCollector(exchange_rates={"USD": 0.01264, "EUR": 0.01083, "RUR": 1.00000})

    vacancies = dc.collect_vacancies(
        query={"text": "FPGA", "area": 1, "per_page": 50},
        # refresh=True
    )
    print(vacancies["Employer"])
