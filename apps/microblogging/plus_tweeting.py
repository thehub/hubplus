

def tweet(sender, instance, created, **kwargs):
    #if tweet is None:                                                                                

    #    tweet = Tweet.objects.create(text=text, sender=user)                                                                
    recipients = set() # keep track of who's received it                                                                     
    user = instance.sender

    # add the sender's followers                                                                                             
    user_content_type = ContentType.objects.get_for_model(user)
    followings = Following.objects.filter(followed_content_type=user_content_type, followed_object_id=user.id)
    for follower in (following.follower_content_object for following in followings):
        recipients.add(follower)

    # add sender  
    recipients.add(user)

    # if starts with @user send it to them too even if not following 
    match = reply_re.match(instance.text)
    if match:
        try:
            reply_recipient = User.objects.get(username=match.group(1))
            recipients.add(reply_recipient)
        except User.DoesNotExist:
            pass # oh well
        else:
            if notification:
                notification.send([reply_recipient], "tweet_reply_received", {'tweet': tweet,})

    # if contains #tribe sent it to that tribe too (the tribe itself, not the members)   
    for tribe in tribe_ref_re.findall(instance.text):
        try:
            recipients.add(Tribe.objects.get(slug=tribe))
        except Tribe.DoesNotExist:
            pass # oh well                                      

    # now send to all the recipients                                                          
  
    for recipient in recipients:
        tweet_instance = TweetInstance.objects.create(text=instance.text, sender=user, recipient=recipient, sent=instance.sent)

