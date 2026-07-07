---
title: 서버 개발시 사용되는 HTTP Status Code
date: 2026-07-07
description: HTTP Status Code 정리
---

**HTTP Status Code란?**
서버가 응답(Response)할 때 돌려주는 3자리 숫자로, 요청이 어떻게 처리되었는지를 나타내는 상태 값이다. "HTTP 상태 코드" 혹은 "HTTP Response Status Code"라고 부른다.

상태 코드는 첫 자리 숫자를 기준으로 아래의 5가지 범주로 나뉜다.

| 범위 | 이름 | 의미 |
|------|------|------|
| 1xx | Informational | 정보 (요청을 받았고 처리 중) |
| 2xx | Success | 성공 |
| 3xx | Redirection | 리다이렉트 (추가 동작 필요) |
| 4xx | Client Error | 클라이언트 에러 |
| 5xx | Server Error | 서버 에러 |

### 4xx — 클라이언트 에러 (Client Error)
요청한 쪽(클라이언트)에 문제가 있을 때 반환된다. 잘못된 요청, 권한 없음 등이 원인이다.

| 코드 | 이름 | 의미 |
|------|------|------|
| 400 | Bad Request | 요청 자체가 잘못됨 (문법 오류 등) |
| 401 | Unauthorized | 인증 안 됨 (로그인 필요) |
| 403 | Forbidden | 권한 없음 (인증됐지만 접근 불가) |
| 404 | Not Found | 리소스 없음 |
| 405 | Method Not Allowed | 허용되지 않은 HTTP 메서드 |
| 409 | Conflict | 충돌 (예: 중복 데이터) |
| 429 | Too Many Requests | 요청 과다 (rate limit) |

### 5xx — 서버 에러 (Server Error)
서버 쪽에 문제가 있을 때 반환된다. 요청은 정상이지만 서버가 처리에 실패한 경우다.

| 코드 | 이름 | 의미 |
|------|------|------|
| 500 | Internal Server Error | 서버 내부 오류 |
| 502 | Bad Gateway | 게이트웨이/프록시가 잘못된 응답을 받음 |
| 503 | Service Unavailable | 서버 과부하 / 점검 중 |
| 504 | Gateway Timeout | 게이트웨이 응답 시간 초과 |

### 핵심 구분
- **4xx = 클라이언트 잘못** (요청을 잘못 보냄)
- **5xx = 서버 잘못** (요청은 정상이나 서버가 처리 실패)
