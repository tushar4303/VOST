poc_reponse = '''These are the contact information for IT department:
Teaching Staff:
Shiv Negi -              wa.me/+919819002150
Tayyabali Sayyed -       wa.me/+918605134503
Nilesh Ghavate -         wa.me/+919594813901
Prasad Padalkar -        wa.me/+919967555817
Dept HOD:
Janhavi Baikerikar -     wa.me/+919833348725
'''

grade_response = '''Please select one from the following:
/FE - for First year
/SE - for Second year
/TE - for Third year
/BE - for Final year
'''

# def subject_was_selected(update, context):
#     #save file_id in the context
#     context.user_data["folder_id"] = update.callback_query.data
#     update.message.edit_text("Now send your file", reply_markup=None)

# def file_uploader(update, context):
#   """handles the uploaded files"""
#   query = update.callback_query
#   query.answer()

#   file = context.bot.getFile(update.message.document.file_id)
#   file.download(update.message.document.file_name)

#   doc = update.message.document

#   service = build('drive', 'v3', credentials=getCreds(),cache_discovery=False)
#   filename = doc.file_name
  
#   metadata = {'name': filename,
#               'parents': [context.user_data]
#   }
#   media = MediaFileUpload(filename, chunksize=1024 * 1024, mimetype=doc.mime_type,  resumable=True)
#   request = service.files().create(body=metadata,
#                                 media_body=media)

#   response = None
#   while response is None:
#     status, response = request.next_chunk()
#     if status:
#        print( "Uploaded %d%%." % int(status.progress() * 100))

#   context.bot.send_message(chat_id=update.effective_chat.id, text="✅ File uploaded!")
#   os.remove(filename)
#   return ConversationHandler.END

# conv_handler = ConversationHandler(
#         entry_points=[CommandHandler('submissions', select_year)],
#         states={
#             DEPARTMENT: [CallbackQueryHandler(select_department)],
#             SEMESTER: [CallbackQueryHandler(select_semester)],
#             SUBJECT: [CallbackQueryHandler(select_subject)],
#             WAIT_STATE: [MessageHandler(Filters.document,file_uploader)]
#         },
#         fallbacks=[CommandHandler('submissions', select_year)],
#     )