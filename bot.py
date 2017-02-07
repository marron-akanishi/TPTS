import os
import glob
import tweepy as tp
import oauth_bot  # oauthの認証キー

class StreamListener(tp.StreamListener):
    def __init__(self, api):
        """コンストラクタ"""
        self.api = api

    def on_status(self, status):
        if status.text.startswith("@marron_recbot"):
            filename = status.text.lstrip("@marron_recbot ").split(":")
            print(str(filename))
            filelist = glob.glob("./" + filename[0] + "/" + filename[1] + ".*")
            if filelist == []:
                self.api.update_status("@marron_general 指定されたファイルは存在しないみたい",in_reply_to_status_id=status.id)
            else:
                self.api.update_with_media(filelist[0],"@marron_general " + filelist[0],in_reply_to_status_id=status.id)

def main():
    """メイン関数"""
    auth = oauth_bot.get_oauth()
    stream = tp.Stream(auth, StreamListener(tp.API(auth)), secure=True)
    print('Start Streaming!')
    while True:
        try:
            stream.userstream()
        except KeyboardInterrupt:
            exit()
        except:
            print('UserStream Error')
            time.sleep(60)

if __name__ == '__main__':
    main()