
import logging
import random
import gspread 
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

from random import randint
from telegram import (
    Poll,
    ParseMode,
    KeyboardButton,
    KeyboardButtonPollType,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    PollAnswerHandler,
    PollHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

ABUSE_STRINGS = (
    "Fuck off",
    "Stfu go fuck yourself",
    "Ur mum gey",
    "Ur dad lesbo",
    "Bsdk",
    "Ur granny tranny",
    "you noob",
	"Stfu bc",
	"Stfu and Gtfo U nub",
	"GTFO bsdk",
    " Gay is here",
    "Ur dad gey bc "
) 

TOSS = (
    "Heads",
    "Tails",
)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    """Inform user about what this bot can do"""
    update.message.reply_text(
        '''Hello this is VOST, how may I help you today?
        
Please select:
/poll to get a Poll on Monday\'s test schedule
/quiz to get a Quiz on dbms 
/preview to generate a preview for your poll
/poc to get info on Point of contact for IT dept
/roll to roll a dice
/toss to flip a coin
/abuse if you're having a good day.
/shrug . to get shruged
/decide to let the bot decide something for you
/rickroll to get rickrolled'''
    )


def poll(update: Update, context: CallbackContext) -> None:
    """Sends a predefined poll"""
    questions = ["12.30-1:00", "2:30-3:00", "4:30-5:00", "7:30-8:00"]
    message = context.bot.send_poll(
        update.effective_chat.id,
        "Which slot would you prefer for monday's test?",
        questions,
        is_anonymous=False,
        allows_multiple_answers=True,
    )
    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }
    context.bot_data.update(payload)


def receive_poll_answer(update: Update, context: CallbackContext) -> None:
    """Summarize a users poll vote"""
    answer = update.poll_answer
    poll_id = answer.poll_id
    try:
        questions = context.bot_data[poll_id]["questions"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return
    selected_options = answer.option_ids
    answer_string = ""
    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + " and "
        else:
            answer_string += questions[question_id]
    context.bot.send_message(
        context.bot_data[poll_id]["chat_id"],
        f"{update.effective_user.mention_html()} {answer_string} slot has been reserved for you!",
        parse_mode=ParseMode.HTML,
    )
    context.bot_data[poll_id]["answers"] += 1
    # Close poll after three participants voted
    if context.bot_data[poll_id]["answers"] == 3:
        context.bot.stop_poll(
            context.bot_data[poll_id]["chat_id"], context.bot_data[poll_id]["message_id"]
        )


def quiz(update: Update, context: CallbackContext) -> None:
    """Send a predefined poll"""
    questions = ["Degree", "Tuples", "Entity", "All of the above"]
    message = update.effective_message.reply_poll(
        "Rows of a relation are known as?", questions, type=Poll.QUIZ, correct_option_id=3
    )
    # Save some info about the poll the bot_data for later use in receive_quiz_answer
    payload = {
        message.poll.id: {"chat_id": update.effective_chat.id, "message_id": message.message_id}
    }
    context.bot_data.update(payload)


def receive_quiz_answer(update: Update, context: CallbackContext) -> None:
    """Close quiz after three participants took it"""
    # the bot can receive closed poll updates we don't care about
    if update.poll.is_closed:
        return
    if update.poll.total_voter_count == 3:
        try:
            quiz_data = context.bot_data[update.poll.id]
        # this means this poll answer update is from an old poll, we can't stop it then
        except KeyError:
            return
        context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])


def preview(update: Update, context: CallbackContext) -> None:
    """Ask user to create a poll and display a preview of it"""
    # using this without a type lets the user chooses what he wants (quiz or poll)
    button = [[KeyboardButton("Press me!", request_poll=KeyboardButtonPollType())]]
    message = "Press the button to let the bot generate a preview for your poll"
    # using one_time_keyboard to hide the keyboard
    update.effective_message.reply_text(
        message, reply_markup=ReplyKeyboardMarkup(button, one_time_keyboard=True)
    )

# def unknown_message(update: Update, context: CallbackContext):
#     context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry I've not been programmed to understand this message yet")

# randomtext_handler = MessageHandler(Filters.text & (~Filters.command), unknown_message)


