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
from bot_responses import * 
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
    MessageHandler, Filters
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

PORT = int(os.environ.get('PORT', '8443'))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

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
    """Inform user about what this bot can do"""
    update.message.reply_text('''Welcome to VOST! 
This bot helps in users to submit their assignments and also know more about DBIT.

Click /help to know more about the bot.
/submission - Use this command to submit your files and documents. 
/Academic_documents - Use this command to view and download the annual documents like exam seat number, hall ticket, time table and academic calendar.
/College_information - Use this command to know more about DBIT i.e. student clubs, student chapters, cultural fest, technical fest. 
/poc - Use this command to get point of contact i.e information about professors in DBIT branch wise. 

'''
)

def collegeBrochure(update, context):
    # # fetch from Google Drive
    # url = 'https://drive.google.com/file/d/1ktIb4priH8P1iGIghj7CD6UJV5X8Gsm5/view'
    # r = requests.get(url, allow_redirects=True)
    # # save local copy
    # open('brochure.pdf', 'wb').write(r.content)# send file to user
    context.bot.sendDocument(update.effective_chat.id, document=open('pdfFiles/brochure.pdf', 'rb'), filename="brochure.pdf")
    # os.remove('brochure.pdf')

def error(bot, update, error):
  logger.warning('Update "%s" caused error "%s"', update, error)
    
def select_year(update, context) -> int:
    buttons = []
    for year in file_ids.keys():
        buttons.append([InlineKeyboardButton(year, callback_data=year)])

    reply_markup = InlineKeyboardMarkup(buttons)  
    update.message.reply_text("Select the year in which you are studying:", reply_markup=reply_markup)
    return DEPARTMENT

def select_yearinfo(update, context) -> int:
    query = update.callback_query
    query.answer()
    choice = query.data
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
    for file in doc_ids[year][department].keys():
        buttons.append([InlineKeyboardButton(file, callback_data=file_ids[year][department][semester][file])])
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
    context.user_data["doc_ids"] = update.callback_query.data
    query.edit_message_text("Your file is on the way", reply_markup=None)
    return SENDFILE

def subject_was_selected(update, context):
    #save file_id in the context
    query = update.callback_query
    query.answer()
    context.user_data["file_ids"] = update.callback_query.data
    query.edit_message_text("Now send your file", reply_markup=None)
    return WAIT_STATE

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
  print(context.user_data["file_ids"])
  media = MediaFileUpload(filename, chunksize=1024 * 1024, mimetype=doc.mime_type,  resumable=True)
  request = service.files().create(body=metadata,
                                media_body=media)

  response = None
  while response is None:
    status, response = request.next_chunk()
    if status:
       print( "Uploaded %d%%." % int(status.progress() * 100))

  context.bot.send_message(chat_id=update.effective_chat.id, text="✅ File uploaded!")
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
            DEPARTMENT: [CallbackQueryHandler(select_department)],
            SEMESTER: [CallbackQueryHandler(select_semester)],
            SUBJECT: [CallbackQueryHandler(select_subject)],
            SETFID: [CallbackQueryHandler(subject_was_selected)],
            WAIT_STATE: [MessageHandler(Filters.document,file_uploader)]
        },
        fallbacks=[CommandHandler('submissions', select_year)],
    )

def poc_handler(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(poc_reponse)

def getAcademicFiles(update, context) -> None:
    update.message.reply_text("Select your year, branch and semester to get the files accordingly", reply_markup=reply_markup)
    return YEAR

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