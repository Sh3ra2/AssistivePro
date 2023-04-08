# -- Importing curret files
from django.shortcuts import render, redirect
from django.http.response import StreamingHttpResponse
from streamapp.attendance import attendance
from streamapp.monitor_students import HeadDetectionView
import os
import time
import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,logout,login
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import cv2
from PIL import Image
import base64
import io
import numpy as np

# -- Importing Created Files
from .pic_form import image_form
from .pic_form import camera_form
from .models import profile_image
from .models import camera_model
from .encode import encode_process
from .att_history_check import time_difference
from .mk_csv import export_firestore_to_csv

# -- Import Firebase libraries
from django.contrib import messages
import firebase_admin
from firebase_admin import credentials, firestore, storage

# -- Setup Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("static/server-assistivepro-firebase-adminsdk-mpb8d-f8b5a22e4e.json")
    app = firebase_admin.initialize_app(cred,{
	    'databaseURL': "https://server-assistivepro-default-rtdb.firebaseio.com/",
	    'storageBucket': "server-assistivepro.appspot.com"
	})
db = firestore.client()

# ------------------- views here ---------------------



# -- Homepage --\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def index(request):
	print("User is ",request.user)
	if request.user.is_anonymous:
		return redirect('/login_user')
	return render(request, 'home.html')



# -- Log Functions --\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def login_user(request):
	if request.method == "POST":
		email = request.POST.get('email')
		password = request.POST.get('password')
		user =  authenticate(username = email,password = password)
		print(user)
		print(email, password )
		if user is not None:
			print("You are authenticated")
			# A backend authenticated the credentials
			login(request, user)
			return redirect('/')
		else:
			# No back
			print("You are not authenticated")
			return render(request,'login.html')
	
	return render(request, 'login.html')

def logout_user(request):
	logout(request)
	return redirect('/login_user')



# -- Get Video Functions --\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def gen(camera):
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def video_feed(request):
	return StreamingHttpResponse(gen(attendance()),
					content_type='multipart/x-mixed-replace; boundary=frame')

HeadDet = HeadDetectionView()
@csrf_exempt
def monitor_students_feed(request):
	if request.method == 'POST':
		# print(request.FILES)  # Add this line to log the request.FILES dictionary
		frame = request.FILES['frame']
		frame_bytes = frame.read()
		frame_array = np.asarray(bytearray(frame_bytes), dtype=np.uint8)
		frame_bgr = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
		# frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

		frame_gray = HeadDet.get_frame(frame_bgr)
		

		frame_gray_pil = Image.fromarray(frame_gray)
		buffer = io.BytesIO()
		frame_gray_pil.save(buffer, format='JPEG')
		frame_gray_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

		return JsonResponse({'grayscale_frame': f'data:image/jpeg;base64,{frame_gray_base64}'})

	return JsonResponse({'error': 'Invalid request'})


# -- Students Functions --\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def new_data(request):
	if request.user.is_anonymous:
		return redirect('/login_user')

	print("Hello from new data")
	if request.method == 'POST':

		form  = image_form(request.POST, request.FILES)

		if form.is_valid():
			form.save()
		
			# -- Getting index of data to upload to fireabse
			d = (len(profile_image.objects.all())-1)

			# -- Getting data
			rollnumber = profile_image.objects.all()[d].roll_num
			# print("Roll Number: ",profile_image.objects.all()[d].roll_num, "Type:",type(profile_image.objects.all()[d].roll_num))
			st_name = profile_image.objects.all()[d].name
			# print("Name: ",profile_image.objects.all()[d].name, "Type:",type(profile_image.objects.all()[d].name))
			department = profile_image.objects.all()[d].department
			# print("department: ",profile_image.objects.all()[d].department, "Type:",type(profile_image.objects.all()[d].department))
			semester = profile_image.objects.all()[d].semester
			# print("Semester: ",profile_image.objects.all()[d].semester, "Type:",type(profile_image.objects.all()[d].semester))
			status = profile_image.objects.all()[d].status
			# print("Status ",profile_image.objects.all()[d].status, "Type:",type(profile_image.objects.all()[d].status))
			filename = profile_image.objects.all()[d].photo
			
			# -- Getting file from storage and renaming it
			filename1 = f'media/{str(filename)}'
			pic_name = str(rollnumber) + '.jpg'
			print("picname is ", pic_name)
			
			# -- Setting up folder and file for firesorage
			db_folder = f'Data/{pic_name}'
			print((" After changing filename1 is", filename1, "and filetype is ", type(filename1)))
		
			# -- Uplaoding file
			bucket = storage.bucket()
			blob = bucket.blob(db_folder)
			blob.upload_from_filename(filename1)


			student = {
				u'id': rollnumber,
				u'Name': st_name,
				u'Department': department,
				u'Semester': semester,
				u'Status': status,
			}
			print("student data got:", student)

			student_ref = db.collection(u'Students').document(str(rollnumber)).set(student)

			messages.success(request,f"Roll Number {rollnumber} Added!")
			return redirect('/view_data')
		else:
			messages.success(request,"Error")
			return redirect('/view_data')

	form = image_form()
	return render(request, 'NewData.html', {'form': form})


