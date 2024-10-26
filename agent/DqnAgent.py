import random

import numpy as np
from collections import deque
import keras
from keras import Sequential, Input
from keras.src.layers import (
    Flatten,
    Dense,
    BatchNormalization,
    Conv2D,
    MaxPooling2D,
    Activation,
    Dropout,
)
from keras.src.initializers import HeNormal
from keras.src.optimizers import Adam
from tqdm import tqdm

from domain import OthelloEnv
from domain.models import *
import ray


class DqnAgent(Agent):
    def __init__(self, epsilon: float = 1.0, weights: list | None = None):
        self.memory = deque[tuple[State, Action, int, State, bool]](maxlen=2000)
        self.gamma = 0.998
        self.epsilon = epsilon
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.98
        self.learning_rate = 0.001
        self.model = self._build_model()
        if weights is not None and len(weights) != 0:
            self.model.set_weights(weights)

    def _build_model(self):
        model = Sequential()
        relu = Activation("relu")
        model.add(Input(shape=(SIZE, SIZE, 3)))
        model.add(
            Conv2D(
                512,
                3,
                padding="same",
                use_bias=False,
            )
        )
        model.add(BatchNormalization())
        model.add(relu)
        model.add(
            Conv2D(
                512,
                3,
                padding="same",
                use_bias=False,
            )
        )
        model.add(BatchNormalization())
        model.add(relu)
        model.add(
            Conv2D(
                512,
                3,
                padding="valid",
                use_bias=False,
            )
        )
        model.add(BatchNormalization())
        model.add(relu)
        model.add(
            Conv2D(
                512,
                3,
                padding="valid",
                use_bias=False,
            )
        )
        model.add(BatchNormalization())
        model.add(relu)
        model.add(Flatten())

        model.add(Dense(1024, use_bias=False))
        model.add(BatchNormalization())
        model.add(relu)
        model.add(Dropout(0.3))

        model.add(Dense(512, use_bias=False))
        model.add(BatchNormalization())
        model.add(relu)
        model.add(Dropout(0.3))

        model.add(Dense(SIZE * SIZE, activation="tanh"))
        # model.add(BatchNormalization())
        # model.add(Activation("tanh"))
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
        x_next = []
        x_cur = []
        for state, action, reward, next_state, done in minibatch:
            x_next.append(next_state.to_image())
            x_cur.append(state.to_image())
        y_next = self.model.predict(np.array(x_next), verbose=0)
        target_ys = self.model.predict(np.array(x_cur), verbose=0)

        for i, (state, action, reward, next_state, done) in enumerate(minibatch):
            if not done:
                nx_valid = {a.index for a in OthelloEnv.valid_actions(next_state)}
                nx_p = y_next[i]
                target = self.gamma * np.amin(
                    [v if i in nx_valid else 2 for i, v in enumerate(nx_p)]
                )
            else:
                target = reward

            target_y = target_ys[i]
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
        return self.model.predict(state.to_image().reshape((1, SIZE, SIZE, 3)))[
            0
        ]  # * (1 if state.color == Color.BLACK else -1)

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)


class DqnNetwork(keras.Model):
    def __init__(self):
        super(DqnNetwork, self).__init__()
        self.conv1 = Conv2D(
            512,
            (3, 3),
            activation="relu",
            padding="same",
            use_bias=False,
            kernel_initializer=HeNormal(),
        )
        self.bn1 = BatchNormalization()
        self.conv2 = Conv2D(
            512,
            (3, 3),
            activation="relu",
            padding="same",
            use_bias=False,
            kernel_initializer=HeNormal(),
        )
        self.bn2 = BatchNormalization()
        self.flatten = Flatten()
        self.dense1 = Dense(
            SIZE * SIZE * 2, activation="relu", kernel_initializer=HeNormal()
        )
        self.dence2 = Dense(SIZE * SIZE)
        self.bn3 = BatchNormalization()
        self.tanh = Activation("tanh")

    def call(self, x):
        x = Input((SIZE, SIZE, 3))(x)
        x = self.bn1(self.conv1(x))
        x = self.bn2(self.conv2(x))
        x = self.dense1(self.flatten(x))
        return self.tanh(self.bn3(self.dence2(x)))

    def build(self, input_shape):
        super(DqnNetwork, self).build(input_shape)
