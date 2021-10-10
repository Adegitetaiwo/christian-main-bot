import os
import telebot
from telebot import types
import time
import requests
from tinydb import TinyDB, Query
import random
import logging

import database

db = TinyDB('db.json')

# logger = telebot.logger
# telebot.logger.setLevel(logging.DEBUG)  # Outputs debug messages to console.

image = 'https://res.cloudinary.com/afmdjango/image/upload/v1609893859/gurdjvtxmdnupiyf4rfm.webp'
# document = 'https://res.cloudinary.com/afmdjango/image/upload/v1587142438/nhajgc6z5o3l5tavy0la.pdf'

API_KEY = os.getenv('API_KEY')

bot = telebot.TeleBot('1957271668:AAHfqUHXUN4qH8sGrRNc0jcT0MrznZ_UkLU')


# command to respond to a greeting using the command word /greet
@bot.message_handler(commands=['greet'])
def greet(message):
    bot.reply_to(message, 'Hi how is it going?')


# command to respond to a greeting using the command word /hello
@bot.message_handler(commands=['hello'])
def hello(message):
    bot.send_message(message.chat.id, 'Hi how is it going 👋?')


# command to send file using the command word /file
@bot.message_handler(commands=['file'])
def file(message):
    bot.send_document(message.chat.id, image, caption="Thanks, that's the file you requested for")


# Handler filters all categories that a user could send in a chat
@bot.message_handler(func=lambda message: True, content_types=['audio', 'video',
                                                               'document', 'text', 'location',
                                                               'contact', 'sticker'])
def message_path(message):
    global_result = []

    if message.text is not None and message.text.lower() == '/start' or message.text.lower() in ['hello', 'hi',
                                                                                                 'hey', 'good morning',
                                                                                                 'good afternoon',
                                                                                                 'good evening', '👋']:
        # Introduction message when one start with a greeting
        welcome_msg_list = [f"Hello *{message.from_user.first_name}* 👋, Welcome!\
                        \nLet's get started, what can I help you with today?\
                        \n[1]. Book request\
                        \n[2]. Book Feedback\
                        \n[3]. Contact us",

                            f"Holla *{message.from_user.first_name}* 👋, It nice to have you here!\
                        \nWhat can I help you with today?\
                        \n[1]. Book request\
                        \n[2]. Book Feedback\
                        \n[3]. Contact us",

                            f"You're Welcome *{message.from_user.first_name}* ❤,\
                        \nWhat brings you to me 😉, what can I help you with today?\
                        \n[1]. Book request\
                        \n[2]. Book Feedback\
                        \n[3]. Contact us"
                            ]
        intro_message = random.choice(welcome_msg_list)

        # set up markup for keyboard
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        book_request_btn = types.KeyboardButton('Book request')
        book_feedback_btn = types.KeyboardButton('Book Feedback')
        contact_btn = types.KeyboardButton('Contact')
        markup.add(book_request_btn, book_feedback_btn, contact_btn)

        # send message, pop up the custom keyboard (Book request and Book Feedback)
        msg = bot.send_message(message.chat.id, intro_message, parse_mode="Markdown", reply_markup=markup)
        # bot.register_next_step_handler(msg, bot_ability_option)
    #

    # def bot_ability_option(message):
    #     pass

    if "book request" in message.text.lower() or message.text.lower() == '1':
        # set up markup for keyboard
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        book_request_btn = types.KeyboardButton('search by Book title')
        book_feedback_btn = types.KeyboardButton('search by Book author')
        markup.add(book_request_btn, book_feedback_btn)

        # send message, pop up the custom keyboard (search by Book title OR search by Book author)
        reply_list = ["Alright, that is why i'm here! Would you like to search by Book title "
                      "or Authors name?",
                      "Perfect, which method would you like to search by, 'Book title' OR 'Author\'s name'?",
                      "Brilliant!, You can choose to search by 'Book title' OR Book 'Author's name', which one are you "
                      "going for?"]
        bot_response = random.choice(reply_list)
        msg = bot.send_message(message.chat.id, bot_response, reply_markup=markup)
        bot.register_next_step_handler(msg, search_by_book_attrib)


