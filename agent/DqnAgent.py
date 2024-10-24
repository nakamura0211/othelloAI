import random

import numpy as np
from collections import deque

from keras import Sequential, Input
from keras.src.layers import (
    Flatten,
    Dense,
    BatchNormalization,
    Conv2D,
    MaxPooling2D,
)

from keras._tf_keras.keras.callbacks import TensorBoard

from domain import OthelloEnv
from domain.models import *


class DqnAgent(Agent):
    def __init__(self, epsilon: float = 1.0):
        self.memory = deque[tuple[State, Action, int, State, bool]](maxlen=2000)
        self.gamma = 0.98
        self.epsilon = epsilon
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.998
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential()
        model.add(Input(shape=(SIZE, SIZE, 3)))
        model.add(
            Conv2D(256, (3, 3), activation="relu", padding="same", use_bias=False)
        )
        model.add(BatchNormalization())
        model.add(
            Conv2D(256, (3, 3), activation="relu", padding="same", use_bias=False)
        )
        model.add(BatchNormalization())
        model.add(MaxPooling2D((2, 2)))
        model.add(Flatten())
        # model.add(Dense(256,activation='relu'))
        model.add(Dense(SIZE * SIZE * 2, activation="relu"))
        model.add(Dense(SIZE * SIZE, activation="linear"))
        print(model.summary())
        model.compile(loss="mse", optimizer="adam")
        return model

    def remember(
        self, state: State, action: Action, reward: int, next_state: State, done: bool
    ):
        self.memory.append((state, action, reward, next_state, done))

    def train(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        x = []
        y = []
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward - self.gamma * np.amax(
                    self.model.predict(
                        next_state.to_image().reshape((1, SIZE, SIZE, 3)),
                        verbose=0,
                    )[0]
                )
            target_f = self.model.predict(
                state.to_image().reshape((1, SIZE, SIZE, 3)), verbose=0
            )
            target_f[0][action.index] = target
            invalid_mask = np.min(target_f)
            valid_actions = {a.index for a in OthelloEnv.valid_actions(state)}
            for i in range(SIZE, SIZE):
                if i not in valid_actions:
                    target_f[0][i] = invalid_mask

            x.append(state.to_image())
            y.append(target_f)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        self.model.fit(np.array(x), np.array(y), epochs=1, verbose=0)

    def act(self, state: State) -> Action:
        if np.random.rand() <= self.epsilon:
            return random.choice(OthelloEnv.valid_actions(state))
        valid = [action.index for action in OthelloEnv.valid_actions(state)]
        act_values = self.model.predict(
            state.to_image().reshape(1, SIZE, SIZE, 3), verbose=0
        )
        return Action(
            np.argmax(
                [v if i in valid else -np.inf for i, v in enumerate(act_values[0])]
            )
        )

    def policy(self, state: State) -> list[float]:
        return self.model.predict(state.to_image().reshape((1, SIZE, SIZE, 3)))

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)
