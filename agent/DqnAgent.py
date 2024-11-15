import random

import numpy as np
from collections import deque
import keras
from keras import Sequential
from keras.src.models import Model
import keras._tf_keras.keras.backend as K
from keras.src.layers import (
    Flatten,
    Dense,
    BatchNormalization,
    Conv2D,
    MaxPooling2D,
    Activation,
    Dropout,
    Lambda,
    Input,
    concatenate,
)
import tensorflow as tf
from keras.src.losses import (
    categorical_crossentropy,
    mean_squared_error,
    mean_absolute_error,
    huber,
    Huber,
)
from keras.src.activations import relu
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
    invalid_mask = -2

    def __init__(
        self, epsilon: float = 1.0, pb_epsilon: float = 1.0, weights: list | None = None
    ):
        self.gamma = 1
        self.pb_epsilon = pb_epsilon
        self.pb_epsilon_min = 0.6
        self.pb_epsilon_decay = 0.9999
        self.epsilon = epsilon
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9994
        self.learning_rate = 0.000005
        self.model = self._build_dueling_model()
        if weights is not None and len(weights) != 0:
            self.model.set_weights(weights)
        self.target = self._build_dueling_model()
        self.sync_network()

    def sync_network(self):
        self.target.set_weights(self.model.weights)

    def _build_dueling_model(self):
        kernel_initializer = HeNormal()
        inputs = Input(shape=(SIZE, SIZE, 2))
        x = relu(
            BatchNormalization()(
                Conv2D(
                    512,
                    3,
                    padding="same",
                    use_bias=False,
                    kernel_initializer=kernel_initializer,
                )(inputs)
            )
        )
        x = relu(
            BatchNormalization()(
                Conv2D(
                    512,
                    3,
                    padding="same",
                    use_bias=False,
                    kernel_initializer=kernel_initializer,
                )(x)
            )
        )
        x = relu(
            BatchNormalization()(
                Conv2D(
                    512,
                    3,
                    padding="valid",
                    use_bias=False,
                    kernel_initializer=kernel_initializer,
                )(x)
            )
        )

        x = relu(
            BatchNormalization()(
                Conv2D(
                    512,
                    3,
                    padding="valid",
                    use_bias=False,
                    kernel_initializer=kernel_initializer,
                )(x)
            )
        )

        x = Flatten()(x)

        v = Dropout(0.3)(relu(BatchNormalization()(Dense(1024)(x))))
        v = Dropout(0.3)(relu(BatchNormalization()(Dense(512)(v))))
        v = Dense(1)(v)

        adv = Dropout(0.3)(relu(BatchNormalization()(Dense(1024)(x))))
        adv = Dropout(0.3)(relu(BatchNormalization()(Dense(512)(adv))))
        adv = Dense(SIZE * SIZE)(adv)
        y = concatenate([v, adv])
        outputs = Activation("tanh")(
            # BatchNormalization()(
            Lambda(
                lambda a: K.expand_dims(a[:, 0], -1) + a[:, 1:],
                output_shape=(SIZE * SIZE,),
            )(y)
            # )
        )

        model = Model(inputs=inputs, outputs=outputs)

        model.compile(
            loss=TdHuberLoss(),
            optimizer=Adam(learning_rate=self.learning_rate),
            # metrics=["cosine_similarity", "mean_absolute_error"],
        )

        return model

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
            loss=TdHuberLoss(),
            optimizer=Adam(learning_rate=self.learning_rate),
            # metrics=["cosine_similarity", "mean_absolute_error"],
        )
        return model

    @staticmethod
    def tanh_crossentropy(y_true, y_pred):
        return categorical_crossentropy((y_true + 1) / 2, (y_pred + 1) / 2)

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

            # valid_actions = {a.index for a in OthelloEnv.valid_actions(exp.state)}
            for i in range(SIZE * SIZE):
                if i != exp.action.index:
                    target_y[i] = DqnAgent.invalid_mask

            x.append(exp.state.to_image())
            y.append(target_y)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        if self.pb_epsilon > self.pb_epsilon_min:
            self.pb_epsilon *= self.pb_epsilon_decay
        self.model.fit(np.array(x), np.array(y), epochs=1, verbose=1)

    def fit(self, x, td_losses):
        pass

    def act(self, state: State) -> Action:
        if np.random.rand() <= self.epsilon:
            return random.choice(OthelloEnv.valid_actions(state))
        valid = {action.index for action in OthelloEnv.valid_actions(state)}
        act_values = self.model.predict(
            state.to_image().reshape(1, SIZE, SIZE, 2), verbose=0
        )
        filtered = np.array(
            [v if i in valid else -1 for i, v in enumerate(act_values[0])]
        )
        if np.random.rand() <= self.pb_epsilon:
            weights = (filtered + 1) / 2
            if weights.sum() <= 0:
                return random.choice(OthelloEnv.valid_actions(state))
            act = random.choices([i for i in range(SIZE * SIZE)], weights=weights)[0]
        else:
            act = np.argmax(filtered)
        if act in valid:
            return Action(act)
        else:
            return random.choice(OthelloEnv.valid_actions(state))

    def policy(self, state: State) -> list[float]:
        return self.model.predict(state.to_image().reshape((1, SIZE, SIZE, 2)))[0]

    def Q(self, state: State, action: Action):
        return self.policy(state)[action.index]

    def V(self, state: State) -> float:
        policy = self.model.predict(
            state.to_image().reshape((1, SIZE, SIZE, 2)), verbose=0
        )[0]
        valid = {action.index for action in OthelloEnv.valid_actions(state)}
        return np.amax([v if i in valid else -2 for i, v in enumerate(policy)])

    def load(self, name):
        self.model.load_weights(name)
        return self

    def save(self, name):
        self.model.save_weights(name)
        return self


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


