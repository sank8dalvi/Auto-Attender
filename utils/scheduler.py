import pickle
import threading
import datetime
from utils.lecture import Lecture
from utils.attender import Attender
from utils.schedule_builder import buildschedule


class Scheduler:
    def __init__(self, launch_interval=20, build_schedule=True, block_chrome_mic_camera=False, mute_chrome_audio=False):
        self.launch_interval = launch_interval
        if build_schedule:
            buildschedule()
        with open('./schedule.pickle', 'rb') as f:
            self.schedule = pickle.load(f)
        self.lastLectureEndTime = self.getLastLectureEndTime()
        self.attend = Attender(
            block_chrome_mic_camera=block_chrome_mic_camera, mute_chrome_audio=mute_chrome_audio)

    # get end time for last lecture ie. end of lectures for that day
    def getLastLectureEndTime(self):
        currentDay = datetime.datetime.now().strftime('%a')
        endOfLectures = datetime.datetime(1970, 1, 1, 0, 0).time()
        for lecture in self.schedule[currentDay]:
            endOfLectures = max(lecture.end_time, endOfLectures)
        return endOfLectures

    # Get current lecture meet code
    def getCurrentMeetCode(self):
        # Get current time params
        currentDateTime = datetime.datetime.now()
        currentDay = currentDateTime.strftime('%a')
        currentTime = currentDateTime.time().replace(microsecond=0, second=0)
        # get current lecture
        for lecture in self.schedule[currentDay]:
            if lecture.start_time <= currentTime < lecture.end_time:
                return lecture.meetcode
        return None

    def attendLecture(self):
        # You can access "attend" variable in this function
        threading.Timer(self.launch_interval, self.attendLecture).start()
        # Gets current lecture meetcode
        currentMeet = self.getCurrentMeetCode()
        # attend.currentLecture is None for no ongoing meet : attend.currentLecture != currentMeet if next meetcode is different from current meet
        if self.attend.currentLecture == None or self.attend.currentLecture != currentMeet:
            # if currentMeet is not None
            if currentMeet:
                self.attend.driver.maximize_window()
                self.attend.join_meet(currentMeet)
            # if college hasnt ended for the day
            elif datetime.datetime.now().time() < self.lastLectureEndTime:
                if self.attend.driver.current_url != 'https://www.google.com/':
                    self.attend.driver.maximize_window()
                    self.attend.driver.get('https://www.google.com/')
                self.attend.currentLecture = None
                self.attend.driver.minimize_window()
            # college lectures ended for the day
            else:
                self.attend.driver.quit()
