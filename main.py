import requests
from __init__ import *
from typing import List
from pathlib import Path
from requests import Response
from datetime import datetime


class Report:

    def __init__(self):
        self.logger: getLogger = get_logger(os.path.basename(__file__).replace(".py", "_") + str(datetime.now().date()))

    def get_data_by_api(self) -> None:
        """

        :return:
        """
        response_users: Response = requests.get("https://json.medrocket.ru/users")
        response_tasks: Response = requests.get("https://json.medrocket.ru/todos")
        if response_users.status_code == 200 and response_tasks.status_code == 200:
            self.logger.info("Data received successfully")
            data_users: List[dict] = response_users.json()
            data_tasks: List[dict] = response_tasks.json()
            self.parse_all_data(data_users, data_tasks)
        else:
            self.logger.error(f"No data was received. Response users code is {response_users.status_code} "
                              f"and Response tasks code is {response_tasks.status_code}")

    def parse_all_data(self, data_users: List[dict], data_tasks: List[dict]) -> None:
        """

        :param data_users:
        :param data_tasks:
        :return:
        """
        for user in data_users:
            dict_tasks: dict = self.get_data_and_count_tasks(data_tasks, user)
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

    def get_data_and_count_tasks(self, data_tasks: List[dict], user: dict) -> dict:
        """

        :param data_tasks:
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
        for task in data_tasks:
            if task.get("userId") == user.get("id"):
                if task.get("completed"):
                    dict_tasks["completed_count_tasks"] += 1
                    dict_tasks["completed_tasks"].append(task.get("title"))
                else:
                    dict_tasks["actual_count_tasks"] += 1
                    dict_tasks["actual_tasks"].append(task.get("title"))
                dict_tasks["total_count_tasks"] += 1
        self.logger.info("Tasks were successfully counted and received")
        return dict_tasks

    def parse_personal_data(self, user: dict, total_count_tasks: int) -> str:
        """

        :param user:
        :param total_count_tasks:
        :return:
        """
        self.logger.info("Will record the user's personal data in the paragraph")
        return f"# Отчёт для {user.get('company', {}).get('name', None)}.\n" \
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
        for task in tasks:
            tasks_str += f"- {task}\n"
        return f"{tasks_str}\n"

    def write_to_file(self, filename: str, content: str) -> None:
        """

        :param filename:
        :param content:
        :return:
        """
        fle: Path = Path(filename)
        if not os.path.exists(os.path.dirname(fle)):
            os.makedirs(os.path.dirname(fle))
        with open(filename, 'w') as file:
            file.write(content)
            self.logger.info(f"The data on the file {os.path.basename(filename)} was recorded successfully")


if __name__ == '__main__':
    Report().get_data_by_api()