def search_by_book_attrib(message):
    try:
        if message.text is not None and 'book title' in message.text.lower():
            markup = types.ForceReply(selective=False, input_field_placeholder="Book title. e.g God's general")

            reply_list = ["Please what's the *Title of the book of the book you're trying "
                          "to get? 🙂", "Alright, kindly enter the title of the Book! 🙂",
                          "Brilliant!, What's is the Title of the book you're searching for?",
                          "Ok, i can help you with that, but i'll need to know the *Book's title*. 🙂"]

            bot_response = random.choice(reply_list)
            msg = bot.send_message(message.chat.id, bot_response,
                                   parse_mode="Markdown", reply_markup=markup)
            bot.register_next_step_handler(msg, user_input_book_title)

        elif message.text is not None and "book author" in message.text.lower():
            markup = types.ForceReply(selective=False, input_field_placeholder="Author's name. e.g Roberts Liardon")

            reply_list = ["Please what's the name of the *Author* of the book you're trying "
                          "to get? 🙂", "Alright, kindly enter the name of the Author! 🙂",
                          "Brilliant!, What's is the Author's name of the book you're searching for?",
                          "Ok, i can help you with that, but i'll like to know the *Authors name*. 🙂"]
            bot_response = random.choice(reply_list)
            msg = bot.send_message(message.chat.id, bot_response,
                                   parse_mode="Markdown", reply_markup=markup)
            bot.register_next_step_handler(msg, user_input_book_author)
    except Exception as exc:
        pass


def user_input_book_title(message):
    try:
        if message.text is not None or "title:" in message.text.lower():
            bot.send_message(message.chat.id, "Searching the dataBase for Matches...")
            print(message.text.lower())

            book_title = message.text.lower()

            # book_title_ = message.text.lower().split()
            # book_title_.pop(0)
            # book_title__ = book_title_
            # book_title = ""
            #
            # for word in book_title__:
            #     book_title = book_title + word
            #     book_title = book_title + " "
            #
            # book_title = book_title.strip()

            response = requests.get(f"https://christianbooks-bot-api.herokuapp.com/api/book/?title={book_title}")

            result = []
            data = response.json()['queryset']
            if not data:
                bot.send_message(message.chat.id,
                                 f"I'm sorry, I could'nt find any book in my database that marches your "
                                 f"search '{book_title.capitalize()}'!"
                                 f"\nPlease check your input and try again or you search by Author instead.")
            else:
                for index, item in enumerate(data):
                    result_dict = {'user_id': f"{message.from_user.id}", 'rank': index + 1,
                                   'id': item['id'], 'title': item['title'], 'author': item['author'],
                                   'file': item['file']}
                    result.append(result_dict)

                message_text = ""
                # global_result = result

                print("line 155: ", result)
                for item in result:
                    line = f"\n{item['rank']}.   {item['title']} by {item['author']}"
                    message_text = message_text + line

                if len(result) == 1:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                                                       input_field_placeholder="Trying Placeholder")
                    db.insert(
                        {'user_id': f"{message.from_user.id}", 'file_id': result[0]['id'], 'file': result[0]['file'],
                         'file_title': f"{result[0]['title']}", 'file_author': f"{result[0]['author']}",
                         'status': 'pending'})

                    _yes = types.KeyboardButton('Yes, exactly 😊')
                    _no = types.KeyboardButton('No, not this 😌')

                    markup.add(_yes, _no)
                    msg = bot.send_message(message.chat.id, "*Do you mean this?* \n"
                                                            f"{message_text}",
                                           parse_mode="Markdown", reply_markup=markup)
                    bot.register_next_step_handler(msg, download_file_from_single_list)

                elif len(result) > 1:
                    db.insert_multiple(result)
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                                                       input_field_placeholder="Trying Placeholder")

                    _1 = types.KeyboardButton('1')
                    _2 = types.KeyboardButton('2')
                    _3 = types.KeyboardButton('3')
                    _4 = types.KeyboardButton('4')
                    _5 = types.KeyboardButton('5')
                    _6 = types.KeyboardButton('6')
                    _7 = types.KeyboardButton('7')
                    _8 = types.KeyboardButton('8')
                    _9 = types.KeyboardButton('9')

                    markup.add(_1, _2, _3, _4, _5, _6, _7, _8, _9)

                    msg = bot.send_message(message.chat.id, "*Which of this do you said you want?* \n"
                                                            f"{message_text}",
                                           parse_mode="Markdown", reply_markup=markup)
                    bot.register_next_step_handler(msg, down_load_file_from_multiple_list)

    except Exception as exc:
        print('Something went wrong in search by title section')
        bot.reply_to(message, "Oops something went wrong!, Let try it "
                              "again. Please click /start")


