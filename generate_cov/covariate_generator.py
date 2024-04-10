
from movie_profile_generator import ProfileGenerator
from LAC import LAC
import zhconv
import json

lac = LAC()

class CovariateGenerator:
    def __init__(self, original_data):
        self.orignal_data=original_data
        self.track_unseen_director=False
        self.cov_name2LST={}
        for cov_name_str in ['ACTOR','DIRECTOR','TYPE','GENRE','COUNTRY','LANGUAGE','FESTIVAL','DATE',"VOCAB"]:
            self.cov_name2LST[cov_name_str] = []
            file_name="covariate_name/"+cov_name_str+"_LST.txt"
            with open(file_name, "r") as f:
                for line in f:
                    self.cov_name2LST[cov_name_str].append((line.strip()))
        self.unseen_director2count=None
        self.rating2weight={5:1, 4:0.8, 3:0.6, 2:0.4, 1:0.2, 'NA':0}

    def load_unseen_director2count(self, prev_director2count):
        self.track_unseen_director=True
        self.unseen_director2count=prev_director2count
    

    def convert_date2cat(self,date):
        yr_str=date[:4]

        n=len(self.cov_name2LST['DATE'])
        yrs_lst=[]
        for i in range(n):
            if i==0:
                yrs_lst.append(int(self.cov_name2LST['DATE'][i][2:]))
            elif i==n-1:
                continue
            else:
                yrs_lst.append(int(self.cov_name2LST['DATE'][i][-4:]))

        if yr_str.isnumeric():
            yr=int(yr_str)
            for i in range(n-1):
                if yr<yrs_lst[i]:
                    return self.cov_name2LST['DATE'][i]
            return self.cov_name2LST['DATE'][-1]
        else:
            return 'NA'

    def convert2item_profile(self, movie_dic):
        item_profile={}
        all_attrs=[]
        for cov_name, cov_lst in self.cov_name2LST.items():
            all_attrs+=cov_lst
        for attr in all_attrs:
            item_profile[attr]=0

        genres=movie_dic['genre']
        types=movie_dic['type']
        countries=movie_dic['production_country']
        languages=movie_dic['language']
        festivals=movie_dic['release_film_festival']
        directors=movie_dic['director']
        actors=movie_dic['actor']
        
        if len(movie_dic['release_date'])>0:
            date=movie_dic['release_date'][0]
            date_cat=self.convert_date2cat(date)
            if date_cat!='NA':
                item_profile[date_cat]=1

        for g in genres:
            if 'G_'+g in self.cov_name2LST['GENRE']:
                item_profile['G_'+g]=1
                
        for t in types:
            if 'T_'+t in self.cov_name2LST['TYPE']:
                item_profile['T_'+t]=1

        for c in countries:
            if 'C_'+c in self.cov_name2LST['COUNTRY']:
                item_profile['C_'+c]=1
            else:
                item_profile['C_'+'其他']=1

        for l in languages:
            if 'L_'+l in self.cov_name2LST['LANGUAGE']:
                item_profile['L_'+l]=1
            else:
                item_profile['L_'+'其他']=1

        for f in festivals:
            if 'F_'+f in self.cov_name2LST['FESTIVAL']:
                item_profile['F_'+f]=1
            else:
                item_profile['F_'+'其他']=1
                
        for d in directors:
            if 'D_'+d  in self.cov_name2LST['DIRECTOR']:
                item_profile['D_'+d]=1
        
        for a in actors:
            if 'A_'+a in self.cov_name2LST['ACTOR']:
                item_profile['A_'+a]=1
            
        return  item_profile
    
    def get_movie_id2movie_info_dic(data):
        '''
        perform NER task on raw movie_intro text
        '''
        movie_id2movie_info_dic={}
        for user_id, rating_lst in data.items():
            for rating in rating_lst:
                movie_id=rating['movie_id']
                if movie_id in movie_id2movie_info_dic:
                    continue
                intro_text=rating['intro']
                title_text=rating['title']
                movie_dic=ProfileGenerator(intro_text,title_text).run() 
                movie_id2movie_info_dic[movie_id]=movie_dic
        return  movie_id2movie_info_dic
    
    def get_movie_ids_lst(rating_lst):
        res=[]
        for ele in rating_lst:
            res.append(ele['movie_id'])
        return res      
    
    def get_user_id2movie_lst(data):
        user_id2movie_lst={}
        for user_id, rating_lst in (data).items():
            user_id2movie_lst[user_id]=CovariateGenerator.get_movie_ids_lst(rating_lst)
        return user_id2movie_lst

    def get_movie_id2rating(rating_lst):
        movie_id2rating={}
        for ele in rating_lst:
            movie_id2rating[ele['movie_id']]=ele['rating']
        return movie_id2rating

    def get_user_id2item_rating(data):
        user_id2item_rating={}
        for user_id, rating_lst in (data).items():
            if user_id not in user_id2item_rating:
                user_id2item_rating[user_id]=CovariateGenerator.get_movie_id2rating(rating_lst)
        return user_id2item_rating
    

    
    def get_user_id2user_profile(self):
        rating2weight={5:1, 4:0.8, 3:0.6, 2:0.4, 1:0.2, 'NA':0}
        user_id2user_profile={}
        user_id2movie_lst=CovariateGenerator.get_user_id2movie_lst(self.orignal_data)
        user_id2item_rating=CovariateGenerator.get_user_id2item_rating(self.orignal_data)

        #perform NER to extract cov
        movie_id2movie_info_dic=CovariateGenerator.get_movie_id2movie_info_dic(self.orignal_data)
        movie_id2movie_profile={}
        #map to our cov 
        for movie_id, movie_info_dic in movie_id2movie_info_dic.items():
            movie_profile=self.convert2item_profile(movie_info_dic) 
            movie_id2movie_profile[movie_id]=movie_profile

        inital_profile={}  #init_profile for each user
        temp_key=list(movie_id2movie_profile.keys())[0]
        for k in movie_id2movie_profile[temp_key].keys():
            inital_profile[k]=0

        if self.track_unseen_director:
            current_unseen_director_dic={}
            for user_id, movie_id_lst in user_id2movie_lst.items():
                user_profile=inital_profile.copy()  
                for movie_id in movie_id_lst:
                    rating=user_id2item_rating[user_id][movie_id]
                    movie_profile=movie_id2movie_profile[movie_id] 
                    movie_profile_weighted= {k:v*rating2weight[rating] for k,v in movie_profile.items()}
                    user_profile_updated={k: user_profile[k] + movie_profile_weighted[k] for k in list(movie_profile_weighted.keys())}
                    user_profile=user_profile_updated.copy()

                    movie_info_dictionary=movie_id2movie_info_dic[movie_id]
                    director_lst= movie_info_dictionary['director']
                    for director in director_lst:
                        if 'D_' + director not in self.cov_name2LST['DIRECTOR']:
                            if director not in current_unseen_director_dic:
                                current_unseen_director_dic[director]=1
                            else:
                                current_unseen_director_dic[director]+=1

                user_id2user_profile[user_id]=user_profile
            updated_UNSEEN_DIRECTOR_DIC={k:v for k,v in self.unseen_director2count.items()} #copy prev unseen director dict

            for director, count in current_unseen_director_dic.items():
                if director in self.unseen_director2count:
                    updated_UNSEEN_DIRECTOR_DIC[director]+=count
                else:
                    updated_UNSEEN_DIRECTOR_DIC[director]=count

            self.result_user_id2user_profile=user_id2user_profile
            self.result_unseen_director2count=updated_UNSEEN_DIRECTOR_DIC
        
        else:
            for user_id, movie_id_lst in user_id2movie_lst.items():
                user_profile=inital_profile.copy()  
                for movie_id in movie_id_lst:
                    rating=user_id2item_rating[user_id][movie_id]
                    movie_profile=movie_id2movie_profile[movie_id] 
                    movie_profile_weighted= {k:v*rating2weight[rating] for k,v in movie_profile.items()}
                    user_profile_updated={k: user_profile[k] + movie_profile_weighted[k] for k in list(movie_profile_weighted.keys())}
                    user_profile=user_profile_updated.copy()
                user_id2user_profile[user_id]=user_profile
            self.result_user_id2user_profile=user_id2user_profile
        
    def get_user_id2upvotes(self):
        user_id2upvotes={}
        for user_id, rating_lst in (self.orignal_data).items():
            if user_id not in user_id2upvotes:
                user_id2upvotes[user_id]={'total_upvotes':0}
            for rating in rating_lst:
                upvotes=rating['upvotes']
                user_id2upvotes[user_id]['total_upvotes']+=upvotes
        self.result_user_id2upvotes=user_id2upvotes
    
    def get_user_id2num_movies(self):
        user_id2num_movies={}
        for user_id, rating_lst in (self.orignal_data).items():
            if user_id not in user_id2num_movies:
                user_id2num_movies[user_id]={'number_of_movies':0}
            user_id2num_movies[user_id]['number_of_movies']=len(rating_lst)
        self.result_user_id2num_movies=user_id2num_movies
    
    def get_user_id2vocab_count_vec(self):
        user_id2vocab_count_vec={}
        for user_id, rating_lst in (self.orignal_data).items():
            user_id2vocab_count_vec[user_id]={}

            for token in self.cov_name2LST['VOCAB']:
                user_id2vocab_count_vec[user_id][token]=0

            for rating in rating_lst:
                if rating['comment']!='NA' and rating['rating']!='NA':
                    if rating['rating']>=3:
                        text=rating['comment']
                        seg_result=lac.run(text)
                        pos_lst=seg_result[1]
                        text_lst=seg_result[0]
                        n_idx=[i for i in range(len(pos_lst)) if pos_lst[i] in ['n','vn','an']]
                        n_tokens=[text_lst[i] for i in n_idx]
                        for token in n_tokens:
                            token=zhconv.convert(token, 'zh-hans')
                            token='V_'+token
                            if token in user_id2vocab_count_vec[user_id]:
                                user_id2vocab_count_vec[user_id][token]+=1
                            
        self.result_user_id2vocab_count_vec=user_id2vocab_count_vec


    def merge_4_dicts(d1,d2,d3,d4):
        d={}
        for k,v in d1.items():
            d[k]=v
        for k,v in d2.items():
            d[k]=v
        for k,v in d3.items():
            d[k]=v
        for k,v in d4.items():
            d[k]=v
        return d
           
    def run(self): 
        self.get_user_id2vocab_count_vec()
        print('finish generating vocabs')
        
        self.get_user_id2user_profile()
        print('finish generating movie-related covariates')
        
        self.get_user_id2upvotes()
        print('finish generating upvotes covariates')
        
        self.get_user_id2num_movies()
        
        print('finish generating number of movies rated')
        
        result_user_id2cov={}
        for user_id in list(self.result_user_id2user_profile.keys()):
            
            result_user_id2cov[user_id]=CovariateGenerator.merge_4_dicts(self.result_user_id2upvotes[user_id],
                                                                         self.result_user_id2num_movies[user_id],
                                                                         self.result_user_id2user_profile[user_id],
                                                                         self.result_user_id2vocab_count_vec[user_id])
            
           
    
        if self.track_unseen_director:
            return {'user_id2cov': result_user_id2cov,
                    'updated_unseen_director2count': self.result_unseen_director2count}
        else:
            return {'user_id2cov': result_user_id2cov}