class TdHuberLoss(tf.keras.losses.Loss):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def call(self, y_true, y_pred):
        # y_pred が 0 でない要素のマスクを作成
        mask = tf.not_equal(y_true, DqnAgent.invalid_mask)
        # y_pred と y_true の 0 でないインデックスのみを取得
        y_pred_filtered = tf.boolean_mask(y_pred, mask)
        y_true_filtered = tf.boolean_mask(y_true, mask)
        return huber(y_true_filtered, y_pred_filtered, delta=0.1) * 10


class TdMaeLoss(tf.keras.losses.Loss):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def call(self, y_true, y_pred):
        # y_pred が 0 でない要素のマスクを作成
        mask = tf.not_equal(y_true, DqnAgent.invalid_mask)
        # y_pred と y_true の 0 でないインデックスのみを取得
        y_pred_filtered = tf.boolean_mask(y_pred, mask)
        y_true_filtered = tf.boolean_mask(y_true, mask)
        return tf.abs(y_true_filtered - y_pred_filtered)


class TdCrossEntropyLoss(tf.keras.losses.Loss):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def call(self, y_true, y_pred):
        # y_pred が 0 でない要素のマスクを作成
        mask = tf.not_equal(y_true, DqnAgent.invalid_mask)
        # y_pred と y_true の 0 でないインデックスのみを取得
        y_pred_filtered = tf.boolean_mask(y_pred, mask)
        y_true_filtered = tf.boolean_mask(y_true, mask)
        return tf.reduce_sum(y_true_filtered * tf.math.log(y_pred_filtered + 0.00001))


class Memory:
    def __init__(self, maxlen: int = 200000):
        self.transition = deque[Experience](maxlen=maxlen)
        self.priorities = deque(maxlen=maxlen)
        self.total_p = 0
        self.a = 1.0
        self.a_decay = -0.0005
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
        self.rate_decay = 0.15
        self.rate_decay_grow = 0.0005
        self.rate_decay_max = 0.8

    def length(self):
        return len(self.memories[0])

    def add(self, transiton_batch: list[Experience]):
        n = (SIZE * SIZE - 4) // self.memory_len
        for exp in transiton_batch:
            blank, _, _ = OthelloEnv.count(exp.state)
            if blank == SIZE * SIZE - 4:
                self.memories[0].append(exp)
            else:
                self.memories[blank // n].append(exp)
        if self.rate_decay >= self.rate_decay_max:
            self.rate_decay = self.rate_decay_max
        else:
            self.rate_decay += self.rate_decay_grow

    def sample(self, n) -> list[Experience]:
        allocate_rate = []
        rate = 1
        for i in range(self.memory_len):
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


class DqnNetwork(Model):
    """See https://github.com/suragnair/alpha-zero-general/"""

    def __init__(self, action_space, filters=512, use_bias=False):

        super(DqnNetwork, self).__init__()

        self.action_space = action_space
        self.filters = filters

        self.conv1 = Conv2D(filters, 3, padding="same", use_bias=use_bias)
        self.bn1 = BatchNormalization()

        self.conv2 = Conv2D(filters, 3, padding="same", use_bias=use_bias)
        self.bn2 = BatchNormalization()

        self.conv3 = Conv2D(filters, 3, padding="valid", use_bias=use_bias)
        self.bn3 = BatchNormalization()

        self.conv4 = Conv2D(filters, 3, padding="valid", use_bias=use_bias)
        self.bn4 = BatchNormalization()

        self.flat = Flatten()

        self.dense5 = Dense(1024, use_bias=use_bias)
        self.bn5 = BatchNormalization()
        self.drop5 = Dropout(0.3)

        self.dense6 = Dense(512, use_bias=use_bias)
        self.bn6 = BatchNormalization()
        self.drop6 = Dropout(0.3)

        self.q = Dense(self.action_space, activation="tanh")

        self.value = Dense(1, activation="tanh")

    def call(self, x, training=False):
        x = relu(self.bn1(self.conv1(x), training=training))
        x = relu(self.bn2(self.conv2(x), training=training))
        x = relu(self.bn3(self.conv3(x), training=training))
        x = relu(self.bn4(self.conv4(x), training=training))

        x = self.flat(x)

        x = relu(self.bn5(self.dense5(x), training=training))
        x = self.drop5(x, training=training)

        x = relu(self.bn6(self.dense6(x), training=training))
        x = self.drop6(x, training=training)

        q = self.q(x)
        v = self.value(x)

        return q, v

    def predict(self, state):
        if len(state.shape) == 3:
            state = state[np.newaxis, ...]

        q, value = self(state)

        return q, value
