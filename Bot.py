import telebot
from pymongo import MongoClient
bot = telebot.TeleBot("5061166024:AAHIko-D20d0Mu0inh6aj6QzxuidhagyLNM")

class DataBase:
	def __init__(p):
		""" Функция Init это метод класса, нужен для того чтобы при создании объекта db выражением
		db = DataBase() задавались свойства и начальные знания объекта.
		То есть функция для управления базой данных. Подключается к коллекции, считает количество вопросов в викторине.
		Внутри класса мы обращаемся к объекту через p.

		:param p: принимает объект, как и все функции данного класса.
		"""
		cluster = MongoClient("mongodb+srv://annv:polol2461@cluster0.082c6.mongodb.net/test")
		p.db = cluster["quiz"] #коллекция
		p.students = p.db["test"]
		p.questions = p.db["que"]
		p.NumberOfQuestions = len(list(p.questions.find({}))) #количество вопросов
	def GetStudent(p, userID):
		"""Функция, которая индифицирует пользователя по chat_id.
		Если пользователя нет в базе данных, то создается новый.

		:param p: принимает объект базы данных
		:param userID: принимает chat_id пользователя
		:return: данные о студенте
		"""
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
		p.students .insert_one(student)
		return student
	def setStudent(p, userID, update):
		"""Функция меняет параметры пользователя по chat_id.

		:param p:принимает объект базы данных
		:param userID: принимает chat_id пользователя
		:param update: принимает новые данные на обновление
		"""
		p.students .update_one({"chat_id": userID}, {"$set": update})
	def GiveAQuestion(p, index):
		"""
		:param p: принимает объект базы данных
		:param index: индекс вопроса (его номер)
		:return: возвращет вопрос по индексу самого вопроса
		"""
		return p.questions.find_one({"id": index})
db = DataBase()
@bot.message_handler(commands=["start"])
def start(message):
	"""
	Функция вызывается по команде 'start'. Начинается работа бота.
	В этой функции проверяется проходил ли раньше пользователь бота викторину.
	Происходит обработка сообщения для отправки пользователю и неполсредственнно его отправка.

	:param message: новое входящее сообщение любого рода
	"""
	student = db.GetStudent(message.chat.id)
	if student["is_passed"]:
		bot.send_message(message.from_user.id, "Вторая попытка невозможна.")
		return
	if student["is_passing"]:
		return
	db.setStudent(message.chat.id, {"question_index": 0, "is_passing": True})
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
	if student["is_passed"] or not student["is_passing"]:
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
	if student["is_passed"] or not student["is_passing"]:
		return
	student["question_index"] += 1
	db.setStudent(query.message.chat.id, {"question_index": student["question_index"]})
	Unloading = Receiving_A_Message_With_A_Question(student)
	if Unloading is not None:
		bot.edit_message_text(Unloading["question"], query.message.chat.id, query.message.id,
						 reply_markup=Unloading["keyboard"])

def Get_A_Reply_Message(student):
	"""
	Функция отвечает пользователю. Проверяет его правильные и ложные ответы и соответственно показывает это.
	:param student:
	:return: Ответ пользователю
	"""
	question = db.GiveAQuestion(student["question_index"])
	text = f"Вопрос №{student['question_index'] + 1}\n\n{question['question']}\n"
	for answer_index, answer in enumerate(question["answers"]):
		text += f"{chr(answer_index + 97)}) {answer}"
		if answer_index == question["right"]:
			text += " 👍- Верный ответ"
		elif answer_index == student["answers"][-1]:
			text += "- Ваш ответ неверный"
		text += "\n"
	keyboard = telebot.types.InlineKeyboardMarkup()
	keyboard.row(telebot.types.InlineKeyboardButton("Перейти на следующий шаг", callback_data="?next"))
	return {
		"question": text,
		"keyboard": keyboard
	}
def Receiving_A_Message_With_A_Question(student):
	"""Функция возвращает текст и клавиатуру  вопросов для тех, кто не прошел викторину.
	Пробегаем по всем ответам и добавляем ответы в кнопки клавиатуры. Возвращается словарь с текстом вопроса и клавиатурой.

	:param student:- данные о пользователе из базы данных
	"""
	if student["question_index"] == db.NumberOfQuestions:
		counter = 0
		for question_index, question in enumerate(db.questions.find({})):
			if question["right"] == student["answers"][question_index]:
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
		db.setStudent(student["chat_id"], {"is_passed": True, "is_passing": False})
		return {
			"question": text, "keyboard": None
		}
	question = db.GiveAQuestion(student["question_index"])
	if question is None:
		return
	keyboard = telebot.types.InlineKeyboardMarkup()
	for answer_index, answer in enumerate(question["answers"]):
		keyboard.row(telebot.types.InlineKeyboardButton(f"{chr(answer_index + 97)}) {answer}",
														callback_data=f"?ans&{answer_index}"))
	text = f"Вопрос №{student['question_index'] + 1}\n\n{question['question']}"
	return {
		"question": text,
		"keyboard": keyboard
	}
bot.polling()
