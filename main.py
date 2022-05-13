from __future__ import print_function
import os
from submissionFolderPath import file_ids
from academicDocsFolderPath import doc_ids
import pickle
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import telegram
import logging
import pyfiglet
import config
import requests
from functools import wraps
from bot_responses import * 
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
    MessageHandler, Filters
)
from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup, Update

PORT = os.environ.get('PORT')
if PORT:
    # get the heroku port 
    port = int(os.environ.get("PORT"))  
else:
    port = 8443
  
logging.basicConfig(filename='bot_usage.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_USERS = ['saanvi_naik', 'tushar_493', 'vendra_0408', 'jannuom']
STUDENTS = ['saanvi_naik', 'tushar_493', 'vendra_0408']

DEPARTMENT, SEMESTER, SUBJECT, WAIT_STATE, SETFID, YEAR, CHOOSE_FILE, SETDID, SENDFILE, DEPARTMENTINFO, YEARINFO, SEMESTERINFO = range(12)
file_ids
doc_ids

def getCreds():
  # The file token.pickle stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  creds = None
  DRIVE_TOKEN_FILE = "token.pickle"
  SCOPES = 'https://www.googleapis.com/auth/drive'

  if os.path.exists('token.pickle'):
      with open('token.pickle', 'rb') as token:
          creds = pickle.load(token)
  else:
    print("Either tokenpickle is missing or is invalid. Regenerate it using generate_token.py")
    
  return creds

def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_name = update.effective_user.username
        if user_name not in STUDENTS:
            update.message.reply_text(f"Unauthorized access denied for {user_name}. This function is only for students")
            logging.info('Unauthorized access denied for %s on accessing a student feature: %s.', str(user_name), func)
            return
        return func(update, context, *args, **kwargs)
    return wrapped

def restricted_User(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_name = update.effective_user.username
        if user_name not in ALLOWED_USERS:
            update.message.reply_text(f"Unauthorized access denied for {user_name}.")
            logging.info('Unauthorized access denied for %s on accessing %s.', str(user_name), func)

            return
        return func(update, context, *args, **kwargs)
    return wrapped

def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator

send_typing_action = send_action(ChatAction.TYPING)
send_upload_file_action = send_action(ChatAction.UPLOAD_DOCUMENT)

def start(update: Update, context: CallbackContext) -> None:
    pass 
    update.message.reply_text('''Welcome to VOST! 
This bot helps in users to submit their assignments and also know more about DBIT.

Click /help to know more on how to use the bot.
/submission - Use this command to submit your files and documents. 
/Academic_documents - Use this command to view and download the annual documents like exam seat number, hall ticket, time table and academic calendar.
/College_information - Use this command to know more about DBIT i.e. student clubs, student chapters, cultural fest, technical fest. 
/poc - Use this command to get point of contact i.e information about professors in DBIT branch wise. 
/vost - to know more about the bot.
'''
)

"""to bot send files stored in your server"""
@send_upload_file_action
def collegeBrochure(update, context):
    context.bot.sendDocument(update.effective_chat.id, document=open('pdfFiles/brochure.pdf', 'rb'), filename="brochure.pdf")

def error(bot, update, error):
  logger.warning('Update "%s" caused error "%s"', update, error)

#This is to choose attribues for /submission feature
@restricted   
def select_year(update, context) -> int:
    buttons = []
    for year in file_ids.keys():
        buttons.append([InlineKeyboardButton(year, callback_data=year)])

    reply_markup = InlineKeyboardMarkup(buttons)  
    update.message.reply_text("Select the year in which you are studying:", reply_markup=reply_markup)
    return DEPARTMENT

def select_department(update, context) -> int:
    query = update.callback_query
    query.answer()
    year = query.data
    buttons = []
    for department in file_ids[year].keys():
        buttons.append([InlineKeyboardButton(department, callback_data=f'{year}|{department}')])

    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text="Choose your Department:", reply_markup=reply_markup)
    return SEMESTER

def select_semester(update, context) -> int:
    query = update.callback_query
    query.answer()
    year, department = update.callback_query.data.split("|")
    buttons = []
    for semester in file_ids[year][department].keys():
        buttons.append([InlineKeyboardButton(semester, callback_data=update.callback_query.data+f"|{semester}")])
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text="Choose your Semester:", reply_markup=reply_markup)
    
    return SUBJECT

def select_subject(update, context) -> int:
    query = update.callback_query
    query.answer()
    year, department, semester = update.callback_query.data.split("|") 
    buttons = []
    for subject in file_ids[year][department][semester].keys():
        buttons.append([InlineKeyboardButton(subject, callback_data=file_ids[year][department][semester][subject])])

    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text="Choose a Subject:", reply_markup=reply_markup)
    return SETFID      
   
