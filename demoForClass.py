# - *- coding: utf- 8 - *-
import time

from pepper.robot import Pepper
import urllib2
import urllib
import base64
import json
from PIL import Image
import random

'''we need to upload photo to web as we (me) are not able to open it from local folder'''
def uploadPhotoToWeb(photo):
    f = open(photo, "rb")  # open our image file as read only in binary mode
    image_data = f.read()  # read in our image file
    b64_image = base64.standard_b64encode(image_data)
    client_id = "af482612ae6d1c1"  # this the id which we've got after registrating the app on imgur
    headers = {'Authorization': 'Client-ID ' + client_id}
    data = {'image': b64_image, 'title': 'test'}
    request = urllib2.Request(url="https://api.imgur.com/3/upload.json", data=urllib.urlencode(data),
                              headers=headers)
    response = urllib2.urlopen(request).read()
    parse = json.loads(response)
    return parse['data']['link'] #returns a url of the photo

'''reurns a random name for the picture in order not to replace the old photo'''
def getRandName():
    randNum = random.randint(0, 1000)
    return "demoPictures/photo" + str(randNum) + ".png"


class PepperDemo:
    def __init__(self, ip_address, port=9559):
        self.robot = None
        self.robot = Pepper(ip_address, port)
        self.robot.set_czech_language()
        self.photoName = None
        self.greetings = ["dobrý den", "ahoj", "zdravím", "zdravíčko", "dobrý den ve spolek"]
        self.asks = ["Mohu vás vyfotit a zveřejnit to na internetu?","Chcete se vyfotit?", "Chcete abych vas vyfotil?"]

    '''recognise answer with google speech reco'''
    def wantToTakePic(self):
        answers = {"no": ["ne", "ani ne", "vůbec", "moc ne", "nechci", "nevím", "dnes ne", "později", "přiště"],
                   "yes": ["jo", "rozhodně", "ano", "jasně", "jo jo", "to teda", "no jasně", "no",
                          "strašně", "chci", "celkem jo", "vcelku jo", "celkem ano", "ale jo", "asi", "třeba",
                          "nožná"]}
        recorded = self.robot.recordSound()
        answer = self.getAnswer(answers, recorded)
        if answer == "no":
            return False
        elif answer == "yes":
            return True
        else:
            return None

    '''looks for a recorded answer in a dictionary'''
    def getAnswer(self, dic, recorded):
        answer = None
        for x in dic.keys():
            if recorded in dic[x]:
                answer = x
                break
        return answer

    def welcomeAndAsk(self):
        self.robot.say(random.choice(self.greetings))
        self.robot.greet()
        self.robot.say(random.choice(self.asks))

    def takePicture(self):
        self.robot.subscribe_camera("camera_top", 2, 30)
        img = self.robot.get_camera_frame(show=False)
        self.robot.unsubscribe_camera()
        self.robot.play_sound("/home/nao/camera1.ogg")
        im = Image.fromarray(img)
        self.photoName = getRandName()
        im.save(self.photoName)

    def showPicture(self):
        link = uploadPhotoToWeb(self.photoName)
        self.robot.show_image(link)
        time.sleep(5)
        self.robot.reset_tablet()

    def recogniseAnswerAndDecide(self):
        isTakePic = self.wantToTakePic()
        if isTakePic:
            self.robot.say("Super, připravte se. 3, 2, 1 .")
            self.takePicture()
            self.showPicture()
        elif isTakePic is None:
            self.robot.say("Nepochopil jsem nebo mluvili jste příliš potichu, zkuste to řict jinak")
            self.recogniseAnswerAndDecide()
        else:
            self.robot.say("Tak možná někdy přiště")

    '''there is a modifiable grammar error sometimes occurred. 
    In order to deal with it you should change language to english and back'''
    def dealWithRecoErrors(self):
        self.robot.set_english_language()
        self.robot.set_czech_language()

    def run(self):
        self.dealWithRecoErrors()
        self.welcomeAndAsk()
        self.recogniseAnswerAndDecide()

if __name__ == "__main__":
    pepperDemo = PepperDemo("10.37.1.232")
    pepperDemo.run()

