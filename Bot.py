import telebot
from pymongo import MongoClient
from pathlib import Path

bot = telebot.TeleBot(token=Path('token.txt').read_text().strip())
class DataBase:
	"""
		class DataBase экземпляр этого класса получается из DbContext объекта и может использоваться
		для управления фактической базой данных резервной копии DbContext или соединения.
		В частности, поддерживается создание, удаление и проверка наличия базы данных.
		MongoDB — это ориентированная на документы база данных NoSQL с открытым исходным кодом, которая использует для хранения структуру JSON.
		Модель данных MongoDB позволяет представлять иерархические отношения, проще хранить массивы и другие более сложные структуры.

		Attributes
		----------
		self: принимает объект класса
		db: представляет текущую базу данных,  в которой находятся коллекции
		students: получает данные о пользователе из коллекции базы данных
		questions: получает вопросы из коллекции базы данных
		NumberOfQuestions: считает количество вопросов в коллекции, с помощью метода find (указывается словарь, чтобы получить все элементы базы данных),
		который извлекает документы, а потом с помощью преобразования в список и вычисления длины списка, получается необходимый результат


		Commands
		-------
		insertOne(): добавляет один документ
		insertMany(): добавляет несколько документов
		insert(): может добавлять как один, так и несколько документов
		findOne(): извлекается одиночный документ
		find(): все документы извлекаются
	"""
	def __init__(self):
		""" Функция Init это метод класса, нужен для того чтобы при создании объекта db выражением
		db = DataBase() задавались свойства и начальные знания объекта.
		То есть функция для управления базой данных. Подключается к коллекции, считает количество вопросов в викторине.
		Внутри класса мы обращаемся к объекту через self.

		:param  self: принимает объект, как и все функции класса.
		"""
		cluster = MongoClient("mongodb+srv://annv:polol2461@cluster0.082c6.mongodb.net/test")
		self.db = cluster["quiz"]
		self.students = self.db["test"]
		self.questions = self.db["que"]
		self.NumberOfQuestions = len(list( self.questions.find({})))
	def GetStudent( self, userID):
		"""Функция, которая индифицирует пользователя по ChatiId.
		Если пользователя нет в базе данных, то создается новый.

		:param self: принимает объект базы данных
		:param userID: принимает ChatiId пользователя
		:return: данные о студенте
		"""
		student = self.students.find_one({"ChatId": userID})
		if student is not None:
			return student
		student = {
			"ChatId": userID,
			"completed": False,
			"goes": False,
			"QuestionNumber": None,
			"answers": []
		}
		self.students .insert_one(student)
		return student
	def setStudent( self, userID, update):
		"""Функция меняет параметры пользователя по ChatiId.

		:param  self:принимает объект базы данных
		:param userID: принимает ChatiId пользователя
		:param update: принимает новые данные на обновление
		"""
		self.students .update_one({"ChatId": userID}, {"$set": update})
	def GiveAQuestion(self, index):
		"""
		:param self: принимает объект базы данных
		:param index: индекс вопроса (его номер)
		:return: возвращет вопрос по индексу самого вопроса
		"""
		return self.questions.find_one({"id": index})
db = DataBase()
def Receiving_A_Message_With_A_Question(student):
	"""Функция возвращает текст и клавиатуру  вопросов для тех, кто не прошел викторину.
	Пробегаем по всем ответам и добавляем ответы в кнопки клавиатуры. Возвращается словарь с текстом вопроса и клавиатурой.

	:param student:- данные о пользователе из базы данных
	"""
	if student["QuestionNumber"] == db.NumberOfQuestions:
		counter = 0
		for QuestionNumber, question in enumerate(db.questions.find({})):
			if  student["answers"][QuestionNumber] == question["right"]:
				counter += 1
		res=100 * counter
		result = round(res / db.NumberOfQuestions)
		if (result < 20):
			estimation = "- неудволетворительно"
		elif (result >= 20) and (result < 45):
			estimation = " - удволетворительно"
		elif (result >= 45) and (result < 80):
			estimation = "- хорошо"
		elif (result >= 80):
			estimation = "- отлично"
		text = f"Ваша оценка {estimation}. Процент выполненой верно работы {result}%."

		db.setStudent(student["ChatId"], {"goes": True, "completed": False})
		return {
			"question": text, "keyboard": None }
	question = db.GiveAQuestion(student["QuestionNumber"])
	if question is None:
		return

	keyboard = telebot.types.InlineKeyboardMarkup()
	for ResponseNumber, answer in enumerate(question["answers"]):
		keyboard.row(telebot.types.InlineKeyboardButton(f"{chr(97 + ResponseNumber )}) {answer}",

														callback_data=f"?ans&{ResponseNumber}"))
	text = f"Вопрос №{student['QuestionNumber'] + 1}\n\n{question['question']}"
	return {
		"question": text,
		"keyboard": keyboard
	}
