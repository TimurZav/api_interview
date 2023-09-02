import unittest
import requests
from requests import Response
from datetime import datetime
from typing import List, Optional
from __init__ import DATE_FTM, get_logger, getLogger, os


class Report(unittest.TestCase):

    def setUp(self) -> None:
        self.logger: getLogger = get_logger(os.path.basename(__file__).replace(".py", "_") + str(datetime.now().date()))
        self.users: List[dict] = []
        self.tasks: List[dict] = []
        self.user: dict = {}
        self.dict_tasks: dict = {}
        self.filename: Optional[str] = None
        self.content: Optional[str] = None

    def test_get_data_by_api(self) -> None:
        """
        Getting data from the REST API. If errors occur, we record them in the logs.
        :return:
        """
        try:
            users_response: Response = requests.get("https://json.medrocket.ru/users", timeout=120)
            tasks_response: Response = requests.get("https://json.medrocket.ru/todos", timeout=120)
            self.assertEqual(users_response.status_code, 200)
            self.assertEqual(tasks_response.status_code, 200)

            self.logger.info("Data received successfully")
            self.users = users_response.json()
            self.tasks = tasks_response.json()
            self.assertTrue(self.users)
            self.assertTrue(self.tasks)
            self.test_parse_all_data()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"An error occurred during the API request: {str(e)}")
            raise SystemExit(e) from e
        except Exception as e:
            self.logger.error(f"An error occurred: {str(e)}")
            raise SystemExit(e) from e

    def test_parse_all_data(self) -> None:
        """
        Getting all the users data and their tasks and then write them to files.
        :return:
        """
        for user in self.users:
            self.user = user
            self.dict_tasks: dict = self.test_get_data_and_count_tasks()
            personal_data: str = self.test_parse_personal_data()
            actual_tasks: str = self.test_parse_actual_tasks()
            completed_tasks: str = self.test_parse_completed_tasks()
            self.filename = f"test_tasks/{user.get('username')}.txt"
            self.content = f"{personal_data}{actual_tasks}{completed_tasks}"
            self.test_write_to_file()

    def test_get_data_and_count_tasks(self) -> dict:
        """
        Getting actual and completed tasks, as well as their number and total number.
        :return: A dictionary with a number and a list of tasks.
        """
        dict_tasks: dict = {
            "total_count_tasks": 0,
            "actual_count_tasks": 0,
            "completed_count_tasks": 0,
            "actual_tasks": [],
            "completed_tasks": []
        }
        for task in self.tasks:
            if task.get("userId") == self.user.get("id"):
                if task.get("completed"):
                    dict_tasks["completed_count_tasks"] += 1
                    dict_tasks["completed_tasks"].append(task.get("title"))
                else:
                    dict_tasks["actual_count_tasks"] += 1
                    dict_tasks["actual_tasks"].append(task.get("title"))
                dict_tasks["total_count_tasks"] += 1
        self.logger.info(f"Tasks for user '{self.user.get('username')}' were successfully counted and received")
        return dict_tasks

    def test_parse_personal_data(self) -> str:
        """
        Receive personal data on the user with the total number of tasks.
        :return: A paragraph with personal data.
        """
        self.logger.info("Will record the user's personal data in the paragraph")
        return f"# Отчёт для {self.user.get('company', {}).get('name')}.\n" \
               f"{self.user.get('name')} <{self.user.get('email')}> {datetime.now():{DATE_FTM}}\n" \
               f"Всего задач: {self.dict_tasks.get('total_count_tasks')}\n\n"

    def test_parse_actual_tasks(self) -> str:
        """
        Get user tasks (actual or completed) with their number.
        :return: A paragraph with tasks.
        """
        self.logger.info("Will write a list of 'Актуальные' tasks in a paragraph")
        tasks_str: str = f"## Актуальные задачи ({self.dict_tasks.get('actual_count_tasks')}):\n"
        tasks_str += "\n".join(f"- {task}" if len(task) < 46 else f"- {task[:46]}..."
                               for task in self.dict_tasks.get("actual_tasks", {}))
        return f"{tasks_str}\n\n"

    def test_parse_completed_tasks(self) -> str:
        """
        Get user tasks (actual or completed) with their number.
        :return: A paragraph with tasks.
        """
        self.logger.info("Will write a list of 'Завершенные' tasks in a paragraph")
        tasks_str: str = f"## Завершенные задачи ({self.dict_tasks.get('completed_count_tasks')}):\n"
        tasks_str += "\n".join(f"- {task}" if len(task) < 46 else f"- {task[:46]}..."
                               for task in self.dict_tasks.get("completed_tasks", {}))
        return f"{tasks_str}\n\n"

    def test_write_to_file(self) -> None:
        """
        Writing data to a file.
        :return:
        """
        if self.filename:
            dir_name: str = os.path.dirname(self.filename)
            os.makedirs(dir_name, exist_ok=True)
            if os.path.isfile(self.filename):
                self.logger.info(f"The file {os.path.basename(self.filename)} exists, so rename other files")
                self.assertTrue(os.path.exists(self.filename), "The file does not exist in the specified directory")
                os.rename(
                    self.filename,
                    f"{dir_name}/"
                    f"old_{os.path.basename(self.filename).replace('.txt', '')}_"
                    f"{datetime.fromtimestamp(os.path.getmtime(self.filename)).strftime('%Y-%m-%dT%H:%M')}.txt"
                )
            self.assertFalse(os.path.exists(self.filename), "The file exists in the specified directory")
            with open(self.filename, "w") as file:
                file.write(self.content)
                self.logger.info(f"The data on the file {os.path.basename(self.filename)} was recorded successfully")


if __name__ == "__main__":
    unittest.main()
