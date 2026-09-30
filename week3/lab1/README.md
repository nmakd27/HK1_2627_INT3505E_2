# Thiết kế resource cho Blog API

## 1. Resources chính

- `users`: Người dùng / tác giả
- `posts`: Bài viết
- `comments`: Bình luận
- `tags`: Thẻ bài viết
- `profile`: Hồ sơ người dùng
- `followers` / `following`: Quan hệ theo dõi

## 2. Phân loại Resource

- **Collection**: `/posts`, `/users`, `/tags`

- **Item**: `/posts/{id}`, `/users/{id}`, `/tags/{id}`

- **Sub-resource**:
  - `/posts/{id}/comments` (Collection)
  - `/posts/{id}/comments/{id}` (Item)
  - `/posts/{id}/tags`
  - `/posts/{id}/tags/{id}`
  - `/users/{id}/posts`
  - `/users/{id}/followers`
  - `/users/{id}/following/{target_id}`

- **Singleton**: `/users/{id}/profile`

## 3. Sơ đồ cây Endpoint

```text
/api/v1
├── /posts
│   └── /{id}
│       ├── /comments
│       │   └── /{id}
│       └── /tags
│           └── /{id}
├── /users
│   └── /{id}
│       ├── /profile
│       ├── /posts
│       ├── /followers
│       └── /following
│           └── /{target_id}
└── /tags
    └── /{id}
        └── /posts
