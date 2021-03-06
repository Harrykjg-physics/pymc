import numpy as np
from tqdm import tqdm
import cupy


class MetroCupy(object):
    def metropolis_cupy(self, iter, T, cp, show_tqdm):
        be = 1.0 / T

        if show_tqdm:
            iterable = tqdm(range(iter))
        else:
            iterable = range(iter)

        acc = 0
        act = 0
        np.random.random()

        temp_H_cupy = cupy.asarray(self.H)
        eigv = cupy.linalg.eigvalsh(temp_H_cupy)
        E0 = -T*cupy.sum(cupy.log(cupy.add(cupy.exp((cp-eigv)*be), 1)))

        temp_empty = list(self.empty_sites)
        temp_filled = list(self.filled_sites)

        for _ in iterable:
            ch_empty = np.random.choice(temp_empty)
            ch_filled = np.random.choice(temp_filled)

            temp_H_cupy[ch_empty, ch_empty] = self.U
            temp_H_cupy[ch_filled, ch_filled] = 0.0

            eigv = cupy.linalg.eigvalsh(temp_H_cupy)
            E = -T*cupy.sum(cupy.log(cupy.add(cupy.exp((cp-eigv)*be), 1)))

            if E <= E0:
                E0 = E
                temp_filled.remove(ch_filled)
                temp_empty.remove(ch_empty)
                temp_empty.append(ch_filled)
                temp_filled.append(ch_empty)
                acc += 1

            elif np.exp((E0-E)*be) >= np.random.random_sample():
                E0 = E
                temp_filled.remove(ch_filled)
                temp_empty.remove(ch_empty)
                temp_empty.append(ch_filled)
                temp_filled.append(ch_empty)
                act += 1
            else:
                temp_H_cupy[ch_empty, ch_empty] = 0.0
                temp_H_cupy[ch_filled, ch_filled] = self.U

        self.empty_sites = set(temp_empty)
        self.filled_sites = set(temp_filled)

        self.H = temp_H_cupy.get()
        print(self.get_F(T, cp))
        return {"E": E0, "acc": acc/iter, "act": act/iter}
