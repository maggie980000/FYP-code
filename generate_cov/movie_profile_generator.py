import re
from LAC import LAC
lac=LAC()


TYPES=['真人秀','纪录片','短片','脱口秀','剧集','电影']

class ProfileGenerator:
    def __init__(self, intro_text,title_text):
        self.intro_text=intro_text
        self.title_text=title_text
       

    def lac_ner_tagging(ele_text):
        seg_result = lac.run(ele_text)
        pos_lst=seg_result[1]
        text_lst=seg_result[0]
        return {'text':text_lst,'pos':pos_lst}
    

    def get_movie_name(movie_title_text):
        title=movie_title_text
        if (' / ') in movie_title_text:
            title=title.split(' / ')[0]
        if ' ' in title:
            title=title.split(' ')[0]
        title=title.replace('\n','')
        if '[' in title:
            title=title.split('[')[0]
        if '(' in title:
            title=title.split('(')[0]
        return title
    

    def lac_tagging_clf(tagging_dic, movie_title):
    # if len(re.findall(r'[\u4e00-\u9fff]+',''.join(tagging_dic['text'])))==0:
        # return None
        movie_name=ProfileGenerator.get_movie_name(movie_title)
        if movie_name in ''.join(tagging_dic['text']):
            return 'movie_name'
        
        if 'PER' in  tagging_dic['pos']:
            return 'person'
        
        if len(re.findall(r'[\u4e00-\u9fff]+',''.join(tagging_dic['text'])))==0:
            return None
        
        if  ('语' in ' '.join(tagging_dic['text']) and all(x in ['n','nz','an','vn'] for x in tagging_dic['pos'])) or (('方言' in tagging_dic['text'] or '话' in tagging_dic['text']) and 'LOC' in tagging_dic['pos']):
            return  'language'
        
        if '中国' in tagging_dic['text']:
            return 'production_country'
        
        if 'LOC' in  tagging_dic['pos'] and len(tagging_dic['pos'])==1:
            return 'production_country'
    
        if len(tagging_dic['pos'])==1 and tagging_dic['pos'][0] in ['n','nz','an','vn']:
            return 'genre'
        
        return 'person'
        
    
    
    def get_tagging(ele_text,movie_title):
    # if movie_title in ele_text:
        # return 'movie_title'
        
        if ('（' in ele_text or '(' in ele_text) and '-' in ele_text:
            return 'release_date_loc'
        
        if '分钟' in ele_text and  any(char.isdigit() for char in ele_text):
            return 'duration'
        
        if any(i.isdigit() for i in ele_text) and '-' in ele_text:
            return 'release_date_loc'
        
        tagging_dic=ProfileGenerator.lac_ner_tagging(ele_text)

        return ProfileGenerator.lac_tagging_clf(tagging_dic,movie_title)


    def intro_text_tagging(intro_text, movie_title):
        ele_text_lst=intro_text.split(' / ')
        ele_text2tagging={}
        idx2tagging={}
        for idx,ele_text in enumerate(ele_text_lst):
            tag=ProfileGenerator.get_tagging(ele_text,movie_title)
            ele_text2tagging[ele_text]=tag
            idx2tagging[idx]=tag
        
        actorstart_idx=None
        actorend_idx=None
        directorstart_idx=None
        directorend_idx=None
    
        for idx in range(len(ele_text_lst)):
            if idx2tagging[idx]=='person':

                if idx>0 and idx2tagging[idx-1]=='release_date_loc':
                    
                    actorstart_idx=idx

                if (idx+1<=len(ele_text_lst)-1) and idx2tagging[idx+1]=='production_country':
                    actorend_idx=idx


                if idx>0 and idx2tagging[idx-1]=='production_country':
                    directorstart_idx=idx
                    
                elif idx>1 and idx2tagging[idx-2]=='production_country':
                    s=ele_text_lst[idx-1]
                    if len(re.findall(r'[\u4e00-\u9fff]+',s))==0:   #special cases
                        directorstart_idx=idx


                if ((idx+1<=len(ele_text_lst)-1) and idx2tagging[idx+1]=='duration'):
                    directorend_idx=idx

                if ((idx+2<=len(ele_text_lst)-1) and idx2tagging[idx+2]=='duration'):
                    #duration_str=ele_text_lst[idx+2]
                    #mins=int(re.findall(r'\d+',duration_str)[0]) #tv series
                    #if mins<70:
                    directorend_idx=idx
        
        if actorstart_idx and actorend_idx:
            actorend_idx=min(actorstart_idx+4, actorend_idx)
        
        for i in range(len(ele_text_lst)):
            ele_text=ele_text_lst[i]
            if ele_text=='日本':
                idx2tagging[i]='production_country'
            elif actorstart_idx and actorend_idx and actorstart_idx<=i and i<=actorend_idx:
                idx2tagging[i]='actor'
            elif directorstart_idx and directorend_idx and directorstart_idx<=i and i<=directorend_idx:
                idx2tagging[i]='director'
        
        return idx2tagging

   
    def get_release_locations(ele_text):
        lst=re.findall(r'[（|(](.*?)[)|）]', ele_text)
        if not lst:
            return ''
        ele=lst[0]
        if '电影节' in ele or 'Film Festival' in ele or 'Festival' in ele or '影展' in ele:
            if '国际' in ele:
                ele=''.join(ele.split('国际'))
            return ele
        else:
            return ''
        
 
    def get_release_date(ele_text):
        lst=re.findall(r'^[^\(|（]+', ele_text)
        if not lst:
            return ''
        return lst[0]


    def run(self):
        ele_text_lst=self.intro_text.split(' / ')
        info_dict={}
        attr_names=['genre','actor','director','production_country','language','release_date','release_film_festival','type']

        for attr in attr_names:
            if attr not in info_dict:
                info_dict[attr]=[]

        idx2tagging=ProfileGenerator.intro_text_tagging(self.intro_text,self.title_text)

        for idx, tagging in idx2tagging.items():
            ele_text=ele_text_lst[idx]

            if tagging in ['genre','director','actor','production_country','language']:
                if tagging in ['director','actor']:  #新海诚 Makoto Shinkai /新海诚
                    if ' ' in ele_text and len(re.findall(r'[\u4e00-\u9fff]+',ele_text))>0:
                        ele_text=ele_text.split(' ')[0]

                info_dict[tagging].append(ele_text)

            elif tagging=='release_date_loc':
                release_date=ProfileGenerator.get_release_date(ele_text)
                if release_date!='':
                    info_dict['release_date'].append(release_date)

                film_festival=ProfileGenerator.get_release_locations(ele_text)
                if film_festival!='':
                    info_dict['release_film_festival'].append(film_festival)

            elif tagging=='duration':
                mins=int(re.findall(r'\d+',ele_text)[0])
                if mins<70:
                    info_dict['genre'].append('剧集')
                else:
                    info_dict['genre'].append('电影')
        
        if ('真人秀' in info_dict['genre'] or '纪录片' in info_dict['genre'] or '短片' in info_dict['genre'] or '脱口秀' in info_dict['genre']):
            if '剧集' in info_dict['genre']:
                info_dict['genre'].remove('剧集')

            if '电影' in info_dict['genre']:
                info_dict['genre'].remove('电影')

        if not ('真人秀' in info_dict['genre'] or '纪录片' in info_dict['genre'] or '短片' in info_dict['genre'] or '脱口秀' in info_dict['genre'] or '剧集' in info_dict['genre']):
            info_dict['genre'].append('电影')

        for attr in attr_names[:-1]:
            info_dict[attr]=list(set(info_dict[attr]))

        genre2types=[]
        for g_str in info_dict['genre']:
            if g_str in TYPES:
                genre2types.append(g_str)

        for g_str in genre2types:
            info_dict['genre'].remove(g_str)
            info_dict['type'].append(g_str)
                
        return info_dict