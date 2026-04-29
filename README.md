BÁO CÁO ĐỒ ÁN MÔN HỌC
(Đồ án phát triển ứng dụng)
Lớp: IT003.Q21.CTTN

SINH VIÊN THỰC HIỆN
Mã sinh viên:25520228	Họ và tên: Quách Cường

---

```python
"""
Define: Quadtree 
In/Args: 
    - obj: Đối tượng cần thêm vào cây .
    - area (pygame.Rect): Khung giới hạn dùng để truy vấn không gian.
    Purpose: Cấu trúc dữ liệu phân chia không gian 2D thành các góc tứ phân (Top-Left, Top-Right, Bottom-Left, Bottom-Right) để tối ưu hóa việc quản lý vị trí thực thể. Tự động chia nhỏ node khi đầy và cho phép truy vấn nhanh các đối tượng.
Last modify,When: 29/04/2026
"""

"""
Define: Object Pool 
In/Args: 
    - size (int): Số lượng thực thể (đạn) được tạo sẵn trong bộ nhớ.
    Purpose:  tối ưu hóa bộ nhớ và hiệu suất trò chơi. Hệ thống khởi tạo sẵn một lượng đạn cố định vào hàng đợi hai đầu (deque). Khi bắn, lấy đạn ra dùng (popleft O(1)), và trong quá trình update, nếu đạn ra khỏi màn hình hoặc trúng mục tiêu sẽ lập tức thu hồi lại vào hàng đợi (append O(1)).
Last modify,When: 29/04/2026
"""
