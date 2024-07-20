from config import supabase
from account import Platform_Account

def updatePostsTable(self : Platform_Account) -> list:

    # get existing posts from posts table
    oldList = self.getPosts()

    # get new posts from IG
    newList = self.getIGMediaObjects()
    NEWwithMedia = {}
    # compare with mediaList
    toUpdateInsert, toDelete = self.processLists(oldList, newList)

    if len(toUpdateInsert) == 0 and len(toDelete) == 0:
        print("No new posts to update or delete")
        return newList
    
    else:
        # delete old posts
        updateSuccess = 0
        deleteSuccess = 0

        for postID in toDelete:
            try:
                response = supabase.table('posts').delete().eq('id', postID).execute()
            except Exception as e:
                print("Error deleting post: ", postID)
                print(e)
                continue
            deleteSuccess += 1
            
        # insert new posts
        for postID in toUpdateInsert:
            post,mediaType = self.getMediaMetadata(postID)
            try:
                response = supabase.table('posts').upsert([{
                    'id': postID,
                    'platform_account': self.platformAccID,
                    'created_at' : post['timestamp'],
                    'post_type': post['media_type'],
                    'caption': post['caption'],
                    'media_url': post['media_url'],
                    'permalink':post['permalink'],
                    'video_thumbnail': post['thumbnail_url'] if post['media_type'] == 'VIDEO' else None

                }]).execute()
                NEWwithMedia[postID] = mediaType
            except Exception as e:
                print("Error inserting post: ", postID)
                print(e)
                continue
            
            updateSuccess += 1

        print ("USER: ", self.platformAccID)
        print ("MediaList: ", NEWwithMedia)
        print ("Update Success: ", updateSuccess, "/", len(toUpdateInsert))
        print ("Delete Success: ", deleteSuccess, "/", len(toDelete))
        print (" ")
        
        return NEWwithMedia

def updatePostMetrics(post,a1: Platform_Account, mediaType, followers):

    print("post: ", post , " mediaType: ", mediaType)
    insights = a1.getMediaInsights(post, mediaType)
    if insights['comments'] != 0:
        sentimentScore = a1.getMediaSentiment(post)
    else:
        sentimentScore = 0
    try:
        response = supabase.table('post_metrics').insert([{
            'post_id': post,
            'post_likes': insights['likes'],
            'post_shares': insights['shares'],
            'post_saved': insights['saved'],
            'post_comments': insights['comments'],
            'post_impressions': insights['impressions'],
            'post_reach': insights['reach'],
            'post_profile_visits': insights['profile_visits'] if mediaType != 'VIDEO' else 0,
            'post_sentiment': sentimentScore,
            'post_video_views': insights['video_views'],
            'post_amplification_rate' : insights['shares']/followers
        }]).execute()
        print("SUCCESS for : ", post)
        print( " ")
    except Exception as e:
        print("FAILED for : ", post)
        print(e)
        return False
    
    fullMetrics = {"id": post , "likes":insights["likes"], "shares": insights['shares'], "saved": insights["saved"], "comments": insights["comments"], "impressions": insights["impressions"], "reach" : insights["reach"], "profile_visits" : insights['profile_visits'] if mediaType != 'VIDEO' else 0, "sentiment" : sentimentScore, "video_views" : insights['video_views'], "amplification_rate":insights['shares']/followers }

    return True, fullMetrics


def updateAccountMetrics(metrics, postCount, a1: Platform_Account):
    metrics["sentiment"] = metrics["sentiment"]/postCount
    try:
        response = supabase.table('platform_metrics').insert([{
            'platform_account' : a1.platformAccID,
            'platform_profile_visits' : metrics["profile_visits"],
            'platform_followers' : metrics["followers"],
            'platform_likes' : metrics["likes"],
            'platform_comments' : metrics['comments'],
            'platform_saves' : metrics['saved'],
            'platform_shares' : metrics['shares'],
            'platform_impressions' : metrics['impressions'],
            'platform_sentiment' : metrics['sentiment']
            # reach cannot be derieved 

        }]).execute()
        print("Account metrics Success for :", a1.platformAccID)
    except Exception as e:
        print( "Account metrics Failed for :", a1.platformAccID)
        print (e)
        return False
    
    return True


def main():
    # updates posts table for all accounts
    allAccounts = supabase.table('platform_account').select("platform_account_id,access_token,account_username").execute()
    accountUpdateSuccess = 0
    for account in allAccounts.data:
        if account["access_token"] == None:
            continue
        a1 = Platform_Account(account["platform_account_id"], account["access_token"], account["account_username"])
        mediaList = updatePostsTable(a1)
        followers = a1.getAccountFollwers()
        postUpdateSuccess = 0
        accountMetrics = {"video_views" : 0, "likes": 0 , "shares": 0 , "saved": 0, "comments": 0 , "impressions": 0, "profile_visits" : 0, "sentiment" : 0 , "sentiment" : 0, "followers" : followers}
        
        for post in mediaList:
            type = mediaList[post]
            insightsETLSuccess, fullPostMetrics = updatePostMetrics(post,a1,type,followers)
            if insightsETLSuccess:
                accountMetrics['likes'] += fullPostMetrics['likes']
                accountMetrics['shares'] += fullPostMetrics['shares']
                accountMetrics['saved'] += fullPostMetrics['saved']
                accountMetrics['comments'] += fullPostMetrics['comments']
                accountMetrics['impressions'] += fullPostMetrics['impressions']
                accountMetrics['profile_visits'] += fullPostMetrics['profile_visits']
                accountMetrics['sentiment'] += fullPostMetrics['sentiment']
                accountMetrics['video_views'] += fullPostMetrics['video_views']

                postUpdateSuccess += 1
        

        print("update Success: ", postUpdateSuccess, "/", len(mediaList))
        
        accountMetricsUpdate = updateAccountMetrics(accountMetrics, len(mediaList), a1)
        print("Full Account Metrics ", accountMetrics)
        if accountMetricsUpdate:
            accountUpdateSuccess += 1
    print("account update Success: ", accountUpdateSuccess, "/", len(allAccounts.data))
    

if __name__ == "__main__":
    main()