def user_input_book_author(message):
    try:

        if message.text is not None or "author:" in message.text.lower():
            bot.send_message(message.chat.id, "Searching the dataBase for Matches...")
            book_author = message.text.lower()

            # book_author_ = message.text.lower().split()
            # book_author_.pop(0)
            # book_author__ = book_author_
            # book_author = ""
            #
            # for word in book_author__:
            #     book_author = book_author + word
            #     book_author = book_author + " "
            #
            # book_author = book_author.strip()

            response = requests.get(f"https://christianbooks-bot-api.herokuapp.com/api/book/?author={book_author}")

            result = []
            data = response.json()['queryset']
            print(data)

            if not data:
                bot.send_message(message.chat.id,
                                 f"I'm sorry, I could'nt find any book in my database that marches your "
                                 f"search '{book_author.capitalize()}'!"
                                 f"\nPlease check your input carefully and try again or you search by Author instead.")
            else:
                for index, item in enumerate(data):
                    result_dict = {'user_id': f"{message.from_user.id}", 'rank': index + 1,
                                   'id': item['id'], 'title': item['title'], 'author': item['author'],
                                   'file': item['file']}
                    result.append(result_dict)

                message_text = ""
                # global_result = result

                print("line 155: ", result)
                for item in result:
                    line = f"\n{item['rank']}.   {item['title']} by {item['author']}"
                    message_text = message_text + line

                if len(result) == 1:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                                                       input_field_placeholder="Trying Placeholder")
                    db.insert(
                        {'user_id': f"{message.from_user.id}", 'file_id': result[0]['id'], 'file': result[0]['file'],
                         'file_title': f"{result[0]['title']}", 'file_author': f"{result[0]['author']}",
                         'status': 'pending'})

                    _yes = types.KeyboardButton('Yes, exactly 😊')
                    _no = types.KeyboardButton('No, not this 😌')

                    markup.add(_yes, _no)
                    msg = bot.send_message(message.chat.id, "*Do you mean this?* \n"
                                                            f"{message_text}",
                                           parse_mode="Markdown", reply_markup=markup)
                    bot.register_next_step_handler(msg, download_file_from_single_list)

                elif len(result) > 1:
                    db.insert_multiple(result)
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                                                       input_field_placeholder="Trying Placeholder")

                    _1 = types.KeyboardButton('1')
                    _2 = types.KeyboardButton('2')
                    _3 = types.KeyboardButton('3')
                    _4 = types.KeyboardButton('4')
                    _5 = types.KeyboardButton('5')
                    _6 = types.KeyboardButton('6')
                    _7 = types.KeyboardButton('7')
                    _8 = types.KeyboardButton('8')
                    _9 = types.KeyboardButton('9')

                    markup.add(_1, _2, _3, _4, _5, _6, _7, _8, _9)

                    msg = bot.send_message(message.chat.id, "*Which of this would you like to get?* \n"
                                                            f"{message_text}",
                                           parse_mode="Markdown", reply_markup=markup)
                    bot.register_next_step_handler(msg, down_load_file_from_multiple_list)

    except Exception as exc:
        print('Something went wrong in search by author section')
        bot.reply_to(message, "Oops something went wrong!, Let try it "
                              "again. Please click /start")

    # ---------------------------------------------------------------------------------------------------------------------------
    if "book feedback" in message.text.lower():
        bot.register_next_step_handler(message, book_feedback_branch())


