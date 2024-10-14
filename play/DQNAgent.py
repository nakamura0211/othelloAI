import random

import numpy as np
from collections import deque

from keras import Sequential, Input
from keras.src.layers import Conv3D, Flatten, Dense, BatchNormalization, Dropout, MaxPooling3D, Conv2D, MaxPooling2D

import OthelloEnv
from OthelloEnv import encode_state
from play.agent import Agent


class DqnAgent(Agent):
    def __init__(self,size=8):
        self.size=size
        self.memory= deque(maxlen=2000)
        self.gamma=0.95
        self.epsilon=1.0
        self.epsilon_min=0.01
        self.epsilon_decay=0.995
        self.learning_rate=0.001
        self.model=self._build_model()

    def __call__(self, othello, color: int) -> tuple[int, int]:
        state=encode_state(othello)
        act=self.act(state)
        return act//8,act%8

    def _build_model(self):
        model=Sequential()
        model.add(Input(shape=(3,self.size,self.size)))
        model.add(Conv2D(32, (3, 3), activation='tanh', padding='same'))
        model.add(BatchNormalization())
        model.add(Conv2D(64, (3, 3), activation='tanh', padding='same'))
        model.add(BatchNormalization())
        model.add(MaxPooling2D((2, 2)))
        model.add(Flatten())
        #model.add(Dense(256,activation='relu'))
        model.add(Dense(self.size*self.size*2,activation='relu'))
        model.add(Dense(self.size*self.size,activation='linear'))
        print(model.summary())
        model.compile(loss='mse',optimizer='adam')
        return model

    def remember(self,state,action,reward,next_state,done):
        self.memory.append((state,action,reward,next_state,done))

    def train(self,batch_size):
        minibatch=random.sample(self.memory,batch_size)
        for state,action,reward,next_state,done in minibatch:
            target=reward
            if not done:
                target=reward+self.gamma*np.amax(self.model.predict(np.array(next_state).reshape(1,3,self.size,self.size),verbose=0)[0])
            state=np.array(state).reshape(1,3,self.size,self.size)
            target_f=self.model.predict(state,verbose=0)
            target_f[0][action]=target
            self.model.fit(state,target_f,epochs=1,verbose=0)
        if self.epsilon>self.epsilon_min:
            self.epsilon*=self.epsilon_decay


    def act(self,state)->int:
        if np.random.rand() <= self.epsilon:
            x,y=random.choice(OthelloEnv.valid_actions(state))
            return x*self.size+y
        valid=[x*self.size+y for x,y in OthelloEnv.valid_actions(state)]
        state=np.array(state).reshape(1,3,self.size,self.size)
        act_values=self.model.predict(state,verbose=0)
        return np.argmax([a if i in valid else -float("inf") for i,a in enumerate(act_values[0])])

    def replay(self,batch_size):
        pass

    def load(self,name):
        self.model.load_weights(name)

    def save(self,name):
        self.model.save_weights(name)
