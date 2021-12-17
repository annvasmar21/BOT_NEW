import unittest
import random as rn
from pymongo import MongoClient
from pymongo import results


class DataBase:

    def __init__(p):
        cluster = MongoClient(
            "mongodb+srv://annv:polol2461@cluster0.082c6.mongodb.net/test")
        p.db = cluster["quiz"]  # коллекция
        p.students = p.db["test"]
        p.questions = p.db["que"]
        p.NumberOfQuestions = len(list(p.questions.find({})))  # количество вопросов

    def GetStudent(p, userID):
        student = p.students.find_one({"ChatId": userID})
        if student is not None:
            return student
        student = {
            "ChatId": userID,
            "goes": False,
            "completed": False,
            "QuestionNumber": None,
            "answers": []
        }
        p.students.insert_one(student)
        return student

    def setStudent(p, userID, update):
        p.students.update_one({"ChatId": userID}, {"$set": update})

    def get_question(p, index):
        return p.questions.find_one({"id": index})


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

    def test_contaiCorrectData(self):
        student = self.db.students.find_one({"completed": True})
        print(student)
        self.assertNotEqual(student['completed'], student['goes'])

    def tearDown(self):
        if self.student_is_rand == True:
            self.d = self.db.students.delete_one({'ChatId': self.student['ChatId']})
            self.assertEqual(results.DeleteResult, type(self.d))


if __name__ == '__main__':
    unittest.main()
