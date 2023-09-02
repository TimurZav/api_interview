import requests
from typing import List
from requests import Response
from datetime import datetime
from __init__ import DATE_FTM, get_logger, getLogger, os


class Report:

    def __init__(self):
        self.logger: getLogger = get_logger(os.path.basename(__file__).replace(".py", "_") + str(datetime.now().date()))

    def get_data_by_api(self) -> None:
        """
        Getting data from the REST API. If errors occur, we record them in the logs.
        :return:
        """
        try:
            users_response: Response = requests.get("https://json.medrocket.ru/users", timeout=120)
            tasks_response: Response = requests.get("https://json.medrocket.ru/todos", timeout=120)
            users_response.raise_for_status()
            tasks_response.raise_for_status()

            self.logger.info("Data received successfully")
            users: List[dict] = users_response.json()
            tasks: List[dict] = tasks_response.json()
            self.parse_all_data(users, tasks)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"An error occurred during the API request: {str(e)}")
            raise SystemExit(e) from e
        except Exception as e:
            self.logger.error(f"An error occurred: {str(e)}")
            raise SystemExit(e) from e

    def parse_all_data(self, users: List[dict], tasks: List[dict]) -> None:
        """
        Getting all the users data and their tasks and then write them to files.
        :param users: List of users with their personal information.
        :param tasks: The list of tasks of these users.
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
        Getting actual and completed tasks, as well as their number and total number.
        :param tasks: The list of tasks of these users.
        :param user: Current user from list.
        :return: A dictionary with a number and a list of tasks.
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
        Receive personal data on the user with the total number of tasks.
        :param user: Current user from list.
        :param total_count_tasks: Total number of tasks.
        :return: A paragraph with personal data.
        """
        self.logger.info("Will record the user's personal data in the paragraph")
        return f"# Отчёт для {user.get('company', {}).get('name')}.\n" \
               f"{user.get('name')} <{user.get('email')}> {datetime.now():{DATE_FTM}}\n" \
               f"Всего задач: {total_count_tasks}\n\n"

    def parse_tasks(self, tasks: list, name: str, count_tasks: int) -> str:
        """
        Get user tasks (actual or completed) with their number.
        :param tasks: The list of tasks of these users.
        :param name: Actual or Completed tasks.
        :param count_tasks: Number of tasks.
        :return: A paragraph with tasks.
        """
        self.logger.info(f"Will write a list of '{name}' tasks in a paragraph")
        tasks_str: str = f"## {name} задачи ({count_tasks}):\n"
        tasks_str += "\n".join(f"- {task}" if len(task) < 46 else f"- {task[:46]}..." for task in tasks)
        return f"{tasks_str}\n\n"

    def write_to_file(self, filename: str, content: str) -> None:
        """
        Writing data to a file.
        :param filename: Current name of file.
        :param content: Content of current file.
        :return:
        """
        dir_name: str = os.path.dirname(filename)
        os.makedirs(dir_name, exist_ok=True)
        if os.path.isfile(filename):
            self.logger.info(f"The file {os.path.basename(filename)} exists, so rename other files")
            os.rename(
                filename,
                f"{dir_name}/"
                f"old_{os.path.basename(filename).replace('.txt', '')}_"
                f"{datetime.fromtimestamp(os.path.getmtime(filename)).strftime('%Y-%m-%dT%H:%M')}.txt"
            )
        with open(filename, "w") as file:
            file.write(content)
            self.logger.info(f"The data on the file {os.path.basename(filename)} was recorded successfully")


if __name__ == "__main__":
    Report().get_data_by_api()