def Get_A_Reply_Message(student):
	"""
	Функция отвечает пользователю. Проверяет его правильные и ложные ответы и соответственно показывает это.
	:param student:
	:return: Ответ пользователю
	"""
	question = db.GiveAQuestion(student["QuestionNumber"])
	text = f"Вопрос №{student['QuestionNumber'] + 1}\n\n{question['question']}\n"
	for ResponseNumber, answer in enumerate(question["answers"]):
		text += f"{chr( 97 + ResponseNumber)}) {answer}"
		if ResponseNumber== question["right"]:
			text += " - Верный ответ"
		elif ResponseNumber == student["answers"][-1]:
			text += " - Ваш ответ неверный"
		text += "\n"
	keyboard = telebot.types.InlineKeyboardMarkup()
	keyboard.row(telebot.types.InlineKeyboardButton("Перейти на следующий шаг", callback_data="?next"))
	return {
		"question": text,
		"keyboard": keyboard
	}
@bot.message_handler(commands=["start"])
def start(message):
	"""
	Функция вызывается по команде 'start'. Начинается работа бота.
	В этой функции проверяется проходил ли раньше пользователь бота викторину.
	Происходит обработка сообщения для отправки пользователю и неполсредственнно его отправка.

	:param message: новое входящее сообщение любого рода
	"""
	student = db.GetStudent(message.chat.id)
	if student["completed"]:
		return
	if student["goes"]:
		bot.send_message(message.from_user.id, "Вторая попытка невозможна.")
		return

	db.setStudent(message.chat.id, {"QuestionNumber": 0, "completed": True})
	student = db.GetStudent(message.chat.id)
	Unloading = Receiving_A_Message_With_A_Question(student)
	if Unloading is not None:
		bot.send_message(message.from_user.id, Unloading["question"], reply_markup=Unloading["keyboard"])
@bot.callback_query_handler(func=lambda query: query.data.startswith("?ans"))
def answered(query):
	""" Функция, которая вызывается пр нажатие пользователя на клавиатуру. Происходит
	добавления ответов пользователя в общий список ответов.

	:param query: объект запроса  ответа
	"""
	student= db.GetStudent(query.message.chat.id)
	if not student["completed"] or student["goes"] :
		return
	student["answers"].append(int(query.data.split("&")[1]))
	db.setStudent(query.message.chat.id, {"answers": student["answers"]})

	Unloading = Get_A_Reply_Message(student)
	if Unloading is not None:
		bot.edit_message_text(Unloading["question"], query.message.chat.id, query.message.id,
						 reply_markup=Unloading["keyboard"])
@bot.callback_query_handler(func=lambda query: query.data == "?next")
def next(query):
	"""
	Функция переходит к следующему вопросу при нажатии на соответствующую кнопку.
	:param query:

	"""
	student = db.GetStudent(query.message.chat.id)
	if not student["completed"] or student["goes"] :
		return
	student["QuestionNumber"] += 1
	db.setStudent(query.message.chat.id, {"QuestionNumber": student["QuestionNumber"]})
	if (Receiving_A_Message_With_A_Question(student)) is not None:
		bot.edit_message_text((Receiving_A_Message_With_A_Question(student))["question"], query.message.chat.id, query.message.id,
						 reply_markup=(Receiving_A_Message_With_A_Question(student))["keyboard"])



bot.polling()

