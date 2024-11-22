import random
from math import ceil

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


@dataclass
class Experiences:
    length: int
    states: list[State]  # length+1
    actions: list[Action]  # length
    rewards: list[int]  # length
    done: bool


class DqnAgent(Agent):
    invalid_mask = -2

    def __init__(
        self,
        epsilon: float = 1.0,
        pb_epsilon: float = 1.0,
        weights: list | None = None,
        dueling: bool = True,
        double: bool = True,
        multistep: bool = True,
    ):
        self.gamma = 1
        self.pb_epsilon = pb_epsilon
        self.pb_epsilon_min = 0.6
        self.pb_epsilon_decay = 0.9999
        self.epsilon = epsilon
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9994
        self.learning_rate = 0.000005
        self.dueling = dueling
        self.multistep = multistep
        self.model = self._build_dueling_model() if dueling else self._build_model()
        if weights is not None and len(weights) != 0:
            self.model.set_weights(weights)
        if double:
            self.target = (
                self._build_dueling_model() if dueling else self._build_model()
            )
        self.double = double
        self.sync_network()

    def sync_network(self):
        if self.double:
            self.target.set_weights(self.model.weights)

    def _build_dueling_model(self):
        kernel_initializer = HeNormal()
        inputs = Input(shape=(SIZE, SIZE, 2), name="board_image")
        valid_mask = Input(shape=(SIZE * SIZE, 1), name="valid_mask")
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

        def subtract_valid_mean(inputs):
            adv, valid_mask = inputs
            valid_adv = adv * valid_mask[:, :, 0]

            valid_adv_stop = K.stop_gradient(valid_adv)
            valid_mask_stop = K.stop_gradient(valid_mask[:, :, 0])

            valid_mean = K.sum(valid_adv_stop, axis=1, keepdims=True) / (
                K.sum(valid_mask_stop, axis=1, keepdims=True) + K.epsilon()
            )
            return adv - valid_mean

        adv_adjusted = Lambda(subtract_valid_mean, output_shape=(SIZE * SIZE,))(
            [adv, valid_mask]
        )
        y = concatenate([v, adv_adjusted])
        outputs = Activation("tanh")(
            BatchNormalization()(
                Lambda(
                    lambda a: K.expand_dims(a[:, 0], -1) + a[:, 1:],
                    output_shape=(SIZE * SIZE,),
                )(y)
            )
        )

        model = Model(inputs=[inputs, valid_mask], outputs=outputs)

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

    def q_values_list(self, states: list[State]) -> np.ndarray:
        images = []
        valid_acts = []
        for s in states:
            images.append(s.to_image())
            valid_acts.append(self._make_valid_mask(s))
        if self.dueling:
            return self.model.predict(
                [
                    np.array(images),
                    np.array(valid_acts),
                ],
                verbose=0,
            )
        else:
            return self.model.predict(np.array(images), verbose=0)

    def q_target_values_list(self, states: list[State]) -> np.ndarray:
        images = []
        valid_acts = []
        for s in states:
            images.append(s.to_image())
            valid_acts.append(self._make_valid_mask(s))
        if self.dueling:
            return self.target.predict(
                [np.array(images), np.array(valid_acts)], verbose=0
            )
        else:
            return self.target.predict(np.array(images), verbose=0)

    def create_train_data_multistep(self, minibatch: list[Experiences]):
        xs = []
        ys = []
        x_mask = []
        if self.double:
            pass
        else:
            states = [
                [] for _ in range(minibatch[0].length + 1)
            ]  # states[t][i] 経験iの時刻tの状態
            for exps in minibatch:
                for t, s in enumerate(exps.states):
                    states[t].append(s)
            q_values = []  # q_values[t][i]経験iの時刻tのq values
            for ss in states:
                q_values.append(self.q_values_list(ss))
            for i, exps in enumerate(minibatch):
                s_origin = exps.states[0]  # s_t
                xs.append(s_origin.to_image())
                x_mask.append(self._make_valid_mask(s_origin))
                valid_acts = OthelloEnv.valid_actions(s_origin)
                y = q_values[0][i]
                target_y_value = 0
                for t, (r, s, a) in enumerate(
                    zip(exps.rewards, exps.states[1:], exps.actions[1:] + [None])
                ):
                    act_value = (
                        0
                        if a is not None
                        else np.amax(
                            [
                                v if i in valid_acts else -2
                                for i, v in enumerate(q_values[t][i])
                            ]
                        )
                    )
                    if s_origin.color == s.color:
                        target_y_value += r + act_value
                    else:
                        target_y_value -= r + act_value
                y[exps.actions[0].index] = target_y_value
                ys.append(y)
        return xs, ys, x_mask

    def create_train_data(self, minibatch: list[Experience]):
        x = []
        y = []
        states = []
        next_states = []
        x_mask = []
        for exp in minibatch:
            states.append(exp.state)
            next_states.append(exp.next_state)
            x_mask.append(self._make_valid_mask(exp.state))
        y_next = self.q_values_list(next_states)
        if self.double:
            y_next_target = self.q_target_values_list(next_states)
        target_ys = self.q_values_list(states)

        for i, exp in enumerate(minibatch):
            if not exp.done:
                nx_valid = {a.index for a in OthelloEnv.valid_actions(exp.next_state)}
                if self.double:
                    best_nx_act = np.argmax(
                        [v if i in nx_valid else -2 for i, v in enumerate(y_next[i])]
                    )
                    nx_act_value = y_next_target[i][best_nx_act]
                else:
                    nx_act_value = np.amax(
                        [v if i in nx_valid else -2 for i, v in enumerate(y_next[i])]
                    )
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
        return x, y, x_mask

    def train(self, minibatch: list[Experience]):
        if self.multistep:
            x, y, x_mask = self.create_train_data_multistep(minibatch)
        else:
            x, y, x_mask = self.create_train_data(minibatch)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        if self.pb_epsilon > self.pb_epsilon_min:
            self.pb_epsilon *= self.pb_epsilon_decay
        if self.dueling:
            self.model.fit(
                [np.array(x), np.array(x_mask)], np.array(y), epochs=1, verbose=1
            )
        else:
            self.model.fit(np.array(x), np.array(y), epochs=1, verbose=1)

    def _make_valid_mask(self, state: State):
        mask = np.zeros((SIZE * SIZE, 1))
        for a in OthelloEnv.valid_actions(state):
            mask[a.index, 0] = 1
        return mask

    def act(self, state: State) -> Action:
        if np.random.rand() <= self.epsilon:
            return random.choice(OthelloEnv.valid_actions(state))
        valid = {action.index for action in OthelloEnv.valid_actions(state)}
        q_values = self.q_values(state)
        filtered = np.array([v if i in valid else -1 for i, v in enumerate(q_values)])
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

    def q_values(self, state: State) -> list[float]:
        return self.q_values_list([state])[0]

    def Q(self, state: State, action: Action):
        return self.q_values(state)[action.index]

    def V(self, state: State) -> float:
        policy = self.q_values(state)
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


class SimpleMemory:
    def __init__(self, maxlen: int) -> None:
        self.memory = deque(maxlen=maxlen)

    def length(self):
        return len(self.memory)

    def add(self, transiton_batch: list[Experience]):
        self.memory.extend(transiton_batch)

    def sample(self, n):
        return random.choices(self.memory, k=n)


class SimpleMultiStepMemory:
    def __init__(self, maxlen: int) -> None:
        self.memory = deque[Experiences](maxlen=maxlen)

    def length(self):
        return len(self.memory)

    def add(self, transiton_batch: list[Experiences]):
        self.memory.extend(transiton_batch)

    def sample(self, n) -> list[Experiences]:
        return random.choices(self.memory, k=n)


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
        self.rate_decay_max = 1.0

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
