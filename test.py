import unittest
import random as rn
from pymongo import results
from Bot import DataBase
from Bot import  Receiving_A_Message_With_A_Question


db = DataBase()
class TestDataBase(unittest.TestCase):

    def setUp(self):

        print("id: " + self.id())
        self.db = DataBase()
        self.randID = rn.randint(1, 352503060)
        self.student = self.db.GetStudent(self.randID)
        if not self.student["QuestionNumber"]:
            self.student_is_rand = True

    def test_access(self):

        print("id: " + self.id())
        self.assertIsInstance(self.student, dict)

    def test_correctWork(self):

        print("id: " + self.id())
        self.assertEqual(self.student['ChatId'], self.randID)

    def test_HasCorrectElements(self):

        print("id: " + self.id())
        self.assertNotEqual(self.student['completed'], None)
        self.assertNotEqual(self.student['goes'], None)

    def test_containCorrectData(self):
        student = self.db.students.find_one({"completed": True})
        self.assertNotEqual(student['completed'], student['goes'])

    def tearDown(self):
        if self.student_is_rand == True:
            self.d = self.db.students.delete_one({'ChatId': self.student['ChatId']})
            self.assertEqual(results.DeleteResult, type(self.d))

    def test_Get_A_Reply_Message(self):

        student = db.students.find_one({'completed': True})
        for i in range(len(student["answers"])):

            question = db.GiveAQuestion(i)
            text = f"Вопрос №{i + 1}\n\n{question['question']}\n"
            for ResponseNumber, answer in enumerate(question["answers"]):
                text += f"{chr(97 + ResponseNumber)}) {answer}"
                if ResponseNumber == question["right"]:
                    text += " - Верный ответ"
                elif ResponseNumber == student["answers"][i]:
                    text += " - Ваш ответ неверный"

            if student["answers"][i] == question["right"]:
                self.assertEqual(text.find(" - Верный ответ"),
                                 text.find(question["answers"][question["right"]]) + len(answer))
            elif student["answers"][i] != question["right"] and ResponseNumber == student["answers"][i]:
                self.assertNotEqual(text.find("Ваш ответ неверный"), -1)

            text = ""

    def test_Receiving_A_Message_With_A_Question(self):

        test_list = ["- неудволетворительно", "- неудволетворительно", " - удволетворительно", " - удволетворительно",
                     " - удволетворительно", "- хорошо", "- хорошо", "- хорошо", "- отлично", "- отлично", "- отлично"]
        for i in range(11):

            result = round(100 * i / db.NumberOfQuestions)

            if (result < 20):
                estimation = "- неудволетворительно"
            elif (result >= 20) and (result < 45):
                estimation = " - удволетворительно"
            elif (result >= 45) and (result < 80):
                estimation = "- хорошо"
            elif (result >= 80):
                estimation = "- отлично"
            self.assertEqual(test_list[i], estimation)

    def test_Receiving_A_Message_With_A_Question_Second(self):

        student = {"QuestionNumber": None}
        self.assertEqual(Receiving_A_Message_With_A_Question(student), None)

        for i in range(0, 10):
            student = {"QuestionNumber": i}

            test_param = Receiving_A_Message_With_A_Question(student)

            question = db.questions.find_one({"id": i})["question"]

            self.assertIn(question, test_param["question"])


if __name__ == '__main__':
    unittest.main()

