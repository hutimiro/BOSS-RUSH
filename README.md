BÁO CÁO ĐỒ ÁN MÔN HỌC
(Đồ án phát triển ứng dụng)
Lớp: IT003.Q21.CTTN

SINH VIÊN THỰC HIỆN
Mã sinh viên:25520228	Họ và tên: Quách Cường

---

```python
"""
		"""
        Define: Cập nhật vị trí và hướng bay tự nhắm của đạn (Homing Bullet)
        In/Args: 
            - self: Khởi tạo đối tượng đạn
            - target: Mục tiêu cần nhắm tới 
        Out/Returns: không 
        Purpose: Ứng dụng toán Vector để tạo đạn tự nhắm. Thuật toán tính toán khoảng 
                 cách (dist) và vector hướng đi (dir_x, dir_y) giữa đạn và mục tiêu. 
                 Sau đó, áp dụng một hệ số bẻ lái (homing_power).
        Last modify: 20/4/2026 
        """
        
        
        
        """
        Define: Khởi tạo hồ chứa đạn (Object Pool)
        In/Args: 
            - size (int): Số lượng đạn tối đa được cấp phát sẵn trong bộ nhớ.
        Out/Returns: Không 
        Purpose: Tránh việc liên tục cấp phát và thu hồi bộ nhớ (tạo/xóa object) làm 
                 giảm FPS. Ứng dụng `collections.deque` (hàng đợi hai đầu) hoạt động 
                 như một Danh sách liên kết (Linked List). Khi cần đạn, popleft() lấy 
                 nhanh đạn rảnh với độ phức tạp O(1). Khi đạn bay ra ngoài hoặc nổ, 
                 nó được append() trả lại pool để tái sử dụng.
        Last modify: 21/4/2026
        """
        
        
        
        """
		Define: Cấu trúc dữ liệu phân chia không gian 2D để tối ưu va chạm
		In/Args: 
			- bounds (pygame.Rect): Khung giới hạn không gian hiện tại của node
			- capacity (int): Số lượng vật thể tối đa trước khi node phải tự chia nhỏ
			- max_depth (int): Độ sâu tối đa của cây để tránh đệ quy vô hạn
			- depth (int): Độ sâu hiện tại của node
		Out/Returns: Một đối tượng Quadtree chứa danh sách đạn ở vùng không gian tương ứng
		Purpose: Thay vì dùng O(N^2) để so sánh mọi viên đạn với nhau, Quadtree chia màn 
				hình thành 4 góc. giúp game giữ FPS cao.
		Last modify: 26/4/2026
		"""
    
    
    
    """
        Define: Vòng lặp cập nhật đạn boss và xử lý đạn con sinh ra
        In/Args:
            - current_time (int): Thời gian hiện tại của game
        Out/Returns: None
        Purpose: Xử lý cơ chế sinh đạn nhổ  
                 Thuật toán sử dụng mảng tạm thời `spawned_bullets` đóng vai trò 
                 như một Hàng đợi (Queue). Khi đạn mẹ phát nổ, đạn con được xếp 
                 vào hàng đợi này và chờ đến cuối vòng lặp mới được giải phóng 
                 vào pool. 
        Last modify: 26/4/2026
        """
        
        
        """
		Define: Boss với nhiều giai đoạn chiến đấu (Phases)
		In/Args: từ BaseBoss, nhận các thông số tọa độ, máu, sprite.
		Out/Returns: Boss có khả năng tự thay đổi hành vi tấn công
		Purpose: Ứng dụng mô hình State Machine đơn giản. Biến 
				 `self.phase` chính là State hiện tại. Tùy thuộc vào việc Boss đang ở Phase 1 
				 hay Phase 2, hàm `update` và `shoot` sẽ rẽ nhánh để áp dụng quy luật 
				 di chuyển mới (thay vì đứng im thì lướt trái/phải)
		Last modify: 10/5/2026
		"""
		
		
		
		"""
		Define: Cấu trúc điều phối lịch trình sự kiện trong game
		In/Args: Không có tham số khởi tạo tĩnh, quản lý bộ nhớ đệm `_events`
		Out/Returns: Trả về instance của hàng đợi sự kiện
		Purpose: Quản lý thứ tự chuyển đổi State của game (Chơi -> Nâng cấp -> Màn Mới). 
				 Áp dụng cấu trúc Hàng đợi ưu tiên (Priority Queue). Bằng cách push 
				 sự kiện dựa trên khi nào thì sự kiện được phép kích hoạt
				 và mức độ ưu tiên , game loop có thể 
				 bốc chính xác luồng sự kiện tiếp
		Last modify: 11/5/2026
		"""
"""
