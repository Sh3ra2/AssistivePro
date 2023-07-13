# -- Import Libraris
from django.shortcuts import render, redirect
from django.http.response import StreamingHttpResponse
from streamapp.attendance import attendance
from streamapp.monitor_students import HeadDetectionView
import os
import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,logout,login
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, FileResponse, HttpResponseNotFound, HttpResponse
import cv2
from PIL import Image
import base64
import io
import numpy as np

# -- Importing Created Files
from .pic_form import image_form, camera_form, settings_form
from .models import profile_image, camera_model, settings_model
from .encode import encode_process
from .att_history_check import time_difference
from .mk_csv import export_firestore_to_csv

# -- Import Firebase libraries
from django.contrib import messages
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth 
from firebase_integration.firebase_utils import get_firebase_users


# -- Firebase Setup ////////////////////////////////////////////////////////////
if not firebase_admin._apps:
    cred = credentials.Certificate("static/server-assistivepro-firebase-adminsdk-mpb8d-f8b5a22e4e.json")
    app = firebase_admin.initialize_app(cred,{
	    'databaseURL': "https://server-assistivepro-default-rtdb.firebaseio.com/",
	    'storageBucket': "server-assistivepro.appspot.com"
	})
db = firestore.client()
# /////////////////////////////////////////////////////////////////////////////////



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
			messages.success(request,f"Invalid user")
			return redirect('/login_user')
	
	return render(request, 'login.html')

def logout_user(request):
	logout(request)
	return redirect('/login_user')



# -- Get Video Functions --\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

markattendance = attendance()
@csrf_exempt
def video_feed(request):
	if request.method == 'POST':
		# print(request.FILES)  # Line to log the request.FILES dictionary
		
		frame = request.FILES['frame']
		frame_bytes = frame.read()
		frame_array = np.asarray(bytearray(frame_bytes), dtype=np.uint8)
		frame_bgr = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

		frame_gray = markattendance.process_frame(frame_bgr)
		
		frame_gray_pil = Image.fromarray(frame_gray)
		buffer = io.BytesIO()
		frame_gray_pil.save(buffer, format='JPEG')
		frame_gray_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
		

		return JsonResponse({'grayscale_frame': f'data:image/jpeg;base64,{frame_gray_base64}'})

	return JsonResponse({'error': 'Invalid request'})


HeadDet = HeadDetectionView()
@csrf_exempt
def monitor_students_feed(request):
	if request.method == 'POST':
		# print(request.FILES)  # -- Line to log the request.FILES dictionary
		frame = request.FILES['frame']
		frame_bytes = frame.read()
		frame_array = np.asarray(bytearray(frame_bytes), dtype=np.uint8)
		frame_bgr = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
		# frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

		frame_gray = HeadDet.get_frame(frame_bgr, f'{request.user}')
		
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

			# -- Getting data to upload to firebase
			rollnumber = profile_image.objects.all()[d].roll_num
			st_name = profile_image.objects.all()[d].name
			department = profile_image.objects.all()[d].department
			semester = profile_image.objects.all()[d].semester
			status = profile_image.objects.all()[d].status
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

	form = image_form(initial={'user': request.user})
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
	

	context = profile_image.objects.filter(user = request.user)

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
		encode_folder = f'media/encode_images/{request.user}/{id}.jpg'
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



		messages.success(request,f"Roll Number {id} Deleted!")
		return redirect('/view_data')

	# -- after deletion redirect user to view data page
	return redirect('/view_data')



# -- Encode Functions --\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def encode_data(request):
	if request.user.is_anonymous:
		return redirect('/login_user')
	

	# --Start--> Getting images to encode
	print("Hi from encode view.py")
	context = profile_image.objects.filter(user = request.user)
	images={}
	for data in context:
		print("images from blob are ", data.roll_num)

		# -- initialize bucket
		bucket = storage.bucket()
		# -- get data from firebase
		blob = bucket.blob(f'Data/{data.roll_num}.jpg')

		# -- get image from bucket and save
		dest = f'media/encode_images/{request.user}/{data.roll_num}.jpg'
		
		blob.download_to_filename(dest)
		images[data.roll_num] = dest
		print(images)
	# <--End-- Getting images to encode

	i = len(context)
	user = User.objects.get(username=request.user.username)
	dfolder = user.get_username()
	encode_process(dfolder)

	return render(request, 'EncodeData.html', {"t_pics":i,"enc_data": images})


def pre_encode(request):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	# -- just show how many students images will be encoded
	context = profile_image.objects.filter(user = request.user)
	i = len(context)

	return render(request, 'PreEncode.html', {"t_pics": i})


# -- Service Functions --\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def video_data(request):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	markattendance.load_encode_file()
	return render(request, 'VideoPage.html')


def pre_session(request):
	if request.user.is_anonymous:
		return redirect('/login_user')

	return render(request, 'PreSession.html')


