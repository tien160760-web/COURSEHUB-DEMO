import test from "node:test";
import assert from "node:assert/strict";
import { api } from "../src/api.js";

// Tạo phản hồi JSON giả lập.
function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

test("GET: trả về dữ liệu JSON", async (t) => {
  const rows = [
    { class_id: "WEB-01", remaining: 1 },
  ];

  t.mock.method(globalThis, "fetch", async (url, options) => {
    assert.ok(url.endsWith("/sections"));
    assert.equal(options.method, "GET");
    assert.equal(options.body, undefined);

    return jsonResponse(rows);
  });

  const result = await api("/sections");

  assert.deepEqual(result, rows);
});

test("POST: gửi đúng JSON và đọc phản hồi 201", async (t) => {
  const payload = {
    student_id: "22000004",
    class_section_id: "WEB-01",
  };

  t.mock.method(globalThis, "fetch", async (url, options) => {
    assert.ok(url.endsWith("/enrollments"));
    assert.equal(options.method, "POST");
    assert.equal(options.headers["Content-Type"], "application/json");
    assert.deepEqual(JSON.parse(options.body), payload);

    return jsonResponse({ message: "Dang ky thanh cong" }, 201);
  });

  const result = await api("/enrollments", {
    method: "POST",
    body: payload,
  });

  assert.equal(result.message, "Dang ky thanh cong");
});

test("DELETE: xử lý 204 với body trống", async (t) => {
  t.mock.method(globalThis, "fetch", async (url, options) => {
    assert.equal(options.method, "DELETE");
    return new Response(null, { status: 204 });
  });

  const result = await api("/enrollments/22000004/WEB-01", {
    method: "DELETE",
  });

  assert.equal(result, null);
});

test("HTTP 409: giữ mã lỗi và thông báo từ Backend", async (t) => {
  t.mock.method(globalThis, "fetch", async () =>
    jsonResponse({ detail: "Lop hoc phan da het cho" }, 409),
  );

  await assert.rejects(
    () => api("/enrollments", { method: "POST", body: {} }),
    (error) => {
      assert.equal(error.status, 409);
      assert.equal(
        error.message,
        "HTTP 409: Lop hoc phan da het cho",
      );
      return true;
    },
  );
});

test("HTTP 422: ghép danh sách lỗi validation", async (t) => {
  t.mock.method(globalThis, "fetch", async () =>
    jsonResponse(
      {
        detail: [
          { msg: "Thieu ma sinh vien" },
          { msg: "Thieu ma lop" },
        ],
      },
      422,
    ),
  );

  await assert.rejects(
    () => api("/enrollments", { method: "POST", body: {} }),
    (error) => {
      assert.equal(error.status, 422);
      assert.equal(
        error.message,
        "HTTP 422: Thieu ma sinh vien; Thieu ma lop",
      );
      return true;
    },
  );
});

test("Phản hồi không phải JSON: báo lỗi rõ ràng", async (t) => {
  t.mock.method(globalThis, "fetch", async () =>
    new Response("<html>Server error</html>", { status: 500 }),
  );

  await assert.rejects(
    () => api("/sections"),
    /HTTP 500: phản hồi không phải JSON/,
  );
});

test("Lỗi mạng: báo lỗi và không tự gửi lại POST", async (t) => {
  let calls = 0;

  t.mock.method(globalThis, "fetch", async () => {
    calls += 1;
    throw new TypeError("Failed to fetch");
  });

  await assert.rejects(
    () => api("/enrollments", { method: "POST", body: {} }),
    /Không nhận được phản hồi API/,
  );

  assert.equal(calls, 1);
});

test("Hủy request: truyền signal và giữ nguyên AbortError", async (t) => {
  const controller = new AbortController();
  controller.abort();

  const abortError = new DOMException(
    "The operation was aborted",
    "AbortError",
  );

  t.mock.method(globalThis, "fetch", async (url, options) => {
    assert.equal(options.signal, controller.signal);
    throw abortError;
  });

  await assert.rejects(
    () => api("/sections", { signal: controller.signal }),
    (error) => {
      assert.equal(error, abortError);
      return true;
    },
  );
});