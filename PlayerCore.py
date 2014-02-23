import subprocess,Queue,urllib,httplib,json
from threading import Timer

global player
global isPlayerOn
global songTimer
global nowPlayingSong
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
	httpConnection.request('GET','/j/app/radio/people?app_name=radio_desktop_win&version=100&user_id='+user_id+'&token='+token+'&expire='+expire+'&channel=0&type=n&kbps=192')
	response = httpConnection.getresponse()
	print('get songlist success')
	return json.loads(response.read())

def reloadSongQueue():
	global songQueue
	userInfo = login()
	songlist = getSongs(userInfo['user_id'],userInfo['token'],userInfo['expire'])['song']
	songQueue = Queue.Queue(0)
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

	if isPlayerOn == False:
		if songQueue.qsize() == 0:
			reloadSongQueue()
		song = songQueue.get()
		nowPlayingSong = song
		player = subprocess.Popen(['mplayer',song['url']])
		songTimer = Timer(song['length'],endSong)
		songTimer.start()
		isPlayerOn = True
		print "Player On:",song['title']
	else:
		songTimer.cancel()
		player.kill()
		isPlayerOn = False
		print "player Stop"

def ring():
	global isPlayerOn
	if isPlayerOn == False:
		play()

def playNext():
	global isPlayerOn
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

