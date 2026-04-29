BÁO CÁO ĐỒ ÁN MÔN HỌC
(Đồ án phát triển ứng dụng)
Lớp: IT003.Q21.CTTN

SINH VIÊN THỰC HIỆN
Mã sinh viên:25520228	Họ và tên: Quách Cường

---

```python
"""
Define: Quadtree (Class & Core Methods: _subdivide, _get_child_index, insert, query)
In/Args: 
    - obj: Đối tượng cần thêm vào cây (yêu cầu có thuộc tính .rect).
    - area (pygame.Rect): Khung giới hạn dùng để truy vấn không gian.
Out/Returns: list (Danh sách các đối tượng nằm trong vùng truy vấn) hoặc bool (Trạng thái chèn đối tượng thành công/thất bại).
Purpose: Cấu trúc dữ liệu phân chia không gian 2D thành các góc tứ phân (Top-Left, Top-Right, Bottom-Left, Bottom-Right) để tối ưu hóa việc quản lý vị trí thực thể. Tự động chia nhỏ node khi đầy và cho phép truy vấn nhanh các đối tượng có khả năng va chạm trong một khu vực cụ thể, giúp giảm thiểu số lượng phép toán từ O(n^2) xuống xấp xỉ O(n log n).
Last modify,When: 29/04/2026
"""

"""
Define: Object Pool (BulletPool / EnemyBulletPool & Core Methods: __init__, get_bullet, update)
In/Args: 
    - size (int): Số lượng thực thể (đạn) được tạo sẵn trong bộ nhớ.
    - x, y, dx, dy, target...: Các tham số cấu hình trạng thái ban đầu và định hướng cho đạn.
Out/Returns: None (Thao tác quản lý trạng thái trực tiếp trên collections.deque và list nội bộ).
Purpose: Mẫu thiết kế tối ưu hóa bộ nhớ và hiệu suất trò chơi. Hệ thống khởi tạo sẵn một lượng đạn cố định vào hàng đợi hai đầu (deque). Khi bắn, lấy đạn "rảnh" ra dùng (popleft O(1)), và trong quá trình update, nếu đạn ra khỏi màn hình hoặc trúng mục tiêu sẽ lập tức thu hồi lại vào hàng đợi (append O(1)). Cơ chế này triệt tiêu hoàn toàn độ trễ do việc cấp phát (allocate) và dọn rác (garbage collection) liên tục gây ra.
Last modify,When: 29/04/2026
"""
