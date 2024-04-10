import numpy as np
import scipy.special as sp


class TTM:
    def __init__(self, K, cov_mat,n_iters,fix_iters, prev_theta_tensor, prev_phi_tensor, alpha_tensor, beta_tensor):
        self.K=K
        self.cov_mat=cov_mat
        self.n_iters=n_iters
        self.fix_iters=fix_iters
        self.prev_theta_tensor = prev_theta_tensor
        self.prev_phi_tensor = prev_phi_tensor
        self.alpha_tensor= alpha_tensor
        self.beta_tensor = beta_tensor
        
        self.U =  self.cov_mat.shape[0]
        self.V =  self.cov_mat.shape[1]
        self.L = self.alpha_tensor.shape[0]
        
    def transform_D(self):
        D=[]
        for i, cov in enumerate(self.cov_mat):
            d=[]
            for cov_id, count in enumerate(cov):
                if count>0:
                    for c in range(int(count*5)):
                        d.append(cov_id)
            D +=[d]
        self.D=D
        
    def _gibbs(self):
        self.n_zw= np.zeros((self.K, self.V),dtype=int)
        self.m_zu= np.zeros((self.K, self.U),dtype=int)
        self.Z=[]
        
        for u, d in enumerate(self.D):
            self.Z += [[0]*len(d)]
            for i,w in enumerate(d):
                
                np.random.seed(13 + u + i)
                j= np.random.choice(self.K, 1)[0]
                self.m_zu[j,u] +=1
                self.n_zw[j,w] += 1
                self.Z[u][i]=j
                
        print('finish init')
                
        for iter in range(self.n_iters):
            for u, d in enumerate(self.D):
                for i,w in enumerate(d):
                    j= self.Z[u][i]
                    self.m_zu[j,u] -= 1
                    self.n_zw[j, w] -= 1
                    
                    P_z= np.zeros(self.K)
                    P_z = (self.n_zw[:,w] + (self.beta_tensor[:,:, w]*self.prev_phi_tensor[:,:, w]).sum(axis=0))\
                        / (self.n_zw + (self.beta_tensor*self.prev_phi_tensor).sum(axis=0)).sum(axis=1) \
                        * (self.m_zu[:,u]  + (self.alpha_tensor[:,:,u]*self.prev_theta_tensor[:,:,u]).sum(axis=0)) \
                        / (self.m_zu[:,u]  + (self.alpha_tensor[:,:,u]*self.prev_theta_tensor[:,:,u]).sum(axis=0)).sum() 
                    P_z = P_z/P_z.sum()
                    
                    np.random.seed(13 + iter+ u + i)
                    j = np.random.choice(self.K, size=1, p=P_z)[0]
                    self.m_zu[j,u]+=1
                    self.n_zw[j, w] += 1
                    
                    self.Z[u][i]=j
            print('finish sampling at iter ' + str(iter))
            
            
            for update_iter in range(self.fix_iters):
                g3 = np.zeros((self.K, self.U))
                g4 = np.zeros((self.K, self.U))
            
                num_ = np.zeros((self.K, self.U))
                den_ = np.zeros((self.U))
                
                for topic in range(self.K):
                    for u_ in range(self.U):    
                        g3[topic,u_] = self.m_zu[topic,u_] + (self.prev_theta_tensor[:,topic,u_]* self.alpha_tensor[:,topic,u_]).sum()
                        g4[topic,u_] =(self.prev_theta_tensor[:,topic,u_]* self.alpha_tensor[:,topic,u_]).sum()
                
                for u_ in range(self.U): 
                    den_[u_] = sp.digamma(g3[:,u_].sum()) -  sp.digamma(g4[:,u_].sum()) 
                        
                    for topic in range(self.K):
                        num_[topic,u_] = (sp.digamma(g3[topic,u_]) -  sp.digamma(g4[topic,u_])) 
                        
                for u_ in range(self.U):    
                    for l in range(self.L):
                        val=((num_[:,u_] * self.prev_theta_tensor[l,:,u_]).sum()) / den_[u_]  
                    
                        for topic in range(self.K):
                            self.alpha_tensor[l,topic,u_] = self.alpha_tensor[l,topic,u_]*val
                            
            print('finish updating alpha at iter ' + str(iter))
            
            for update_iter in range(self.fix_iters):
                gc = np.zeros((self.K, self.V))
                gd = np.zeros((self.K, self.V))
                
                num_ = np.zeros((self.K, self.V))
                den_ = np.zeros((self.K))
                
                for topic in range(self.K):
                    for w in range(self.V):
                        gc[topic,w] = self.n_zw[topic,w]+ (self.prev_phi_tensor[:,topic,w]* self.beta_tensor[:,topic,w]).sum()
                        gd[topic,w] = (self.prev_phi_tensor[:,topic,w] * self.beta_tensor[:,topic,w]).sum()
                    
                for topic in range(self.K):
                    den_[topic]  += sp.digamma(gc[topic,:].sum()) -  sp.digamma(gd[topic,:].sum())
                    for w in range(self.V):
                        num_[topic,w] += sp.digamma(gc[topic,w]) -  sp.digamma(gd[topic,w])
                        
                for topic in range(self.K):
                    for l in range(self.L):
                        val = ((num_[topic,:] * self.prev_phi_tensor[l,topic,:]).sum()) / den_[topic] 
                        
                        for w in range(self.V):
                            self.beta_tensor[l,topic,w] = self.beta_tensor[l,topic,w] * val 
                
            print('finish updating beta at iter ' + str(iter))
            
            
    def fit(self):
        self.cur_phi = np.zeros((self.K,self.V))
        self.cur_theta = np.zeros((self.K, self.U))
        
        for u in range(self.U):
            self.cur_theta[:,u] = (self.m_zu[:,u] + (self.prev_theta_tensor[:,:,u] * self.alpha_tensor[:,:,u]).sum(axis=0)) \
            /((self.m_zu[:,u] + (self.prev_theta_tensor[:,:,u]* self.alpha_tensor[:,:,u]).sum(axis=0)).sum())
        
        for z in range(self.K):
            self.cur_phi[z,:]  = (self.n_zw[z,:] + (self.prev_phi_tensor[:,z,:]*self.beta_tensor[:,z,:]).sum(axis=0)) \
            / ((self.n_zw[z,:] + (self.prev_phi_tensor[:,z,:]*self.beta_tensor[:,z,:]).sum(axis=0)).sum())
    
            
            
            
                    
            
                
            
        
            