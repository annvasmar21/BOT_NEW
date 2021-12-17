import unittest
import random as rn
from pymongo import MongoClient
from pymongo import results


class DataBase:

    def __init__(p):
        cluster = MongoClient(
            "mongodb+srv://annv:polol2461@cluster0.082c6.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        p.db = cluster["quiz"]  # коллекция
        p.students = p.db["test"]
        p.questions = p.db["que"]
        p.NumberOfQuestions = len(list(p.questions.find({})))  # количество вопросов

    def GetStudent(p, userID):
        student = p.students.find_one({"chat_id": userID})
        if student is not None:
            return student
        student = {
            "chat_id": userID,
            "is_passing": False,
            "is_passed": False,
            "question_index": None,
            "answers": []
        }
        p.students.insert_one(student)
        return student

    def setStudent(p, userID, update):
        p.students.update_one({"chat_id": userID}, {"$set": update})

    def get_question(p, index):
        return p.questions.find_one({"id": index})


class TestDataBase(unittest.TestCase):

    def setUp(self):

        print("id: " + self.id())
        self.db = DataBase()
        self.randID = rn.randint(1, 352503060)
        self.student = self.db.GetStudent(self.randID)
        if not self.student["question_index"]:
            self.student_is_rand = True

    def test_access(self):

        print("id: " + self.id())
        self.assertIsInstance(self.student, dict)

    def test_correctWork(self):

        print("id: " + self.id())
        self.assertEqual(self.student['chat_id'], self.randID)

    def test_HasCorrectElements(self):

        print("id: " + self.id())
        self.assertNotEqual(self.student['is_passed'], None)
        self.assertNotEqual(self.student['is_passing'], None)

    def test_contaiCorrectData(self):
        student = self.db.students.find_one({"is_passed": True})
        print(student)
        self.assertNotEqual(student['is_passed'], student['is_passing'])

    def tearDown(self):
        if self.student_is_rand == True:
            self.d = self.db.students.delete_one({'chat_id': self.student['chat_id']})
            self.assertEqual(results.DeleteResult, type(self.d))


if __name__ == '__main__':
    unittest.main()
