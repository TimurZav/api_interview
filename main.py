import re
import requests
from __init__ import *
from typing import List
from requests import Response
from datetime import datetime


class Report:

    def __init__(self):
        self.logger: getLogger = get_logger(os.path.basename(__file__).replace(".py", "_") + str(datetime.now().date()))

    def get_data_by_api(self) -> None:
        """

        :return:
        """
        try:
            response_users: Response = requests.get("https://json.medrocket.ru/users", timeout=120)
            response_tasks: Response = requests.get("https://json.medrocket.ru/todos", timeout=120)
            response_users.raise_for_status()
            response_tasks.raise_for_status()

            self.logger.info("Data received successfully")
            users: List[dict] = response_users.json()
            tasks: List[dict] = response_tasks.json()
            self.parse_all_data(users, tasks)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"An error occurred during the API request: {str(e)}")
        except Exception as e:
            self.logger.error(f"An error occurred: {str(e)}")

    def parse_all_data(self, users: List[dict], tasks: List[dict]) -> None:
        """

        :param users:
        :param tasks:
        :return:
        """
        for user in users:
            dict_tasks: dict = self._get_data_and_count_tasks(tasks, user)
            personal_data: str = self.parse_personal_data(user, dict_tasks["total_count_tasks"])
            actual_tasks: str = self.parse_tasks(
                dict_tasks["actual_tasks"],
                "Актуальные",
                dict_tasks["actual_count_tasks"]
            )
            completed_tasks: str = self.parse_tasks(
                dict_tasks["completed_tasks"],
                "Завершённые",
                dict_tasks["completed_count_tasks"]
            )
            self.write_to_file(f"tasks/{user.get('username')}.txt", f"{personal_data}{actual_tasks}{completed_tasks}")

    def _get_data_and_count_tasks(self, tasks: List[dict], user: dict) -> dict:
        """

        :param tasks:
        :param user:
        :return:
        """
        dict_tasks: dict = {
            "total_count_tasks": 0,
            "actual_count_tasks": 0,
            "completed_count_tasks": 0,
            "actual_tasks": [],
            "completed_tasks": []
        }
        for task in tasks:
            if task.get("userId") == user.get("id"):
                if task.get("completed"):
                    dict_tasks["completed_count_tasks"] += 1
                    dict_tasks["completed_tasks"].append(task.get("title"))
                else:
                    dict_tasks["actual_count_tasks"] += 1
                    dict_tasks["actual_tasks"].append(task.get("title"))
                dict_tasks["total_count_tasks"] += 1
        self.logger.info(f"Tasks for user '{user.get('username')}' were successfully counted and received")
        return dict_tasks

    def parse_personal_data(self, user: dict, total_count_tasks: int) -> str:
        """

        :param user:
        :param total_count_tasks:
        :return:
        """
        self.logger.info("Will record the user's personal data in the paragraph")
        return f"# Отчёт для {user.get('company', {}).get('name')}.\n" \
               f"{user.get('name')} <{user.get('email')}> {datetime.now():{DATE_FTM}}\n" \
               f"Всего задач: {total_count_tasks}\n\n"

    def parse_tasks(self, tasks: list, name: str, actual_count_tasks: int) -> str:
        """

        :param tasks:
        :param name:
        :param actual_count_tasks:
        :return:
        """
        self.logger.info(f"Will write a list of '{name}' tasks in a paragraph")
        tasks_str: str = f"## {name} задачи ({actual_count_tasks}):\n"
        tasks_str += "\n".join(f"- {task}" if len(task) < 46 else f"- {task[:46]}..." for task in tasks)
        return f"{tasks_str}\n\n"

    def _get_date_from_file_content(self, content: str) -> str:
        """

        :param content:
        :return:
        """
        self.logger.info("Get date in file content")
        if match := re.search(r"\d{2}[.]\d{2}[.]\d{4} \d{2}:\d{2}", content):
            return match.group()
        else:
            return datetime.now().strftime(DATE_FTM)

    def rename_old_files(self, filename: str, dir_name: str):
        """

        :param filename:
        :param dir_name:
        :return:
        """
        self.logger.info(f"The file {os.path.basename(filename)} exists, so rename other files")
        with open(filename, "r") as file:
            date: str = self._get_date_from_file_content(file.read())
            os.rename(
                filename,
                f"{dir_name}/"
                f"old_{os.path.basename(filename).replace('.txt', '')}_"
                f"{datetime.strptime(date, DATE_FTM).strftime('%Y-%m-%dT%H:%M')}.txt"
            )

    def write_to_file(self, filename: str, content: str) -> None:
        """

        :param filename:
        :param content:
        :return:
        """
        dir_name: str = os.path.dirname(filename)
        os.makedirs(dir_name, exist_ok=True)
        if os.path.isfile(filename):
            self.rename_old_files(filename, dir_name)
        with open(filename, "w") as file:
            file.write(content)
            self.logger.info(f"The data on the file {os.path.basename(filename)} was recorded successfully")


if __name__ == "__main__":
    Report().get_data_by_api()
