from django.shortcuts import render,HttpResponse,redirect
from django.db.models import Q
from .models import Room,Topic,Message
from .forms import RoomForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

# rooms = [
#     {'id':1,
#      'name':'Let\'s Learn Python'
#      },
#     {'id':2,
#      'name':'Let\'s Learn Django'
#      },
#     {'id':3,
#      'name':'Let\'s Learn React'
#      }
# ]
def loginPage(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method=="POST":
        username=request.POST.get('username').lower()
        password=request.POST.get('password')

        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request,'User doesn\'t exist')

        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
             messages.error(request,'Username OR password doesn\'t match')

    page='login'
    context={'page':page}
    return render(request,'config/login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    page='register'
    form= UserCreationForm()

    if request.method=="POST":
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"An error occurred during registration")

    return render(request,'config/login_register.html',{'page':page,'form':form})

def home(request):
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    rooms=Room.objects.filter(
        Q(topic__name__icontains=q)|
        Q(name__icontains=q)|
        Q(description__icontains=q)
        ) 
    
    topic=Topic.objects.all()
    room_count=rooms.count()
    context={'rooms':rooms,'topics':topic,'room_count':room_count}
    return render(request,'config/home.html',context) 

def room(request,pk):
    room=Room.objects.get(id=pk)
    # for i in rooms:
    #     if i['id']== int(pk):
    #         room=i 
    room_messages=room.message_set.all().order_by('-created')
    participants=room.participants.all()

    if request.method=="POST":
        message= Message.object.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    
    context={'room': room,'room_messages':room_messages,'participants':participants}
    return render(request,'config/room.html',context)

@login_required(login_url="login")
def CreateRoom(request):
    form=RoomForm()
    if request.method =='POST':
        form=RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context={'form': form}
    return render(request,'config/room_form.html',context)

@login_required(login_url="login")
def UpdateRoom(request,pk):
    room=Room.objects.get(id=pk)
    form=RoomForm(instance=room)  #use instance to prefill it with room values

    if request.user!= room.host:
        return HttpResponse('You are not allowed here!!')
    
    if request.method =='POST':
        form=RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context={'form':form}
    return render(request,'config/room_form.html',context)

@login_required(login_url="login")
def DeleteRoom(request,pk):
    room=Room.objects.get(id=pk)

    if request.user!= room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request,'config/delete.html',{'obj':room})

@login_required(login_url="login")
def DeleteMessage(request,pk):
    message=Message.objects.get(id=pk)

    if request.user!= message.user:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request,'config/delete.html',{'obj':message})

