poc_reponse = '''These are the contact information for IT department:
Teaching Staff:
Shiv Negi -              wa.me/+919819002150
Tayyabali Sayyed -       wa.me/+918605134503
Nilesh Ghavate -         wa.me/+919594813901
Prasad Padalkar -        wa.me/+919967555817
Dept HOD:
Janhavi Baikerikar -     wa.me/+919833348725
'''

academic_docs_response = '''/Academic_calendar
/Timetable
/Hallticket 
/seatNO

'''

academic_calendar_response = '''{grade_response}


'''

academic_calendar_response = '''/Branch
/Timetable
/Hallticket and seatNO

'''

CollegeInfoResponse = '''
/Student_clubs to know more about active student clubs in DBIT
/Student_chapters for student chapters
/Technical_fest to know about technical events hosted at DBIT
/Cultural_fest for cultural events
'''

studentClubsResponse = '''
/Student_clubs to know more about active student clubs in DBIT
/Student_chapters for student chapters
/Technical_fest to know about technical events hosted at DBIT
/Cultural_fest for cultural events
'''

studentChaptersResponse = '''DBIT's technical chapters and clubs aims to provide one-of-a-kind chances for networking, mentorship, and connecting through shared interests.
These student chapters act as a springboard to forums, panel debates, and symposia that further a student's professional growth.

/csi - Information Technology Dept's official Student Chapter
/ieee - Electronics DEPT's student chapter
/iete - Another student chapter Electronics DEPT of DBIT
/madgears - MECH Dept's official student chapter
/ishrae - Another student chapter by MECH Dept
/acm - Computer Engineering Dept's official Student Chapter
'''

csiResponse = '''CSI (Computer Society of India) is the student chapter of Information Technology department. 

CSI also promotes and supports professionals in maintaining the profession's integrity and competence, 
and it creates a feeling of cooperation among members.

Insta handle:
https://instagram.com/csidbit

Website:
N/A

Membership form:
N/A

Brochure:
tap /csi_brochure to the brochure
'''

ieeeResponse = '''IEEE (Institute of Electrical and Electronics Engineers) is the student chapter of Electronics engineering department.

The IEEE society at Don Bosco Institute of Technology is a professional organisation that creates, 
defines, and evaluates standards in electronics and computer science. 

Insta handle:
https://instagram.com/ieee_dbit

Website:
https://ieee.dbit.in/

Membership form:
N/A

Pdf (optional):
N/A
'''

ieteResponse = '''IETE (Institution of Electronics and Telecommunication Engineers) is the student chapter of Electronics engineering department.

The IETE conducts and sponsors technical meetings, conferences, symposia, 
and exhibitions all over India, publishes technical journals and provides 
continuing education as well as career advancement opportunities to its members.

Insta handle:
https://instagram.com/iete_dbit

Website:
https://iete.dbit.in/

Membership form:
N/A

Pdf (optional):
N/A
'''

madgearsResponse = '''MADGEARS is a student chapter of mechanical engineering department and automative enthusiasts.

Madgears is the motorsports club of DBIT who have participated in various national 
level motorsports events and are also a club dedicated for social media and networking.

Insta handle:
https://instagram.com/madgearmotorsports

Website:
N/A

Membership form:
N/A

Pdf (optional):
N/A

'''

ishraeResponse = '''ISHRAE (Indian Society of Heating, Refrigerating and Air Conditioning Engineers) is a student chapter of mechanical engineering department.
It was formed at Don Bosco Institute of Technology to help students get more knowledge about the HVAC industry. 

The goal of an ISHRAE student chapter is to increase the number of students who are interested, 
concerned, and active in pursuing a profession in the field of heating, ventilation, air conditioning, and refrigeration.

Insta handle:
https://instagram.com/ishraedbit

Website:
http://ishrae.dbit.in/

Membership form:
N/A

Pdf (optional):
N/A

'''

acmResponse = '''ACM (Association for Computing Machinery) is the student chapter of Computer engineering department.

ACM encourages its members' professional development by offering opportunities for lifelong learning, career advancement, and professional networking.

Insta handle:
https://instagram.com/acmdbitt

Website:
N/A

Membership form:
N/A

Pdf (optional)
N/A
'''
technicalEventsResponse = '''
/Student_clubs to know more about active student clubs in DBIT
/Student_chapters for student chapters
/Technical_fest to know about technical events hosted at DBIT
/Cultural_fest for cultural events
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