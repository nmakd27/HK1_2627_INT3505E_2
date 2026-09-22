# Bài tập 2: Audit một Public API thực – GitHub REST API

## Endpoint 1: Lấy thông tin một GitHub user

**Method:** `GET`

**URL:** `/users/{username}`

**Status code:**

* `200 OK`: lấy thông tin user thành công.
* `404 Not Found`: không tìm thấy user.

**Headers:**

* `Accept: application/vnd.github+json`
* `X-GitHub-Api-Version: 2026-03-10`

**RESTful:** Có. URL `/users/{username}` đại diện cho resource `user`. `GET` được sử dụng để đọc dữ liệu của resource. URL không sử dụng động từ.

---

## Endpoint 2: Lấy thông tin của một repository

**Method:** `GET`

**URL:** `/repos/{owner}/{repo}`

**Status code:**

* `200 OK`: repository được tìm thấy và trả về thành công.
* `301 Moved Permanently`: repository đã được chuyển sang địa chỉ khác.
* `404 Not Found`: không tìm thấy repository.

**Headers:**

* `Accept: application/vnd.github+json`
* `X-GitHub-Api-Version: 2026-03-10`

**RESTful:** Có. URL `/repos/{owner}/{repo}` đại diện cho một repository cụ thể. `GET` được sử dụng để đọc resource. URL không chứa động từ.

---

## Endpoint 3: Lấy danh sách các issue của một repository

**Method:** `GET`

**URL:** `/repos/{owner}/{repo}/issues`

**Status code:**

* `200 OK`: lấy danh sách issue thành công.
* `301 Moved Permanently`: repository đã được chuyển.
* `404 Not Found`: không tìm thấy resource.
* `422 Unprocessable Content`: request không hợp lệ hoặc endpoint bị GitHub đánh dấu là spam.

**Headers:**

* `Accept: application/vnd.github+json`
* `X-GitHub-Api-Version: 2026-03-10`

**RESTful:** Có. `/issues` đại diện cho một collection resource gồm các issue của repository. `GET` dùng để đọc collection.

---

## Endpoint 4: Tạo một issue mới trong repository

**Method:** `POST`

**URL:** `/repos/{owner}/{repo}/issues`

**Status code:**

* `201 Created`: tạo issue thành công.
* `400 Bad Request`: request không hợp lệ.
* `403 Forbidden`: không có quyền thực hiện thao tác.
* `404 Not Found`: không tìm thấy repository hoặc resource.
* `410 Gone`: resource không còn tồn tại.
* `422 Unprocessable Content`: validation thất bại hoặc request bị đánh dấu là spam.
* `503 Service Unavailable`: dịch vụ GitHub hiện không khả dụng.

**Headers:**

* `Accept: application/vnd.github+json`
* `Authorization: Bearer <YOUR-TOKEN>`
* `X-GitHub-Api-Version: 2026-03-10`

**RESTful:** Có. URL `/issues` đại diện cho collection `issues`, không chứa động từ. `POST` dùng để tạo một resource mới. API trả về `201 Created` khi POST thành công.

---

## Endpoint 5: Lấy thông tin của một issue trong repository.

**Method:** `GET`

**URL:** `/repos/{owner}/{repo}/issues/{issue_number}`

**Path parameters:**

* `owner`: tên tài khoản sở hữu repository.
* `repo`: tên repository.
* `issue_number`: số của issue cần lấy.

**Status code:**

* `200 OK`: lấy issue thành công.
* `301 Moved Permanently`: repository đã được chuyển.
* `304 Not Modified`: resource chưa thay đổi.
* `404 Not Found`: không tìm thấy repository hoặc issue.
* `410 Gone`: resource không còn tồn tại.

**Headers:**

* `Accept: application/vnd.github+json`
* `X-GitHub-Api-Version: 2026-03-10`

**RESTful:** Có. URL `/issues/{issue_number}` đại diện cho một resource issue cụ thể trong collection `issues`. `GET` được sử dụng để đọc resource. URL không chứa động từ.