def receive_poll(update: Update, context: CallbackContext) -> None:
    """On receiving polls, reply to it by a closed poll copying the received poll"""
    actual_poll = update.effective_message.poll
    # Only need to set the question and options, since all other parameters don't matter for
    # a closed poll
    update.effective_message.reply_poll(
        question=actual_poll.question,
        options=[o.text for o in actual_poll.options],
        # with is_closed true, the poll/quiz is immediately closed
        is_closed=True,
        reply_markup=ReplyKeyboardRemove(),
    )


def help_handler(update: Update, context: CallbackContext) -> None:
    """Display a help message"""
    update.message.reply_text("Use /quiz, /poll or /preview to test this bot.")

def poc_handler(update: Update, context: CallbackContext) -> None:
    """Display a help message"""
    update.message.reply_text('''These are the contact information for IT department:

Teaching Staff:
Shiv Negi -              wa.me/+919819002150
Tayyabali Sayyed -       wa.me/+918605134503
Nilesh Ghavate -         wa.me/+919594813901
Prasad Padalkar -        wa.me/+919967555817

Dept HOD:
Janhavi Baikerikar -     wa.me/+919833348725''')

def credits_handler(update: Update, context: CallbackContext) -> None:
    """Display a help message"""
    update.message.reply_text("Hello I am Vost.")

def roll(update: Update, context: CallbackContext):
    update.message.reply_text(random.choice(range(1, 10)))
	
def toss(update: Update, context: CallbackContext):
    update.message.reply_text(random.choice(TOSS))

def abuse(update: Update, context: CallbackContext):
    # reply to correct message
    reply_text = update.effective_message.reply_to_message.reply_text if update.effective_message.reply_to_message else update.effective_message.reply_text
    reply_text(random.choice(ABUSE_STRINGS))

def shrug(update: Update, context: CallbackContext):
    # reply to correct message
    reply_text = update.effective_message.reply_to_message.reply_text if update.effective_message.reply_to_message else update.effective_message.reply_text
    reply_text("¯\_(ツ)_/¯")

def decide(update: Update, context: CallbackContext):
        r = randint(1, 100)
        if r <= 65:
            update.message.reply_text("Yes.")
        elif r <= 90:
            update.message.reply_text("NoU.")
        else:
            update.message.reply_text("Maybe.")

def rickroll(update, context):
    # update.message.reply_text('The file is downloading')
    # context.bot.sendDocument(update.effective_chat.id, document=open('python-basics-sample-chapters.pdf', 'rb'))
    context.bot.sendDocument(update.effective_chat.id, "https://media.giphy.com/media/Ju7l5y9osyymQ/giphy.gif")
# def unknown(update: Update, context: CallbackContext):
#     context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

def getmetutorial(update, context):
    # update.message.reply_text('The file is downloading')
    # context.bot.sendDocument(update.effective_chat.id, document=open('python-basics-sample-chapters.pdf', 'rb'))
    context.bot.sendDocument(update.effective_chat.id, "https://drive.google.com/uc?export=download&id=1Dup4IQo4cJeOGS7lMHJ1Ug5J9EiOugIrY4M221e5cJA") 

# unknown_handler = MessageHandler(Filters.command, unknown)

def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("5128996956:AAGxnVrJImju7iMz2D3Wdf_pPtbhi11BxeM")
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('poll', poll))
    dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))
    dispatcher.add_handler(CommandHandler('quiz', quiz))
    dispatcher.add_handler(PollHandler(receive_quiz_answer))
    dispatcher.add_handler(CommandHandler('preview', preview))
    dispatcher.add_handler(MessageHandler(Filters.poll, receive_poll))
    dispatcher.add_handler(CommandHandler('help', help_handler))
    dispatcher.add_handler(CommandHandler('poc', poc_handler))
    dispatcher.add_handler(CommandHandler('vost', credits_handler))
    # dispatcher.add_handler(unknown_handler)
    # dispatcher.add_handler(randomtext_handler)
    dispatcher.add_handler(CommandHandler('roll', roll))
    dispatcher.add_handler(CommandHandler('toss', toss))
    dispatcher.add_handler(CommandHandler('abuse', abuse))
    dispatcher.add_handler(CommandHandler('shrug', shrug))
    dispatcher.add_handler(CommandHandler('decide', decide))
    dispatcher.add_handler(CommandHandler('rickroll', rickroll))
    dispatcher.add_handler(CommandHandler('getmetutorial', getmetutorial))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()