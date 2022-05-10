from __future__ import print_function
import os
from path import file_ids
from path2 import doc_ids
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

PORT = int(os.environ.get('PORT', '8443'))

logging.basicConfig(filename='bot_usage.log', filemode='w', encoding='utf-8', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_USERS = ['tushar_493', 'saanvi_naik']
STUDENTS = ['tushar_493', 'saanvi_naik']

def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_name = update.effective_user.username
        if user_name not in STUDENTS:
            update.message.reply_text(f"Unauthorized access denied for {user_name}.")
            return
        return func(update, context, *args, **kwargs)
    return wrapped

from functools import wraps

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

def getCreds():
  # The file token.pickle stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  creds = None
  SCOPES = 'https://www.googleapis.com/auth/drive'

  if os.path.exists('token.pickle'):
      with open('token.pickle', 'rb') as token:
          creds = pickle.load(token)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
      else:
          flow = InstalledAppFlow.from_client_secrets_file(
              'credentials.json', SCOPES)
          creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open('token.pickle', 'wb') as token:
          pickle.dump(creds, token)

  return creds

DEPARTMENT, SEMESTER, SUBJECT, WAIT_STATE, SETFID, YEAR, CHOOSE_FILE, SETDID, SENDFILE = range(9)
file_ids
doc_ids

def start(update: Update, context: CallbackContext) -> None:
    pass 
    update.message.reply_text('''Welcome to VOST! 
This bot helps in users to submit their assignments and also know more about DBIT.

Click /help to know more about the bot.
/submission - Use this command to submit your files and documents. 
/Academic_documents - Use this command to view and download the annual documents like exam seat number, hall ticket, time table and academic calendar.
/College_information - Use this command to know more about DBIT i.e. student clubs, student chapters, cultural fest, technical fest. 
/poc - Use this command to get point of contact i.e information about professors in DBIT branch wise. 

'''
)

# @send_upload_file_action
# def collegeBrochure(update, context):
    
#     context.bot.sendDocument(update.effective_chat.id, document=open('pdfFiles/brochure.pdf', 'rb'), filename="brochure.pdf")
#     os.remove('brochure.pdf')

@send_upload_file_action
def collegeBrochure(update, context):

    context.bot.sendDocument(update.effective_chat.id, document=open('pdfFiles/brochure.pdf', 'rb'), filename="brochure.pdf")
    os.remove('brochure.pdf')
    
    # # fetch from Google Drive
    # url = 'https://github.com/tushar4303/VOST/blob/main/pdfFiles/ExamTimetable/SE/SE_IT_Sem4_C-Scheme.pdf'
    # r = requests.get(url, allow_redirects=True)
    # # save local copy
    # open('file.pdf', 'wb').write(r.content)# send file to user
    # context.bot.sendDocument(update.effective_chat.id, document=open('file.pdf', 'rb'), filename="timetable.pdf")
    # os.remove('timetable.pdf')

def error(bot, update, error):
  logger.warning('Update "%s" caused error "%s"', update, error)
    
@restricted
def select_year(update, context) -> int:
    buttons = []
    for year in file_ids.keys():
        buttons.append([InlineKeyboardButton(year, callback_data=year)])

    reply_markup = InlineKeyboardMarkup(buttons)  
    update.message.reply_text("Select the year in which you are studying:", reply_markup=reply_markup)
    return DEPARTMENT

def select_yearinfo(update, context) -> int:
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

def file_was_selected(update, context):
    #save file_id in the context
    query = update.callback_query
    query.answer()
    context.user_data["doc_ids"] = str(update.callback_query.data)
    
    query.edit_message_text("Your file is on the way", reply_markup=None)
    # context.bot.sendDocument(update.effective_chat.id, document=open("{context.user_data["doc_ids"]}"))
    print
    # return SENDFILE

def file_sender(update, context):
    print(str(context.user_data["doc_ids"]))
    # context.bot.sendDocument(update.effective_chat.id, document=open([context.user_data["doc_ids"]], 'rb'))

def getAcademicFiles(update, context) -> None:
    update.message.reply_text('''Select your year, branch and semester to get the files accordingly
tap /userinfo to start''')
    return YEAR
    
def subject_was_selected(update, context):
    #save file_id in the context
    query = update.callback_query
    query.answer()
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
            YEAR: [CommandHandler('userinfo', select_yearinfo)],
            DEPARTMENT: [CallbackQueryHandler(select_department)],
            SEMESTER: [CallbackQueryHandler(select_semesterinfo)],
            CHOOSE_FILE: [CallbackQueryHandler(selectFile)],
            SETDID: [CallbackQueryHandler(file_was_selected)],
            # SENDFILE: [CallbackQueryHandler(file_sender)]
        },
        fallbacks=[CommandHandler('academic_documents', getAcademicFiles)],
    )

def poc_handler(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(poc_response)

def getCollegeInfo(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(CollegeInfoResponse)

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

def main():
  updater = Updater(token=config.TOKEN,use_context=True)
  dispatcher = updater.dispatcher
  updater.dispatcher.add_handler(CommandHandler('start', start))
  dispatcher.add_handler(conv_handler)
  dispatcher.add_handler(fileRequest_handler)
  dispatcher.add_handler(CommandHandler('getmeBrochure', collegeBrochure))
  updater.dispatcher.add_handler(CommandHandler('poc', poc_handler))
  updater.dispatcher.add_handler(CommandHandler('College_information', getCollegeInfo))
  updater.dispatcher.add_handler(CommandHandler('Student_chapters', studentChapters))
  updater.dispatcher.add_handler(CommandHandler('csi', csi))
  updater.dispatcher.add_handler(CommandHandler('ieee', ieee))
  updater.dispatcher.add_handler(CommandHandler('iete', iete))
  updater.dispatcher.add_handler(CommandHandler('madgears', madgears))
  updater.dispatcher.add_handler(CommandHandler('ishrae', ishrae))
  updater.dispatcher.add_handler(CommandHandler('acm', acm))
  updater.dispatcher.add_handler(CommandHandler('Student_clubs', studentClubs))
  updater.dispatcher.add_handler(CommandHandler('LITSOC', lisoc))
  updater.dispatcher.add_handler(CommandHandler('SIE', sie))
  updater.dispatcher.add_handler(CommandHandler('ECELL', ecell))
  updater.dispatcher.add_handler(CommandHandler('Music_Club', musicClub))
  updater.dispatcher.add_handler(CommandHandler('Dance_Club', danceClub))
  updater.dispatcher.add_handler(CommandHandler('Drama_Club', dramaClub))
  updater.dispatcher.add_handler(CommandHandler('Marathi_Club', marathiClub))
  updater.dispatcher.add_handler(CommandHandler('academic_documents', getAcademicFiles))

  # updater.start_webhook(listen="0.0.0.0",
  #                     port=int(PORT),
  #                     url_path=config.TOKEN,
  #                     webhook_url = "https://vost-bot-tg.herokuapp.com/" + config.TOKEN)
                      
  updater.start_polling()

if __name__ == '__main__':
    ascii_banner = pyfiglet.figlet_format("VOST   TELEGRAM   BOT")
    print(ascii_banner)
    main()