def subject_was_selected(update, context):
    #save file_id in the context
    query = update.callback_query
    query.answer()
    user_name = update.effective_user.username
  
    context.user_data["file_ids"] = update.callback_query.data
    query.edit_message_text("Now send your file", reply_markup=None)
    return WAIT_STATE

@send_typing_action
def file_uploader(update, context):
  """handles the uploaded files"""
  file = context.bot.getFile(update.message.document.file_id)
  file.download(update.message.document.file_name)

  doc = update.message.document

  service = build('drive', 'v3', credentials=getCreds(),cache_discovery=False)
  filename = doc.file_name
  
  metadata = {'name': filename,
              'parents': [context.user_data["file_ids"]]
  }
  media = MediaFileUpload(filename, chunksize=1024 * 1024, mimetype=doc.mime_type,  resumable=True)
  request = service.files().create(body=metadata,
                                media_body=media)
  user_name = update.effective_user.username
  response = None
  while response is None:
    status, response = request.next_chunk()
    if status:
       print( "Uploaded %d%%." % int(status.progress() * 100))

  context.bot.send_message(chat_id=update.effective_chat.id, text="✅ File uploaded!")
  logging.info('%s uploaded %s', str(user_name), str(filename))

  os.remove(filename)
  return ConversationHandler.END

def getAcademicFiles(update, context) -> None:
    update.message.reply_text('''Select your year, branch and semester to get the files accordingly
tap /userinfo to start''')
    return YEARINFO  
  
#This is to choose attributes for /Academic_documents feature
def select_yearinfo(update, context) -> int:
    buttons = []
    for year in file_ids.keys():
        buttons.append([InlineKeyboardButton(year, callback_data=year)])

    reply_markup = InlineKeyboardMarkup(buttons)  
    update.message.reply_text("Select the year in which you are studying:", reply_markup=reply_markup)
    return DEPARTMENTINFO

def select_departmentinfo(update, context) -> int:
    query = update.callback_query
    query.answer()
    year = query.data
    buttons = []
    for department in doc_ids[year].keys():
        buttons.append([InlineKeyboardButton(department, callback_data=f'{year}|{department}')])

    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text="Choose your Department:", reply_markup=reply_markup)
    return SEMESTERINFO

def select_semesterinfo(update, context) -> int:
    query = update.callback_query
    query.answer()
    year, department = update.callback_query.data.split("|")
    buttons = []
    for semester in doc_ids[year][department].keys():
        buttons.append([InlineKeyboardButton(semester, callback_data=update.callback_query.data+f"|{semester}")])
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text="Choose your Semester:", reply_markup=reply_markup)
    
    return CHOOSE_FILE

def selectFile(update, context) -> int:
    query = update.callback_query
    query.answer()
    year, department, semester = update.callback_query.data.split("|")
    buttons = []
    for file in doc_ids[year][department][semester].keys():
        buttons.append([InlineKeyboardButton(file, callback_data=doc_ids[year][department][semester][file])])
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text="Choose a file:", reply_markup=reply_markup)
    return SETDID

@send_upload_file_action
def file_was_selected(update, context):
    #save file_id in the context
    query = update.callback_query
    query.answer()
    path = str(update.callback_query.data)
    print(path)
    
    query.edit_message_text("Your file is on the way", reply_markup=None)
    context.bot.sendDocument(update.effective_chat.id, document=open(f"{path}", 'rb'))
    ConversationHandler.END

conv_handler = ConversationHandler(
        entry_points=[CommandHandler('submission', select_year)],
        states={
            DEPARTMENT: [CallbackQueryHandler(select_department)],
            SEMESTER: [CallbackQueryHandler(select_semester)],
            SUBJECT: [CallbackQueryHandler(select_subject)],
            SETFID: [CallbackQueryHandler(subject_was_selected)],
            WAIT_STATE: [MessageHandler(Filters.document,file_uploader)]
        },
        fallbacks=[CommandHandler('submissions', select_year)],
    )

fileRequest_handler = ConversationHandler(
        entry_points=[CommandHandler('academic_documents', getAcademicFiles)],
        states={
            YEARINFO: [CommandHandler('userinfo', select_yearinfo)],
            DEPARTMENTINFO: [CallbackQueryHandler(select_departmentinfo)],
            SEMESTERINFO: [CallbackQueryHandler(select_semesterinfo)],
            CHOOSE_FILE: [CallbackQueryHandler(selectFile)],
            SETDID: [CallbackQueryHandler(file_was_selected)],
        },
        fallbacks=[CommandHandler('academic_documents', getAcademicFiles)]    )

