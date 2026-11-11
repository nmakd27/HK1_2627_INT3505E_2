### **Câu 1: Trong 3 kịch bản, kịch bản nào có p95 cao nhất? Vì sao?**
* **Trả lời:** **Kịch bản C (Spike Test - 200 Users)** có chỉ số p95 cao nhất (**2,900 ms**, với Max latency vọt lên **3,754 ms**).
* **Giải thích nguyên nhân:**
  1. **Đột biến số lượng kết nối đồng thời:** Ở Kịch bản C, spawn rate là 50 users/giây đẩy nhanh số concurrent users lên 200 chỉ trong vài giây. Flask và Thread Pool bị quá tải dẫn tới nghẽn hàng chờ request.
  2. **Độ trễ tích tụ (Latency Tail Degradation):** Các request nằm ở p95 phải xếp hàng chờ giải phóng worker process/thread khiến thời gian phản hồi tăng thêm ~800 ms so với Baseline (từ 2,100 ms lên 2,900 ms).


### **Câu 2: Có endpoint nào fail rate tăng theo số user? Đoán nguyên nhân dựa trên code.**
* **Trả lời & Phân tích nguyên nhân:**
  1. **Tỷ lệ lỗi trên `GET /books/{id}` (69 failures ở Kịch bản B - 33.5%):**
     * **Nguyên nhân:** Kịch bản test sử dụng `random.randint(1, 100)` để truy cập sách ngẫu nhiên, tuy nhiên CSDL thử nghiệm chỉ chứa một số lượng bản ghi hạn chế. Khi số lượng user tăng lên 50, lượng request sinh ID ngẫu nhiên không tồn tại tăng tương ứng, làm tăng số lượng HTTP `404 Not Found`.
  2. **Tỷ lệ lỗi trên `GET /books?year=search` (1 failure ở Kịch bản B):**
     * **Nguyên nhân:** Do kịch bản trong `locustfile.py` chủ động cài đặt logic ngẫu nhiên với xác suất 1% ra lỗi giả lập `CatchResponseError` (mô phỏng server error 500). Khi tổng số request tăng, số lượng lỗi ghi nhận cũng tăng theo xác suất này.


### **Câu 3: Nếu Prod cần SLO p95 < 300ms (hoặc ngưỡng chuẩn SLO phù hợp), kịch bản nào đạt? Đề xuất baseline cho CI gate.**
* **Đánh giá SLO:**
  * Giả sử mục tiêu SLO tối thiểu chấp nhận được là **p95 <= 2,200 ms** (do ứng dụng thử nghiệm Flask dev server có độ trễ cơ sở khoảng 2,000 ms):
    * **Kịch bản A (Baseline)** và **Kịch bản B (Load Test)** đều **ĐẠT SLO** (p95 = 2,100 ms).
    * **Kịch bản C (Spike Test)** **KHÔNG ĐẠT SLO** (p95 = 2,900 ms > 2,200 ms).
* **Đề xuất Baseline cho CI/CD Quality Gate:**
  * **Kịch bản chọn cho CI:** Chạy tự động **Kịch bản B** (50 Users, Spawn Rate 5/s, Duration 60s).
  * **Ngưỡng Quality Gate (Pass/Fail criteria):**
    * `p95 Response Time <= 2,200 ms` (hoặc < 300 ms đối với hệ thống Production chuẩn chạy Gunicorn/Nginx).
    * `HTTP 5xx Fail Rate < 1.0%` (không tính các lỗi 404 do missing data).

---

### **Câu Hỏi Bonus: Nếu connection pool giới hạn là 5, điều gì xảy ra khi 200 user truy cập đồng thời? Làm thế nào để xác nhận bằng Locust?**

* **Hiện tượng xảy ra khi Connection Pool = 5 và Concurrent Users = 200:**
  1. **Nghẽn Connection Pool (Connection Pool Exhaustion):** Chỉ có tối đa 5 request được mở kết nối DB đồng thời để thực thi SQL query. 195 request còn lại bắt buộc phải xếp hàng chờ trong bộ đệm kết nối (Pool Queue).
  2. **Timeout & Lỗi HTTP 500 / 504:** Khi thời gian chờ vượt quá ngưỡng timeout của SQLAlchemy hoặc timeout của WSGI server, SQLAlchemy sẽ ném ra lỗi `TimeoutError: QueuePool limit of size 5 overflowed`, dẫn tới server trả về mã `500 Internal Server Error` hoặc `504 Gateway Timeout`.
  3. **Biến động Latency (Tail Latency Explodes):** Chỉ số p95 và p99 sẽ tăng vọt có thể lên tới hàng chục giây, chỉ số RPS bị tụt thảm hại do các thread bị block hoàn toàn.

* **Cách xác nhận bằng Locust:**
  1. **Cấu hình giới hạn Connection Pool trong Flask app (`app.py`):**
     ```python
     app.config['SQLALCHEMY_POOL_SIZE'] = 5
     app.config['SQLALCHEMY_MAX_OVERFLOW'] = 0
     # Không cho vượt quá 5 pool
     app.config['SQLALCHEMY_POOL_TIMEOUT'] = 3
     # Ép timeout ngắn (3 giây) để dễ quan sát
     ```
  2. **Chạy Locust kịch bản Spike Test (200 Users):**
     ```bash
     locust -f locustfile.py --headless -u 200 -r 50 -t 30s --html reports/pool_test.html
     ```
  3. **Kiểm tra chỉ số trên báo cáo Locust:**
     * **Cột `# fails`:** Tỷ lệ HTTP 500 tăng đột biến.
     * **Tab `Failures` / `Exceptions`:** Xuất hiện chuỗi lỗi `OperationalError` / `TimeoutError` liên quan đến `QueuePool limit of size 5 overflowed`.
     * **Biểu đồ Response Time:** Đường p95 và p99 tăng dốc đứng chạm ngưỡng timeout (3,000 ms).
