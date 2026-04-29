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
```

Object Pool (Hàng đợi Deque)

Mẫu thiết kế Object Pool kết hợp với cấu trúc dữ liệu Hàng đợi hai đầu (collections.deque) được sử dụng để quản lý vòng đời của đạn, tránh việc cấp phát (allocate) và giải phóng (deallocate) bộ nhớ liên tục gây sụt giảm khung hình.
```python
"""
Define: __init__(self, size)
In/Args: 
    - self
    - size (int): Kích thước tối đa của hồ chứa đạn.
Out/Returns: None
Purpose: Khởi tạo cấu trúc dữ liệu hàng đợi hai đầu (collections.deque) để chứa sẵn các object đạn nhằm tái sử dụng liên tục. 
Last modify,When: 29/04/2026
"""

"""
Define: get_bullet(self, x, y, dx, dy, ...)
In/Args: 
    - self
    - x, y, dx, dy...: Các tham số cấu hình trạng thái ban đầu của viên đạn.
Out/Returns: None
Purpose: Lấy một viên đạn đang "rảnh" từ đầu hàng đợi (độ phức tạp O(1) với popleft) ra để sử dụng, cập nhật trạng thái hoạt động (active = True) và đưa vào danh sách đang bay.
Last modify,When: 29/04/2026
"""

"""
Define: update(self, target=None)
In/Args: 
    - self
    - target: Mục tiêu truyền vào (dùng cho các loại đạn có chức năng tự nhắm).
Out/Returns: None
Purpose: Duyệt qua các viên đạn đang bay để cập nhật vị trí. Nếu đạn tắt (ra khỏi màn hình hoặc trúng mục tiêu), hàm sẽ tự động thu hồi và đẩy lại vào cuối hàng đợi (độ phức tạp O(1) với append) để chờ tái sử dụng.
Last modify,When: 29/04/2026
"""
```