@bot.message_handler(commands=['feedback'])
def book_feedback_branch(message):
    # set up markup for keyboard
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True,
                                       input_field_placeholder="book title, feedback")
    bot.send_message(message.chat.id, "Brilliant!, please write your feedback in this format: "
                                      "\n*book title, feedback*",
                     parse_mode="Markdown", reply_markup=markup)


def down_load_file_from_multiple_list(message):
    try:
        if message.text is not None:
            User = Query()
            query_rank = db.search(User.rank == int(message.text))
            print(query_rank)
            bot.reply_to(message, "Fetching Document...")
            document = query_rank[0]['file']
            caption = f"{query_rank[0]['title']} by {query_rank[0]['author']}"
            bot.send_document(message.chat.id, document, caption=caption)
            db.remove(User.user_id == f'{message.from_user.id}')
        else:
            User = Query()
            db.remove(User.user_id == f'{message.from_user.id}')
    except Exception as e:
        print(e)
        bot.reply_to(message, "Oops something went wrong!, input is not in the list i showed you. If you like to try "
                              "again click /start")


def download_file_from_single_list(message):
    try:
        if message.text is not None and "yes, exactly" in message.text.lower():
            User = Query()

            bot.reply_to(message, "Fetching Document...")
            query_list = db.search(User.user_id == f'{message.from_user.id}')

            document = query_list[0]['file']
            caption = f"{query_list[0]['file_title']} by {query_list[0]['file_author']}"

            bot.send_document(message.chat.id, document, caption=caption)
            db.remove(User.user_id == f'{message.from_user.id}')

            last_msg = "\n" \
                       "\nThanks. Please do well to tell your friends about me." \
                       "\nYou can also drop a /feedback"
            bot.send_message(message.chat.id, last_msg)
        elif message.text is not None and "no, not this" in message.text.lower():
            User = Query()

            msg = bot.send_message(message.chat.id, "Oops..., sorry about that, Let try again. Please click /start")
            db.remove(User.user_id == f'{message.from_user.id}')
            bot.register_next_step_handler(msg, message_path)

    except Exception as e:
        bot.reply_to(message, "Oops something went wrong!, let try again. Please click /start")

    # else:
    #     bot.send_message(message.chat.id,
    #                      "Sorry i could not process what you request for, let try again.")


#     while True:  # Don't end the main thread.
#         bot.send_message(message.chat.id, "What's the author name?_")
#         if 'Roberts ' in message.text:
#             bot.send_document(message.chat.id, document, caption="Thanks, that's the file you requested for")
#
#         pass
#
bot.enable_save_next_step_handlers(delay=1)

bot.load_next_step_handlers()

while True:
    try:
        bot.polling()
    except Exception as e:
        time.sleep(5)

        # response = requests.get("http://127.0.0.1:8000/api/download/?id=8")
        # file_ = response.json()['queryset'][0]['file']
        # file_title = response.json()['queryset'][0]['title']
        #
        # print(file_)
        # print(file_title)
        # # test_file = 'http://res.cloudinary.com/pycodet/image/upload/Purpose_Driven_Life.pdf'
        #
        # bot.send_message(message.chat.id, "Request is processing...")
        # bot.send_document(message.chat.id, file_, caption=file_title)
