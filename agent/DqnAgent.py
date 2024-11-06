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
import tensorflow as tf
from keras.src.losses import (
    categorical_crossentropy,
    mean_squared_error,
    mean_absolute_error,
    huber,
)
from keras.src.initializers import HeNormal
from keras.src.optimizers import Adam, SGD
from keras.src.callbacks import TensorBoard
from tqdm import tqdm

from domain import OthelloEnv
from domain.models import *


@dataclass
class HyperParam:
    learning_rate: float
    epsilon: float
    epsilon_min: float
    epsilon_decay: float
    gamma: float
    memory_maxlen: int


@dataclass
class Experience:
    state: State
    action: Action
    reward: float
    next_state: State
    done: bool


class DqnAgent(Agent):
    def __init__(self, epsilon: float = 1.0, weights: list | None = None):
        self.gamma = 1
        self.epsilon = epsilon
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.999
        self.learning_rate = 0.000005
        self.model = self._build_model()
        if weights is not None and len(weights) != 0:
            self.model.set_weights(weights)
        self.target = self._build_model()
        self.sync_network()

    def sync_network(self):
        self.target.set_weights(self.model.weights)

    def _build_model(self):
        model = Sequential()
        relu = Activation("relu")
        kernel_initializer = HeNormal()
        model.add(Input(shape=(SIZE, SIZE, 2)))
        model.add(
            Conv2D(
                512,
                3,
                padding="same",
                use_bias=False,
                kernel_initializer=kernel_initializer,
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
                kernel_initializer=kernel_initializer,
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
                kernel_initializer=kernel_initializer,
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
                kernel_initializer=kernel_initializer,
            )
        )
        model.add(BatchNormalization())
        model.add(relu)
        model.add(Flatten())

        model.add(Dense(1024, kernel_initializer=kernel_initializer))
        model.add(BatchNormalization())
        model.add(relu)
        model.add(Dropout(0.3))

        model.add(Dense(512, kernel_initializer=kernel_initializer))
        model.add(BatchNormalization())
        model.add(relu)
        model.add(Dropout(0.3))

        model.add(Dense(SIZE * SIZE, kernel_initializer=kernel_initializer))
        model.add(BatchNormalization())
        model.add(Activation("tanh"))
        model.compile(
            loss=CosineSimilarityLoss(),
            optimizer=Adam(learning_rate=self.learning_rate),
            metrics=["cosine_similarity", "mean_absolute_error"],
        )
        return model

    @staticmethod
    def dqn_loss(y_true, y_pred):
        return tf.reduce_mean(tf.square(y_true - y_pred))

    @staticmethod
    def tanh_crossentropy(y_true, y_pred):
        return categorical_crossentropy((y_true + 1) / 2, (y_pred + 1) / 2)

    @staticmethod
    def tanh_mse(y_true, y_pred):
        return mean_squared_error(y_true * 10, y_pred * 10)

    def train(self, minibatch: list[Experience]):
        x = []
        y = []
        x_next = []
        x_cur = []
        for exp in minibatch:
            x_next.append(exp.next_state.to_image())
            x_cur.append(exp.state.to_image())
        y_next = self.model.predict(np.array(x_next), verbose=0)
        y_next_target = self.target.predict(np.array(x_next), verbose=0)
        target_ys = self.model.predict(np.array(x_cur), verbose=0)

        for i, exp in enumerate(minibatch):
            if not exp.done:
                nx_valid = {a.index for a in OthelloEnv.valid_actions(exp.next_state)}
                best_nx_act = np.argmax(
                    [v if i in nx_valid else -2 for i, v in enumerate(y_next[i])]
                )
                nx_act_value = y_next_target[i][best_nx_act]
                if exp.state.color == exp.next_state.color:
                    target = exp.reward + self.gamma * nx_act_value
                else:
                    target = exp.reward - self.gamma * nx_act_value
            else:
                target = exp.reward

            target_y = target_ys[i]
            target_y[exp.action.index] = target
            invalid_mask = 0
            valid_actions = {a.index for a in OthelloEnv.valid_actions(exp.state)}
            for i in range(SIZE * SIZE):
                if i not in valid_actions:
                    target_y[i] = invalid_mask

            x.append(exp.state.to_image())
            y.append(target_y.reshape((SIZE * SIZE)))
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        self.model.fit(np.array(x), np.array(y), epochs=1, verbose=1)

    def act(self, state: State) -> Action:
        if np.random.rand() <= self.epsilon:
            return random.choice(OthelloEnv.valid_actions(state))
        valid = [action.index for action in OthelloEnv.valid_actions(state)]
        act_values = self.model.predict(
            state.to_image().reshape(1, SIZE, SIZE, 2), verbose=0
        )
        return Action(
            np.argmax([v if i in valid else -2 for i, v in enumerate(act_values[0])])
        )

    def policy(self, state: State) -> list[float]:
        return self.model.predict(state.to_image().reshape((1, SIZE, SIZE, 2)))[0]

    def Q(self, state: State, action: Action):
        return self.policy(state)[action.index]

    def load(self, name):

        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)


