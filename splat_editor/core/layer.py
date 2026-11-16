import math
import os
import numpy as np

from ..io.codec import SplatCodec
from ..io.ply import PlyFile
from . import sh
from .math3d import matrix_to_quat, quat_mul
from .splats import Splats
from .transform import Transform

FLIP = np.diag([-1.0, -1.0, 1.0])
CHUNK = 1 << 20


class Layer:
    def __init__(self, name, data, path=None):
        self.name = name
        self.path = path
        self.data = data                                     # dữ liệu gốc (để lưu lại đủ mọi thuộc tính), thường là memmap
        self.splats = SplatCodec.decode(data)
        self.selection = np.zeros(self.splats.count, bool)   # gaussian đang được chọn (cọ), không bao giờ gồm cái đã xoá
        self.deleted = np.zeros(self.splats.count, bool)     # gaussian đã xoá (xoá mềm)
        self.deleted_count = 0
        self.visible = True
        self.transform = Transform()

    @classmethod
    def from_file(cls, path):
        return cls(os.path.basename(path), PlyFile.read(path), path)

    @property
    def size(self):
        """Số hàng của mảng dữ liệu, kể cả gaussian đã xoá."""
        return self.splats.count

    @property
    def count(self):
        """Số gaussian còn lại (chưa xoá)."""
        return self.size - self.deleted_count

    def live_rows(self, rows=slice(None)):
        """Chỉ số (trong toàn mảng) các gaussian chưa xoá thuộc đoạn `rows`."""
        start = rows.start or 0
        return np.flatnonzero(~self.deleted[rows]) + start

    # ------------------------------------------------------------------ vùng chọn
    @property
    def selected_count(self):
        return int(np.count_nonzero(self.selection))

    def select_all(self):
        np.logical_not(self.deleted, out=self.selection)

    def clear_selection(self):
        self.selection[:] = False

    def invert_selection(self):
        self.selection = ~(self.selection | self.deleted)

    def delete_selected(self):
        """Xoá (mềm) các gaussian đang chọn. Trả về chỉ số các gaussian đã xoá (để hoàn tác), hoặc
        None nếu không có gì."""
        indices = np.flatnonzero(self.selection)
        if len(indices) == 0:
            return None
        self.deleted[indices] = True
        self.selection[indices] = False
        self.deleted_count += len(indices)
        return indices

    def restore(self, indices):
        """Hoàn tác delete_selected: các gaussian `indices` hiện lại và được chọn lại như lúc xoá."""
        self.deleted[indices] = False
        self.selection[indices] = True
        self.deleted_count -= len(indices)

    # ------------------------------------------------------------------ biến đổi
    def world_transform(self, flip):
        """(A, t, s): p_thế_giới = s * A @ p_file + t, với A = R * F là phép xoay thuần."""
        rot = self.transform.rotation_matrix() @ (FLIP if flip else np.identity(3))
        return rot, self.transform.translation(), float(self.transform.scale)

    def world_matrix(self, flip):
        """Ma trận 4x4: p_thế_giới = M @ (p_file, 1). Renderer / LOD / cọ dùng ma trận này với dữ liệu
        toạ độ file, nên đổi phép biến đổi không phải tính lại hay gửi lại dữ liệu."""
        rot, t, s = self.world_transform(flip)
        m = np.identity(4)
        m[:3, :3] = s * rot
        m[:3, 3] = t
        return m

    def world_splats(self, flip):
        """Các gaussian còn lại ở toạ độ thế giới."""
        rot, t, s = self.world_transform(flip)
        sp = self.splats if self.deleted_count == 0 else self.splats.subset(~self.deleted)
        n = sp.count
        positions = np.empty((n, 3), np.float32)
        rotations = np.empty((n, 4), np.float32)
        q_rot = matrix_to_quat(rot).astype(np.float32)
        m, t = (s * rot).astype(np.float32), t.astype(np.float32)
        for a in range(0, n, CHUNK):
            positions[a:a + CHUNK] = sp.positions[a:a + CHUNK] @ m.T + t
            rotations[a:a + CHUNK] = quat_mul(q_rot, sp.rotations[a:a + CHUNK])
        identity = np.allclose(rot, np.identity(3), atol=1e-9)
        return Splats(positions=positions, colors=sp.colors, alphas=sp.alphas,
                      scales=sp.scales if s == 1.0 else (sp.scales * np.float32(s)),
                      rotations=rotations, sh_rest=sp.sh_rest,
                      sh_frames=() if identity or sp.sh_count == 0 else ((0, n, rot),))

    def export_blocks(self, flip, dtype):
        """Dữ liệu của lớp sau khi áp phép biến đổi, đổi về toạ độ file, theo kiểu `dtype`,
        trả về từng khối CHUNK hàng (để ghi file mà không giữ cả lớp trong RAM)."""
        for a in range(0, self.size, CHUNK):
            rows = slice(a, a + CHUNK) if self.deleted_count == 0 else self.live_rows(slice(a, a + CHUNK))
            yield self._export_block(rows, flip, dtype)

    def export_data(self, flip, dtype):
        """Toàn bộ dữ liệu của lớp sau khi biến đổi (xem export_blocks)."""
        blocks = list(self.export_blocks(flip, dtype))
        return np.concatenate(blocks) if blocks else np.zeros(0, dtype)

    def _export_block(self, rows, flip, dtype):
        rot, t, s = self.world_transform(flip)
        back = FLIP if flip else np.identity(3)
        rot, t = back @ rot, back @ t            # toạ độ thế giới -> toạ độ file
        src = np.asarray(self.data[rows])
        if src.dtype != dtype:
            src = SplatCodec.encode(src, self.splats.subset(rows), dtype)
        out = src.copy()
        names = dtype.names

        p = np.stack([src['x'], src['y'], src['z']], axis=1).astype(np.float64)
        out['x'], out['y'], out['z'] = (p @ (s * rot).T + t).T
        if {'nx', 'ny', 'nz'} <= set(names):
            n = np.stack([src['nx'], src['ny'], src['nz']], axis=1).astype(np.float64)
            out['nx'], out['ny'], out['nz'] = (n @ rot.T).T
        if 'scale_0' in names and s != 1.0:
            for i in range(3):
                out[f'scale_{i}'] = src[f'scale_{i}'] + math.log(s)
        if 'rot_0' in names:
            q = np.stack([src[f'rot_{i}'] for i in range(4)], axis=1).astype(np.float64)
            q = quat_mul(matrix_to_quat(rot), q)
            for i in range(4):
                out[f'rot_{i}'] = q[:, i]
        coeffs = sh.from_columns(src, names)
        if coeffs.shape[1]:
            sh.to_columns(sh.rotate(coeffs, rot), out)
        return out