def view_data(request):
	if request.user.is_anonymous:

		return redirect('/login_user')
	
	# Connect with data store-------------------------
	users_ref = db.collection(u'Students')
	# get data in stream-------------------------
	my_dict={}
	docs = users_ref.stream()
	for doc in docs:
		# print(f'{doc.id} => {doc.to_dict()}')
		a = doc.id
		b = doc.to_dict()
		my_dict[a] = b
	

	context = profile_image.objects.all()

	print("Context is ", context)

	# for key, values in context.items:
	# 	print("keys are ", key, "values are ", values)
	# print("My dictionary", my_dict)
	
	return render(request, 'ViewData.html',{"Maindata":context})


def edit_student(request, id):
	if request.user.is_anonymous:
		return redirect('/login_user')

	if request.method == 'POST':

		roll = profile_image.objects.get(roll_num = id)
		form  = image_form(request.POST, request.FILES, instance=roll)
		# print(type(form))
		if form.is_valid():
			form.save()

			# -- Getting data to updaet in firebase db
			rollnumber = profile_image.objects.get(roll_num = id).roll_num
			st_name = profile_image.objects.get(roll_num = id).name
			department = profile_image.objects.get(roll_num = id).department
			semester = profile_image.objects.get(roll_num = id).semester
			status = profile_image.objects.get(roll_num = id).status
			filename = profile_image.objects.get(roll_num = id).photo
			
			# -- getting file from storage 
			print("file name is", filename, "and file type is", type(filename))
			filename1 = f'media/{str(filename)}'
			# -- Changing picture name
			pic_name = str(rollnumber) + '.jpg'
			print("picname is ", pic_name)
			
			
			# -- setting up path of firestore storage
			db_folder = f'Data/{pic_name}'
			print((" After changing filename1 is", filename1, "and filetype is ", type(filename1)))

			# -- uplaoding picture to firebase storage
			bucket = storage.bucket()
			blob = bucket.blob(db_folder)
			blob.upload_from_filename(filename1)


			student = {
				u'id': rollnumber,
				u'Name': st_name,
				u'Department': department,
				u'Semester': semester,
				u'Status': status,
			}
			print("student data got:", student)

			student_ref = db.collection(u'Students').document(str(rollnumber)).set(student)
			
			messages.success(request,f"Roll Number {id} Updated!")
			return redirect('/view_data')
	else:
		roll = profile_image.objects.get(roll_num = id)
		form  = image_form(instance=roll)


	return render(request, 'EditStudent.html', {'form': form, 'id':id})


def delete_student(request, id):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	# -- getting id from form
	# print("id is ", id)
	if request.method == "POST":
		# -- delete user from web db
		user_id = profile_image.objects.get(roll_num = id)
		print("user id is ",user_id)
		user_id.delete()


		# -- delete user from firestore db
		db.collection(u'Students').document(str(id)).delete()

		# -- delete user from encode folder
		encode_folder = f'media/encode_images/{id}.jpg'
		try:
    		# Attempt to delete the file
			os.remove(encode_folder)
			print(f"{encode_folder} deleted successfully")
		except OSError as error:
			print(f"Error deleting {encode_folder}: {error}")

		# -- delete user pic from firestore storage
		db_folder = f'Data/{id}.jpg'
		bucket = storage.bucket()
		blob = bucket.blob(db_folder)
		blob.delete()



		messages.success(request,f"Roll Nuber {id} Deleted!")
		return redirect('/view_data')

	# -- after deletion redirect user to view data page
	return redirect('/view_data')



