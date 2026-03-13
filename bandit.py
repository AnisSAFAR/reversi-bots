import random 
import numpy as np

class Bandit :
    def __init__(self,n):
        self.n = n
        self.bandits = [random.uniform(0, 1) for _ in range(n)]
    


    def play(self,i):
        coup = random.random()
        if coup < self.bandits[i]:
            return 1
        return 0


class AgentBanditRandom :
    def __init__(self,n):
        self.n = n
        self.times =[0 for _ in range(n)]
        self.rewards = [0 for _ in range (n)]

    def play(self):
        return np.random.randint(0,self.n)
    
    def reward(self,i,r):
        self.times[i]+=1
        self.rewards[i]+=r
    
    def reset(self):
        self.times =[0 for _ in range(self.n)]
        self.rewards = [0 for _ in range (self.n)]


class JeuBandit :
    def __init__(self,b:Bandit,agent:AgentBanditRandom):
        self.b = b
        self.agent = agent
        self.rewards = []
    
    def reset(self):
        self.agent.reset()
        self.rewards=[]
    
    def play(self,n):
        self.reset()
        for _ in range (n):
            i = self.agent.play()
            r = self.b.play(i)
            self.agent.reward(i,r)
            self.rewards.append(r)

class AgentGlouton (AgentBanditRandom):
    def play(self):
        for i in range (self.n):
            if self.times[i] == 0 :
                return i
        moyennes = [self.rewards[i] / self.times[i] for i in range(self.n)]
        return np.argmax(moyennes)
    

class AgentEpsilon (AgentBanditRandom) :
    def play(self):
        epsilon= 0.1
        if np.random.rand() < epsilon:
            return np.random.randint(0,self.n)
        for i in range(self.n):
            if self.times[i] == 0:
                return i

        moyennes = [self.rewards[i] / self.times[i] for i in range(self.n)]
        return np.argmax(moyennes)
    

class AgentUCB(AgentBanditRandom):
    def __init__(self, n,K=2):
        super().__init__(n)
        self.K = K
        self.index = 0 

    def play(self):
        self.index += 1

        for i in range(self.n):
            if self.times[i] == 0:
                return i

        tab = []
        for i in range(self.n):
            moyenne = self.rewards[i] / self.times[i]
            bonus = np.sqrt((self.K * np.log(self.index)) / self.times[i])
            tab.append(moyenne + bonus)

        return np.argmax(tab)


def regret(bandit,rewards):
    machinemax= max(bandit.bandits)
    regret=[]
    t=1
    
    for t in range(len(rewards)):
        gain_max=t*machinemax
        vrai_gain=sum(rewards[:t+1])
        regret.append(gain_max-vrai_gain)
    return regret


            

    