@restricted_User
def poc_handler(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(poc_response)

@restricted_User
def CompsPoc(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(CompsPoc_response)

@restricted_User
def ItPoc(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(ItPoc_reponse)

@restricted_User
def ExtcPoc(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(ExtcPoc_response)

@restricted_User
def MechPoc(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(MechPoc_response)

def getCollegeInfo(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(CollegeInfoResponse)

def help(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(helpResponse)

def studentClubs(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(studentClubsResponse)

def studentChapters(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(studentChaptersResponse)

def technicalEvents(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(technicalEventsResponse)

def csi(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(csiResponse)

@send_upload_file_action
def csiBrochure(update, context):
    context.bot.send_document(update.effective_chat.id, document=open('pdfFiles/brochure.pdf', 'rb'), filename="CSI_brochure.pdf")

def ieee(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(ieeeResponse)

def iete(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(ieteResponse)

def madgears(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(madgearsResponse)

def ishrae(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(ishraeResponse)

def acm(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(acmResponse)

def lisoc(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(litsocResponse)

def sie(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(sieResponse)

def ecell(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(ecellResponse)

def musicClub(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(musicClubResponse)

def dramaClub(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(dramaClubResponse)

def danceClub(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(danceClubResponse)

def marathiClub(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(marathiClubResponse)

# def unknown(update, context):
#     user_name = update.effective_user.first_name
#     if user_name in ALLOWED_USERS:
#         context.bot.send_message(chat_id=update.effective_chat.id, text=f"Sorry, {user_name} I couldn't understand that command.")
#     else:
#         pass

def vost(update, context):
    update.message.reply_text(vostResponse)
  
TOKEN = os.environ['TOKEN']

def main():
  updater = Updater(token=TOKEN,use_context=True)
  dispatcher = updater.dispatcher
  updater.dispatcher.add_handler(CommandHandler('start', start))
  dispatcher.add_handler(CommandHandler('help', help))
  dispatcher.add_handler(CommandHandler('vost', vost))
#   dispatcher.add_handler(MessageHandler(Filters.command, unknown))
  dispatcher.add_handler(conv_handler)
  dispatcher.add_handler(fileRequest_handler)
  dispatcher.add_handler(CommandHandler('academic_documents', getAcademicFiles))

  
#POC HANDLERS AND ITS SUBFUNCTIONS STARTS HERE
  dispatcher.add_handler(CommandHandler('poc', poc_handler))
  dispatcher.add_handler(CommandHandler('COMPS', CompsPoc))
  dispatcher.add_handler(CommandHandler('IT', ItPoc))
  dispatcher.add_handler(CommandHandler('EXTC', ExtcPoc))
  dispatcher.add_handler(CommandHandler('MECH', MechPoc))
  
#COLLEGE INFORMATION AND ITS SUBFUNCTIONS STARTS HERE
  updater.dispatcher.add_handler(CommandHandler('College_information', getCollegeInfo))
  dispatcher.add_handler(CommandHandler('getmeBrochure', collegeBrochure))
  
#STUDENT CHAPTER STARTS HERE
  updater.dispatcher.add_handler(CommandHandler('Student_chapters', studentChapters))
  updater.dispatcher.add_handler(CommandHandler('csi', csi))
  dispatcher.add_handler(CommandHandler('csi_brochure', csiBrochure))
  updater.dispatcher.add_handler(CommandHandler('ieee', ieee))
  updater.dispatcher.add_handler(CommandHandler('iete', iete))
  updater.dispatcher.add_handler(CommandHandler('madgears', madgears))
  updater.dispatcher.add_handler(CommandHandler('ishrae', ishrae))
  updater.dispatcher.add_handler(CommandHandler('acm', acm))

#STUDENT CLUBS STARTS HERE
  updater.dispatcher.add_handler(CommandHandler('Student_clubs', studentClubs))
  updater.dispatcher.add_handler(CommandHandler('LITSOC', lisoc))
  updater.dispatcher.add_handler(CommandHandler('SIE', sie))
  updater.dispatcher.add_handler(CommandHandler('ECELL', ecell))
  dispatcher.add_handler(CommandHandler('Music_Club', musicClub))
  updater.dispatcher.add_handler(CommandHandler('Dance_Club', danceClub))
  updater.dispatcher.add_handler(CommandHandler('Drama_Club', dramaClub))
  updater.dispatcher.add_handler(CommandHandler('Marathi_Club', marathiClub))
  
  # updater.start_webhook(listen="0.0.0.0",
  #                     port=int(PORT),
  #                     url_path=config.TOKEN,
  #                     webhook_url = "https://vost-bot-tg.herokuapp.com/" + config.TOKEN)
                      
  updater.start_polling()

if __name__ == '__main__':
    ascii_banner = pyfiglet.figlet_format("VOST   TELEGRAM   BOT")
    print(ascii_banner)
    main()
