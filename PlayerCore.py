import subprocess,Queue,urllib,httplib,json,os,signal
from threading import Timer

global player
global isPlayerOn
global songTimer
global nowPlayingSong
global userInfo
isLike = False
isPlayerOn = False
songQueue = Queue.Queue(0)

def login():
	params = urllib.urlencode({'email':'colazeus@hotmail.com','password':'19880712','app_name':'radio_desktop_win','version':'100'})
	headers = headers = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}
	httpConnection = httplib.HTTPConnection("www.douban.com")
	httpConnection.request("POST","/j/app/login",params,headers)
	response = httpConnection.getresponse()
	print('login success')
	return json.loads(response.read())

def getSongs(user_id,token,expire):
	httpConnection = httplib.HTTPConnection('www.douban.com')
	httpConnection.request('GET','/j/app/radio/people?app_name=radio_desktop_win&version=100&user_id='+user_id+'&token='+token+'&expire='+expire+'&channel=0&type=n')
	response = httpConnection.getresponse()
	print('get songlist success')
	return json.loads(response.read())

def reloadSongQueue():
	global songQueue
	global userInfo
	userInfo = login()
	songlist = getSongs(userInfo['user_id'],userInfo['token'],userInfo['expire'])['song']
	songQueue = Queue.Queue(0)
	if len(songlist) > 1:
		songQueue.put(songlist[0])
		songQueue.put(songlist[1])
		songQueue.put(songlist[2])
		songQueue.put(songlist[3])
		songQueue.put(songlist[4])

def endSong():
	playNext()

def play():
	global isPlayerOn
	global player
	global songTimer
	global songQueue
	global nowPlayingSong
	global isLike

	if isPlayerOn == False:
		if songQueue.qsize() == 0:
			reloadSongQueue()
		song = songQueue.get()
		nowPlayingSong = song
		player = subprocess.Popen(['mplayer',song['url']],close_fds=True, preexec_fn = os.setsid)
		songTimer = Timer(song['length'],endSong)
		songTimer.start()
		isPlayerOn = True
		if song['like'] == 1:
			isLike = True
		else:
			isLike = False
		print "Player On:",song['title']
	else:
		songTimer.cancel()
		os.killpg(player.pid,signal.SIGUSR1)
		player.kill()
		isPlayerOn = False
		print "player Stop"

def ring():
	global isPlayerOn
	
	if isPlayerOn == False:
		reloadSongQueue()
		play()

def playNext():
	global isPlayerOn
	global player
	if isPlayerOn == True:
		play()
		play()

def getInfo():
	global nowPlayingSong
	if isPlayerOn == False:
		error = {'error':0}
		return error
	else:
		return nowPlayingSong

def likeTheSong():
	global nowPlayingSong
	global userInfo
	global isLike
	if isPlayerOn == True:
		httpConnection = httplib.HTTPConnection('www.douban.com')
		if isLike == False:
			httpConnection.request('GET','/j/app/radio/people?app_name=radio_desktop_win&version=100&user_id='+userInfo['user_id']+'&token='+userInfo['token']+'&expire='+userInfo['expire']+'&channel=0&type=r&sid='+nowPlayingSong['sid'])
			httpConnection.getresponse()
			print "Like the song:",nowPlayingSong['title']
			isLike = True
			return True
		else:
			httpConnection.request('GET','/j/app/radio/people?app_name=radio_desktop_win&version=100&user_id='+userInfo['user_id']+'&token='+userInfo['token']+'&expire='+userInfo['expire']+'&channel=0&type=u&sid='+nowPlayingSong['sid'])
			httpConnection.getresponse()
			print "Unlike the song:",nowPlayingSong['title']
			isLike = False
			return False

def delTheSong():
	global nowPlayingSong
	global userInfo
	if isPlayerOn == True:
		httpConnection = httplib.HTTPConnection('www.douban.com')
		httpConnection.request('GET','/j/app/radio/people?app_name=radio_desktop_win&version=100&user_id='+userInfo['user_id']+'&token='+userInfo['token']+'&expire='+userInfo['expire']+'&channel=0&type=b&sid='+nowPlayingSong['sid'])
		httpConnection.getresponse()
		print "Del the song:",nowPlayingSong['title']
		playNext()