# -- Monitor Students Functions --\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def monitor_students(request):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	# --Start--> Getting video of monitor students page

	return render(request, 'MonitorStudentsPage.html')


# -- View Attendance --\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def recent_att(request):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	# --Start--> Getting images to show on the encode page

	files = os.listdir(f'media/att_data/{request.user}')

	return render(request, 'RecentAtt.html',{'files':files})


def download_file(request, file_name):
    file_path = os.path.join('media', 'att_data', f'{request.user}', file_name)
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), content_type='application/csv')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
    else:
        return HttpResponseNotFound('File not found')


def delete_csv(request, file_name):
	file_path = os.path.join('media', "att_data",f'{request.user}', file_name)
    
	if os.path.exists(file_path):
		os.remove(file_path)
		messages.success(request,f"File {file_name} Deleted!")
		return redirect('/recent_att')

	else:
		return redirect('/recent_att')
	

# -- app_settings --\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def app_settings(request):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	print("Hello from edit settings")
	if request.method == 'POST':
		roll = settings_model.objects.get(user = request.user)
		form  = settings_form(request.POST,  instance=roll)
		# print(type(form))
		if form.is_valid():
			form.save()

			messages.success(request,f"Updated!")
			return redirect('/app_settings')
		else:
			messages.success(request, f"Recheck Form!")
	else:
		roll = settings_model.objects.get(user = request.user)
		form  = settings_form(instance= roll)
		print("From else of settings")

	return render(request, 'app_settings.html', {'form': form})


# -- service_section --\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def end_session(request):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	users_ref = db.collection(u'Alerts')
	docs = users_ref.stream()
	for doc in docs:
		print("Deleting Alerts")
		doc.reference.delete()

	messages.success(request,"Alerts Deleted!")
	return redirect('/monitor_students')


def end_session_att(request):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	
	# --Start--> Getting last attendance from firestore ---\
	print("Hello from del att")
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
		print('Document not found!')


	# --- getting current date and time
	now = datetime.datetime.now()
	new_now = now.replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
	print("now is ", new_now)

	# --- updating last attendance in firestore
	user_id = request.user.username # Get the user's ID
	at = new_now.replace(":","")
	foldername = f'media/att_data/{user_id}'
	filename = f'media/att_data/{user_id}/{at}.csv'
	# -- Create the folder if it doesn't exist
	os.makedirs(foldername, exist_ok=True)

	# -- function to make csv of attendance present in firestore
	export_firestore_to_csv('recent_att', filename)

	# -- delete data in store
	users_ref = db.collection(u'recent_att')
	# -- get data in stream-------------------------
	docs = users_ref.stream()
	for doc in docs:
		print("deleting attendance for ", doc)
		doc.reference.delete()

	city_ref = db.collection(u'free').document(u'Attendance_track')
	city_ref.set({u'Last_attendance': new_now }, merge=True)
	
	print("new time is ", new_now)

	messages.success(request,"Attendance Saved!")
	return redirect('/video_data')

# -- User Functions --\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def user_view(request):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	firebase_users = get_firebase_users()
	firebase_users_list = list(firebase_users.iterate_all())

	# print(firebase_users_list)
	return render(request, 'UserView.html' ,{"Maindata":firebase_users_list})


def add_user(request):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	# Get user data from the request or generate it as needed
	if request.method == 'POST':
		email = request.POST.get('email')
		password = request.POST.get('password')
		display_name = request.POST.get('display_name')

		try:
			user = auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )

			messages.success(request, 'User added successfully.')
			return redirect('/user_view')
		except:
			messages.success(request, f"Error")
			return redirect('/add_user')

	return render(request, 'AddUser.html')


def edit_user(request, id):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	if request.method == 'POST':
		email = request.POST.get('email')
		password = request.POST.get('password')
		display_name = request.POST.get('display_name')

		try:
            # Update the user's email using the Firebase Admin SDK
			user = auth.update_user(
				uid = id,
				email = email,
				password = password,
				display_name = display_name
			)
			messages.success(request, 'User updated successfully.')
			return redirect('/user_view')
		except auth.AuthError as e:
			error_message = str(e)
			messages.success(request, f'Error Here:{error_message}')
			return redirect('/edit_user')
	else:
		# uid = request.GET.get('uid')  # Retrieve the user ID from the query string
		user = auth.get_user(id)  # Retrieve the user's information from Firebase
		return render(request, 'EditUser.html', {'user': user})



def delete_user(request, id):
	if request.user.is_anonymous:
		return redirect('/login_user')
	
	try:
		auth.delete_user(id)
		messages.success(request,f"User:{id} Deleted!")
		print("User deleted successfully")
		return redirect('/user_view')
		
	except Exception as e:
		messages.success(request,f"Error, {e}, deleting user: {id}")
		return redirect('/user_view')