class CosineSimilarityLoss(keras.losses.Loss):
    def __init__(self, name="cosine_similarity_loss"):
        super().__init__(name=name)

    def call(self, y_true, y_pred):
        y_true_normalized = tf.nn.l2_normalize(y_true, axis=-1)
        y_pred_normalized = tf.nn.l2_normalize(y_pred, axis=-1)
        cosine_similarity = tf.reduce_sum(
            y_true_normalized * y_pred_normalized, axis=-1
        )
        return 1.0 - cosine_similarity


class Memory:
    def __init__(self, maxlen: int = 200000):
        self.transition = deque[Experience](maxlen=maxlen)
        self.priorities = deque(maxlen=maxlen)
        self.total_p = 0
        self.a = 1.0
        self.a_decay = -0.001
        self.a_min = 0

    def _error_to_priority(self, error_batch):
        priority_batch = []
        for error in error_batch:
            priority_batch.append(abs(error) ** self.a + 0.00001)
        return priority_batch

    def length(self):
        return len(self.transition)

    def add(self, transiton_batch, error_batch):
        priority_batch = self._error_to_priority(error_batch)
        self.priorities.extend(priority_batch)
        self.transition.extend(transiton_batch)
        self.total_p = sum(self.priorities)
        if self.a > self.a_min:
            self.a -= self.a_decay
        else:
            self.a = self.a_min

    def sample(self, n) -> list[Experience]:
        batch = []
        idx_batch = []
        segment = self.total_p / n

        idx = -1
        sum_p = 0
        for i in range(n):
            a = segment * i
            b = segment * (i + 1)

            s = random.uniform(a, b)
            while sum_p < s:
                sum_p += self.priorities[idx]
                idx += 1
            idx_batch.append(idx)
            batch.append(self.transition[idx])
        return batch

    def update(self, idx_batch, error_batch):
        priority_batch = self._error_to_priority(error_batch)
        for i in range(len(idx_batch)):
            change = priority_batch[i] - self.priorities[idx_batch[i]]
            self.total_p += change
            self.priorities[idx_batch[i]] = priority_batch[i]


class SegmentMemory:
    def __init__(self, maxlen, memory_len):
        each_len = maxlen // memory_len
        self.memory_len = memory_len
        self.memories = [deque(maxlen=each_len) for _ in range(memory_len)]
        self.rate_decay = 0.1
        self.rate_decay_grow = 0.001
        self.rate_decay_max = 1

    def length(self):
        return len(self.memories[0])

    def add(self, transiton_batch: list[Experience]):
        n = SIZE * SIZE // self.memory_len
        for exp in transiton_batch:
            blank, _, _ = OthelloEnv.count(exp.state)
            self.memories[blank // n].append(exp)
        if self.rate_decay >= self.rate_decay_max:
            self.rate_decay = self.rate_decay_max
        else:
            self.rate_decay += self.rate_decay_grow

    def sample(self, n) -> list[Experience]:
        allocate_rate = []
        rate = 1
        for _ in range(self.memory_len):
            allocate_rate.append(rate)
            rate *= self.rate_decay
        result = []
        rate_sum = sum(allocate_rate)
        for i, rate in enumerate(allocate_rate):
            ln = int(rate / rate_sum * n)
            if len(self.memories[i]) <= ln:
                result.extend(self.memories[i])
            else:
                result.extend(random.choices(self.memories[i], k=ln))
        return result