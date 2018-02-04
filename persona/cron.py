import json
import logging
import twitter
import requests

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django_cron import CronJobBase, Schedule


from persona.models import UserStatus, Benefactors

from bs4 import BeautifulSoup
from datetime import datetime


class UserDead(CronJobBase):
    RUN_EVERY_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'persona.user_dead'

    def do(self):
        date_now = datetime.now()
        obj,created = UserStatus.objects.get_or_create(user = User.objects.get(id=1))

        """-------------------------------- Facebook -----------------------------------"""
        
        facebook_req = requests.get("https://graph.facebook.com/v2.11/me/posts?access_token="+settings.FACEBOOK_TOKEN+\
                   "&debug=all&format=json&method=get&pretty=0&suppress_http_code=1")
        facebook_data = json.loads(facebook_req.text).get('data',None)

        facebook_request = requests.get("https://graph.facebook.com/v2.11/me/feed?fields=comments&&access_token="+settings.FACEBOOK_TOKEN+\
                   "&debug=all&format=json&method=get&pretty=0&suppress_http_code=1")
        facebook_comment = json.loads(facebook_request.text).get('data', None)

        try:
            facebook_last_activity = facebook_data[0]['created_time']

            facebook_last_comment = facebook_comment[0].get('comments', None)['data'][0]['created_time']
            facebook_days_diff = (date_now - datetime.strptime(str(facebook_last_activity), "%Y-%m-%dT%H:%M:%S+0000")).days

            facebook_comment_diff = (date_now - datetime.strptime(str(facebook_last_comment), "%Y-%m-%dT%H:%M:%S+0000")).days
            if facebook_days_diff >= facebook_comment_diff:
                facebook_last_act = facebook_comment_diff
                obj.facebook_status = datetime.strptime(str(facebook_last_comment), "%Y-%m-%dT%H:%M:%S+0000")
            else:
                facebook_last_act = facebook_days_diff
                obj.facebook_status = datetime.strptime(str(facebook_last_activity), "%Y-%m-%dT%H:%M:%S+0000")
            print ("Facebook last post: %s" %(facebook_last_activity))
            facebook_last = facebook_data[0]['message']
        except:
            print("No facebook posts found")
            facebook_last_activity = None
            facebook_days_diff = 0
            facebook_last = ""
            
        """-------------------------------- Reddit -------------------------------------"""

        reddit_session=requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36'
            }
        page = reddit_session.get('https://www.reddit.com/user/'+settings.REDDIT_USER, headers = headers)
        soup = BeautifulSoup(page.text, 'html.parser')
        comment_list = soup.find_all('time')

        try:
            print("Reddit last Post's Date & Time : %s" %(str(comment_list[0]['datetime'])))
            reddit_days_diff = (date_now - datetime.strptime(str(comment_list[0]['datetime']), "%Y-%m-%dT%H:%M:%S+00:00")).days
            obj.reddit_status = datetime.strptime(str(comment_list[0]['datetime']), "%Y-%m-%dT%H:%M:%S+00:00")
            reddit_last = soup.find_all('form',{'class':'usertext'})[0].text
        except:
            print("No reddit posts found")
            reddit_days_diff = 0
            reddit_last = ""

        """-------------------------------- Twitter ------------------------------------"""
        api = twitter.Api(consumer_key=settings.TWITTER_CONSUMER_KEY,
                          consumer_secret=settings.TWITTER_CONSUMER_SECRET,
                          access_token_key=settings.TWITTER_ACCESS_TOKEN,
                          access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET)
        try:
            latest_created = api.GetUserTimeline(screen_name='sarahray_cw')[0].created_at
            twitter_last = api.GetUserTimeline(screen_name='sarahray_cw')[0].text 
        except IndexError:
            latest_created = None
            twitter_last = ""

        if latest_created:
            print ("Twitter last post: %s" %(latest_created))
            converted_date = datetime.strptime(latest_created, "%a %b %d %H:%M:%S +0000 %Y")
            twitter_days_diff = (date_now - converted_date).days
            obj.twitter_status = converted_date
        else:
            print("No twitter posts found")
            twitter_days_diff = 0
        last_activity = settings.ACTIVITY_DAYS
        if reddit_days_diff>= last_activity and facebook_last_act>=last_activity and twitter_days_diff>=last_activity:
            
            if reddit_days_diff> facebook_last_act and reddit_days_diff>twitter_days_diff:
                last_post = reddit_last
            elif facebook_days_diff>reddit_days_diff and facebook_days_diff>twitter_days_diff:
                last_post = facebook_last
            else:
                last_post = twitter_last
            dead = True
            obj.last_activity = last_post
            obj.dead_status = True
        else:
            dead = False
            obj.dead_status = False
        obj.save()
        try:
            users = Benefactors.objects.get(user__id=1).benfactors.all()
        except:
            users = []
        if users and dead:
            send_mail(
                        'Persona User Status',
                        'Persona user has been died',
                        settings.DEFAULT_FROM_EMAIL,
                        users,
                        fail_silently=False,
                    )

        print 'Status', dead