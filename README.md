BÁO CÁO ĐỒ ÁN MÔN HỌC
(Đồ án phát triển ứng dụng)
Lớp: IT003.Q21.CTTN

SINH VIÊN THỰC HIỆN
Mã sinh viên:25520228	Họ và tên: Quách Cường

---

### Cây tứ phân (Quadtree)


```python
"""
Define: _subdivide(self)
In/Args: self
Out/Returns: None
Purpose: Phân chia node Quadtree hiện tại thành 4 node con (4 góc phần tư: Top-Left, Top-Right, Bottom-Left, Bottom-Right) khi mảng chứa đối tượng (objects) đã đạt giới hạn sức chứa (capacity).
Last modify,When: 29/04/2026
"""

"""
Define: _get_child_index(self, rect)
In/Args: 
    - self
    - rect (pygame.Rect): Khung giới hạn của đối tượng cần kiểm tra.
Out/Returns: int (Giá trị từ 0 đến 3 tương ứng với index của node con, hoặc -1 nếu đối tượng nằm vắt ngang giữa các ranh giới).
Purpose: Xác định xem một đối tượng hình chữ nhật có nằm trọn vẹn bên trong một trong 4 góc phần tư của Quadtree hay không để tiến hành phân bổ.
Last modify,When: 29/04/2026
"""

"""
Define: insert(self, obj)
In/Args: 
    - self
    - obj: Đối tượng cần chèn (yêu cầu có thuộc tính .rect).
Out/Returns: bool (True nếu chèn thành công, False nếu đối tượng không nằm trong ranh giới của node này).
Purpose: Thêm một đối tượng vào cấu trúc không gian Quadtree. Hàm sử dụng đệ quy để đẩy đối tượng xuống các node con sâu hơn nếu có thể, giúp phân loại vị trí không gian chính xác.
Last modify,When: 29/04/2026
"""

"""
Define: query(self, area, found=None)
In/Args: 
    - self
    - area (pygame.Rect): Vùng không gian cần truy vấn va chạm.
    - found (list): Danh sách lưu trữ các đối tượng tìm thấy (mặc định là None, dùng cho đệ quy).
Out/Returns: list (Danh sách các đối tượng nằm bên trong hoặc có giao cắt với vùng 'area').
Purpose: Truy vấn và trả về tập hợp con các đối tượng có khả năng xảy ra va chạm trong một khu vực nhất định. Hàm này là cốt lõi để thu hẹp phạm vi kiểm tra va chạm.
Last modify,When: 29/04/2026
"""
