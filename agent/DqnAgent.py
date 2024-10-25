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
    Activation,
)
from keras.src.initializers import HeNormal
from keras.src.optimizers import Adam

from domain import OthelloEnv
from domain.models import *
import ray


class DqnAgent(Agent):
    def __init__(self, epsilon: float = 1.0):
        self.memory = deque[tuple[State, Action, int, State, bool]](maxlen=2000)
        self.gamma = 0.998
        self.epsilon = epsilon
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.998
        self.learning_rate = 0.0005
        self.model = self._build_model()

    # modelがだす値は黒目線のpolicy(-1~1)
    def _build_model(self):
        model = Sequential()
        model.add(Input(shape=(SIZE, SIZE, 3)))
        model.add(
            Conv2D(
                512,
                (3, 3),
                activation="relu",
                padding="same",
                use_bias=False,
                kernel_initializer=HeNormal(),
            )
        )
        model.add(BatchNormalization())
        model.add(
            Conv2D(
                512,
                (3, 3),
                activation="relu",
                padding="same",
                use_bias=False,
                kernel_initializer=HeNormal(),
            )
        )
        model.add(BatchNormalization())
        # model.add(MaxPooling2D((2, 2)))
        model.add(Flatten())
        # model.add(Dense(256,activation='relu'))
        model.add(
            Dense(
                SIZE * SIZE * 2,
                activation="relu",
            )  # kernel_initializer=HeNormal())
        )
        model.add(Dense(SIZE * SIZE))
        model.add(BatchNormalization())
        model.add(Activation("tanh"))
        print(model.summary())
        model.compile(loss="mse", optimizer=Adam(learning_rate=self.learning_rate))
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
            if not done:
                nx_valid = {a.index for a in OthelloEnv.valid_actions(next_state)}
                nx_p = self.model.predict(
                    next_state.to_image().reshape((1, SIZE, SIZE, 3)),
                    verbose=0,
                )[0]
                target = self.gamma * np.amin(
                    [v if i in nx_valid else 2 for i, v in enumerate(nx_p)]
                )
            else:
                target = reward

            target_y = self.model.predict(
                state.to_image().reshape((1, SIZE, SIZE, 3)), verbose=0
            )[0]
            target_y[action.index] = target
            invalid_mask = 0
            valid_actions = {a.index for a in OthelloEnv.valid_actions(state)}
            for i in range(SIZE, SIZE):
                if i not in valid_actions:
                    target_y[i] = invalid_mask

            x.append(state.to_image())
            y.append(target_y.reshape((1, SIZE * SIZE)))
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
        if state.color == Color.BLACK:
            return Action(
                np.argmax(
                    [v if i in valid else -np.inf for i, v in enumerate(act_values[0])]
                )
            )
        else:
            return Action(
                np.argmin(
                    [v if i in valid else np.inf for i, v in enumerate(act_values[0])]
                )
            )

    def policy(self, state: State) -> list[float]:
        return self.model.predict(state.to_image().reshape((1, SIZE, SIZE, 3)))[0] * (
            1 if state.color == Color.BLACK else -1
        )

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)


class ReplayBuffer:
    def __init__(self, maxlen=2000) -> None:
        self.buffer = deque[tuple[State, Action, int, State, bool]](maxlen=maxlen)

    def append(self, sample: tuple[State, Action, int, State, bool]):
        self.buffer.append(sample)

    def get_minibatch(self, batch_size):

        pass

    pass
