from __future__ import print_function
import os
from path import file_ids
import pickle
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import telegram
import logging
import config
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
folder_id = '1DFStWQd-Y6H0WoWr1E1ByNuElANMzCft'

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

def start(update: Update, context: CallbackContext) -> None:
    """Inform user about what this bot can do"""
    update.message.reply_text(
        '''Hello this is VOST, how may I help you today?
        
Please select:
/poc to get info on Point of contact for IT dept
/submissions to submit your journals and assignments
/getmetutorial to get the sample tutorial
'''
    )

def getmetutorial(update, context):
    # update.message.reply_text('The file is downloading')
    # context.bot.sendDocument(update.effective_chat.id, document=open('python-basics-sample-chapters.pdf', 'rb'))
    context.bot.sendDocument(update.effective_chat.id, "https://drive.google.com/uc?id=11tG8lN-l6aZlkJ16wDCMLAgeSYBeItjg&export=download") 

# def silentremove(filename):
#     try:
        
    # except OSError:
    #     pass
YEAR, DEPARTMENT, SEMESTER, SUBJECT = range(4)
file_ids

def error(bot, update, error):
  logger.warning('Update "%s" caused error "%s"', update, error)
    
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
    print(year)
    print(department)
    print(semester)
    buttons = []
    for subject in file_ids[year][department][semester].keys():
        buttons.append([InlineKeyboardButton(subject, callback_data=file_ids[year][department][semester][subject])])

    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text="Choose a Subject:", reply_markup=reply_markup)
    update.message.reply_text('upload file here')
    return ConversationHandler.END

conv_handler = ConversationHandler(
        entry_points=[CommandHandler('submissions', select_year)],
        states={
            DEPARTMENT: [CallbackQueryHandler(select_department)],
            SEMESTER: [CallbackQueryHandler(select_semester)],
            SUBJECT: [CallbackQueryHandler(select_subject)]
        },
        fallbacks=[CommandHandler('submissions', select_year)],
    )

def file_uploader(update, context):
  """handles the uploaded files"""

  file = context.bot.getFile(update.message.document.file_id)
  file.download(update.message.document.file_name)

  doc = update.message.document

  service = build('drive', 'v3', credentials=getCreds(),cache_discovery=False)
  filename = doc.file_name
  
  metadata = {'name': filename,
              'parents': [folder_id]
  }
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



def poc_handler(update, context) -> None:
    """Display a help message"""
    update.message.reply_text(poc_reponse)

def main():
  updater = Updater(token=config.TOKEN,use_context=True)
  dispatcher = updater.dispatcher
  updater.dispatcher.add_handler(CommandHandler('start', start))
  dispatcher.add_handler(MessageHandler(Filters.document,file_uploader))
  dispatcher.add_handler(conv_handler)
  dispatcher.add_handler(CommandHandler('getmetutorial', getmetutorial))
#   dispatcher.add_handler(CallbackQueryHandler())
#   dispatcher.add_handler(CallbackQueryHandler(CNS, pattern='^' + str(CNS) + '$'))
  updater.start_polling()

if __name__ == '__main__':
    main()