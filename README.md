BÁO CÁO ĐỒ ÁN MÔN HỌC
(Đồ án phát triển ứng dụng)
Lớp: IT003.Q21.CTTN

SINH VIÊN THỰC HIỆN
Mã sinh viên:25520228	Họ và tên: Quách Cường

---

## 1. Class `BulletPool` (Triển khai Object Pool bằng Deque)

Kỹ thuật Object Pool sử dụng Hàng đợi hai đầu (`collections.deque`) để quản lý vòng đời của đạn người chơi, giúp tránh tình trạng cấp phát và thu hồi bộ nhớ liên tục gây giật lag.

### `__init__(self, size)`
- **Define:** Khởi tạo hồ chứa đạn (Object Pool).
- **In/Args:** `size` (int) - số lượng đạn tối đa trong pool.
- **Out/Returns:** `None`
- **Purpose:** Khởi tạo cấu trúc dữ liệu hàng đợi hai đầu (`collections.deque`) chứa các object đạn được tạo sẵn. Kỹ thuật này giúp tối ưu hóa bộ nhớ và tránh overhead của việc cấp phát/thu hồi object liên tục trong game loop.
- **Last modify, When:** 28/04/2026

### `get_bullet(self, x, y, dx=0.0, dy=None, homing=False, damage=15)`
- **Define:** Lấy một viên đạn từ pool để sử dụng.
- **In/Args:** `x` (float), `y` (float), `dx` (float), `dy` (float), `homing` (bool), `damage` (int)
- **Out/Returns:** `None`
- **Purpose:** Rút một object Bullet nhàn rỗi từ đầu hàng đợi (`popleft`) với độ phức tạp $O(1)$, kích hoạt thông số và đẩy vào danh sách đạn đang bay.
- **Last modify, When:** 28/04/2026

### `update_and_draw(self, surface, target=None)`
- **Define:** Cập nhật vòng đời và thu hồi đạn.
- **In/Args:**
