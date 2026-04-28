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
- **In/Args:** `surface` (pygame.Surface), `target` (BaseBoss)
- **Out/Returns:** `None`
- **Purpose:** Duyệt qua các đạn đang hoạt động. Nếu đạn hết hiệu lực (ra khỏi màn hình), lập tức loại bỏ khỏi danh sách hiển thị và đẩy ngược lại vào cuối hàng đợi pool (`append`) với $O(1)$ để chờ tái sử dụng.
- **Last modify, When:** 28/04/2026

### `clear(self)`
- **Define:** Dọn dẹp toàn bộ đạn đang bay.
- **In/Args:** `None`
- **Out/Returns:** `None`
- **Purpose:** Duyệt và thu hồi đồng loạt toàn bộ đạn đang hoạt động về lại cuối hàng đợi (`append`), sau đó làm rỗng danh sách active để reset trạng thái (thường dùng khi chuyển màn).
- **Last modify, When:** 28/04/2026

---

## 2. Class `EnemyBulletPool` (Triển khai Object Pool bằng Deque)

Tương tự như `BulletPool`, nhưng được thiết kế riêng để xử lý số lượng đạn khổng lồ (Bullet Hell) từ Boss.

### `__init__(self, size)`
- **Define:** Khởi tạo Object Pool cho đạn của Boss.
- **In/Args:** `size` (int) - kích thước pool.
- **Out/Returns:** `None`
- **Purpose:** Tạo sẵn một `deque` chứa các EnemyBullet tĩnh. Rất quan trọng để duy trì FPS ổn định khi Boss bắn ra lượng đạn khổng lồ.
- **Last modify, When:** 28/04/2026

### `get_bullet(self, x, y, dx, dy, bounces=0, size=10, damage=1)`
- **Define:** Lấy đạn Boss từ pool.
- **In/Args:** `x` (float), `y` (float), `dx` (float), `dy` (float), `bounces` (int), `size` (int), `damage` (int)
- **Out/Returns:** `None`
- **Purpose:** Trích xuất phần tử từ đầu queue (`popleft`) trong $O(1)$, thiết lập các vector vận tốc, số lần nảy tường và đưa vào list hoạt động.
- **Last modify, When:** 28/04/2026

### `update_and_draw(self, surface)`
- **Define:** Cập nhật logic nảy tường và thu hồi đạn Boss.
- **In/Args:** `surface` (pygame.Surface)
- **Out/Returns:** `None`
- **Purpose:** Duyệt tính toán quỹ đạo. Khi đạn bay vượt biên giới màn hình, thực hiện thao tác trả object về cuối queue rảnh (`append`) với độ phức tạp thời gian $O(1)$.
- **Last modify, When:** 28/04/2026

### `clear(self)`
- **Define:** Xóa toàn bộ đạn Boss trên màn hình.
- **In/Args:** `None`
- **Out/Returns:** `None`
- **Purpose:** Đẩy tất cả EnemyBullet đang bay về lại mảng rảnh (queue) và dọn dẹp list đạn đang bay để tạo vùng an toàn khi người chơi tiêu diệt xong Boss.
- **Last modify, When:** 28/04/2026

---

## 3. Class `BossRush` (Triển khai duyệt phần tử tuần tự trên Mảng)

Sử dụng cấu trúc dữ liệu mảng (Array/List) để quản lý thứ tự xuất hiện của các Boss và tiến trình của người chơi.

### `__init__(self, bosses)`
- **Define:** Khởi tạo bộ quản lý danh sách Boss.
- **In/Args:** `bosses` (list) - mảng chứa các object Boss.
- **Out/Returns:** `None`
- **Purpose:** Lưu trữ danh sách Boss dưới dạng mảng (Array/List) và khởi tạo con trỏ chỉ mục (`current_index = 0`) để quản lý tiến trình duyệt qua từng Boss trong game.
- **Last modify, When:** 28/04/2026

### `advance_to_next_boss(self, current_time)`
- **Define:** Chuyển trạng thái sang Boss tiếp theo.
- **In/Args:** `current_time` (int)
- **Out/Returns:** `None`
- **Purpose:** Tịnh tiến con trỏ chỉ mục (`current_index += 1`) để trỏ tới phần tử tiếp theo trong mảng, mô phỏng cơ chế duyệt tuyến tính (linear traversal) của cấu trúc dữ liệu mảng.
- **Last modify, When:** 28/04/2026