# -- Encode Functions --\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def encode_data(request):
	if request.user.is_anonymous:
		return redirect('/login_user')
	

	# --Start--> Getting images to show on the encode page
	print("Hi from encode view.py")
	context = profile_image.objects.all()
	images={}
	for data in context:
		print(data.roll_num)

		bucket = storage.bucket()
		blob = bucket.blob(f'Data/{data.roll_num}.jpg')
		dest = f'media/encode_images/{data.roll_num}.jpg'
		blob.download_to_filename(dest)
		images[data.roll_num] = dest
		print(images)
	# <--End-- Getting images to show on the encode page
	




	# for key, values in my_dict.items:
	# 	print("key is ", key," value is ", values)
	# <--End-- Getting last attendance from firestore
	# print("dict is ",my_dict)
	i = len(context)

	encode_process()

	return render(request, 'EncodeData.html', {"t_pics":i,"enc_data": images})


def pre_encode(request):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	# --Start--> Getting images to show on the encode page
	context = profile_image.objects.all()
	
	i = len(context)

	return render(request, 'PreEncode.html', {"t_pics": i})


# -- Ip Cam Manage Functions --\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def camera_manage(request):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	# get data in stream-------------------------
	context = camera_model.objects.all()

	print("Context is ", context)

	# for key, values in context.items:
	# 	print("keys are ", key, "values are ", values)
	# print("My dictionary", my_dict)

	# --Start--> Getting images to show on the encode page

	return render(request, 'CameraManage.html', {'Maindata':context})


def add_camera(request):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	if request.method == 'POST':

		form  = camera_form(request.POST)

		# print(type(form))
		if form.is_valid():
			form.save()

			d = (len(camera_model.objects.all())-1)

			# Getting data
			id = camera_model.objects.all()[d].cam_id
		
			messages.success(request,f"ID {id} Added!")
			return redirect('/camera_manage')
		else:
			messages.success(request,"Error")
			return redirect('/camera_manage')
		
	form = camera_form()
	return render(request, 'AddCamera.html', {'form':form})


def delete_camera(request, id):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	
	if request.method == "POST":
		# -- delete user from web db
		user_id = camera_model.objects.get(cam_id = id)
		print("user id is ",user_id)
		user_id.delete()

		messages.success(request,f"ID {id} Deleted!")
		return redirect('/camera_manage')

	# -- after deletion redirect user to view data page
	return redirect('/camera_manage')


def edit_camera(request, id):
	if request.user.is_anonymous:
		return redirect('/login_user')

	print("Hellow from edit camra")
	if request.method == 'POST':
		print("Hellow from edit cam IF above")
		roll = camera_model.objects.get(cam_id = id)
		form  = camera_form(request.POST,  instance=roll)
		# print(type(form))
		if form.is_valid():
			form.save()

			messages.success(request,f"ID {id} Updated!")
			return redirect('/camera_manage')
	else:
		roll = camera_model.objects.get(cam_id = id)
		form  = camera_form(instance= roll)
		print("Hellow from edit cam else")


	return render(request, 'EditCamera.html', {'form': form , 'id':id})


# -- Service Functions --\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def video_data(request):
	if request.user.is_anonymous:
		return redirect('/login_user')
	

	# --Start--> Getting last attendance from firestore ---\
	print("Hello form video data from functions")
	users_ref = db.collection(u'free').document(u'Attendance_track')
	# --- get data in stream
	docs = users_ref.get()
	print("docs has ",docs)

	if docs.exists:
		print(f'Document data: {docs.to_dict()}')
		datetime_dict = docs.to_dict()  # Convert method to dictionary
		last_att = list(datetime_dict.values())[0]  # Get first value from dictionary
		print("Last attendance date is ", last_att)
	else:
		print(u'No such document!')


	# --- getting current date and time
	now = datetime.datetime.now()
	new_now = now.replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
	print("now is ", new_now)
	
	# --- time difference is
	a = time_difference(last_att, new_now)
	print("time diff is ",a, " min")

	# --- updating last attendance in firestore
	if a > 1:
		at = last_att.replace(":","")
		filename = f'media/att_data/{at}.csv'
		export_firestore_to_csv('recent_att', filename)
		city_ref = db.collection(u'free').document(u'Attendance_track')
		city_ref.set({u'Last_attendance': new_now }, merge=True)
		print("new time is ", new_now)
		
	return render(request, 'VideoPage.html')


def pre_session(request):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	# --Start--> Getting images to show on the encode page

	return render(request, 'PreSession.html')


# -- Monitor Students Functions --\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def monitor_students(request):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	# --Start--> Getting images to show on the encode page

	return render(request, 'MonitorStudentsPage.html')


def recent_att(request):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	# --Start--> Getting images to show on the encode page

	files = os.listdir('media/att_data')

	return render(request, 'RecentAtt.html',{'files':files})