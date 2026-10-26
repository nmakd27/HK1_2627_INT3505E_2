## 5 điểm có thể rò rỉ / lỗ hổng bảo mật:

### 1. Rò rỉ thông tin xác thực qua URL / Query Parameters (Auth in Query String)

* **Mô tả lỗ hổng:** Truyền `access_token`, `refresh_token`, hoặc `api_key` trực tiếp trên URL Query String.
* **Nguy cơ rò rỉ:** URL chứa token sẽ bị lưu vết tại nhiều nơi không an toàn:
    * Access Log của Web Server
    * Lịch sử duyệt web
    * Header `Referer` khi chuyển hướng sang trang bên thứ ba
* **Biện pháp khắc phục:** Luôn truyền Token qua HTTP Header `Authorization: Bearer <token>` hoặc dùng Cookie `HttpOnly; Secure; SameSite=Strict`.

### 2. Lưu trữ JWT Token ở `localStorage` trên Frontend
* **Mô tả lỗ hổng:** Lưu Access Token và Refresh Token trong `window.localStorage` hoặc `sessionStorage` ở Single Page Application.
* **Nguy cơ rò rỉ:** Mọi mã JavaScript chạy trong trang web (bao gồm cả các thư viện npm bên thứ ba hoặc kịch bản XSS bị tiêm vào) đều có thể đọc `localStorage.getItem('token')` và gửi về máy chủ của kẻ tấn công.
* **Biện pháp khắc phục:** 
    * Lưu trữ Refresh Token trong **Cookie `HttpOnly`, `Secure`, `SameSite=Strict`** để JavaScript không thể đọc được
    * Lưu Access Token ngắn hạn (15 phút) trong bộ nhớ ứng dụng (In-Memory variable / React Context)

### 3. Lỗi phân quyền cấp đối tượng (BOLA)
* **Mô tả lỗ hổng:** Endpoint `GET /posts/{id}` chỉ kiểm tra người dùng đã đăng nhập (Token hợp lệ), nhưng **không kiểm tra mối quan hệ sở hữu/quyền riêng tư** đối với bài viết có `id` tương ứng.
* **Nguy cơ rò rỉ:** Kẻ tấn công có thể thay đổi `{id}` trên URL (Insecure Direct Object Reference) để đọc bài viết riêng tư (*Private/Friends-only*) của người dùng khác.
* **Biện pháp khắc phục:** Thực hiện **3-layer check** tại backend:
    1. AuthN (Token hợp lệ, chưa bị revoke)
    2. AuthZ Scope (Có scope `posts:read`)
    3. **Ownership/Access Policy Check**: Kiểm tra DB xem `post.is_private` và `post.author_id == current_user.id` hoặc `current_user` có trong danh sách bạn bè hay không

### 4. Lỗi gán thuộc tính hàng loạt & Lộ dữ liệu nhạy cảm (Broken Object Property Level Authorization / Mass Assignment)
* **Mô tả lỗ hổng:**
    * Trả về toàn bộ dòng bản ghi DB trong Response API
    * Cho phép người dùng gửi JSON payload tự cập nhật các trường quản trị như `is_admin: true` hoặc `role: "admin"`
* **Nguy cơ rò rỉ:** Lộ thông tin nhạy cảm của người dùng (password hash) hỗ trợ kẻ tấn công bẻ khóa offline; hoặc bị leo quyền quản trị (privilege escalation).
* **Biện pháp khắc phục:**
    * Sử dụng DTO / Serializer để whitelist chính xác các trường trả về client. Không bao giờ echo raw DB row
    * Whitelist các trường được phép cập nhật ở `requestBody`

### 5. Quản lý vòng đời Refresh Token kém & Không có Token Rotation / Revocation List
* **Mô tả lỗ hổng:** Refresh Token có thời hạn quá dài (ví dụ: 30–90 ngày) nhưng không áp dụng cơ chế **Refresh Token Rotation** và không có danh sách thu hồi (**Revocation Blocklist**).
* **Nguy cơ rò rỉ:** Nếu Refresh Token bị đánh cắp, kẻ tấn công có thể liên tục gọi `POST /auth/refresh` để lấy Access Token mới trong nhiều tháng mà người dùng không thể làm gì được kể cả khi đã đổi mật khẩu.
* **Biện pháp khắc phục:**
    * Áp dụng **Refresh Token Rotation**: Mỗi khi gọi `POST /auth/refresh`, hủy ngay Refresh Token cũ và cấp một cặp `{access_token, refresh_token}` hoàn toàn mới
    * Nếu phát hiện một Refresh Token cũ đã bị sử dụng lại, vô hiệu hóa toàn bộ token family của phiên đó
    * Lưu trữ `jti` (JWT ID) của token bị thu hồi trên Redis với TTL bằng thời hạn còn lại của token.