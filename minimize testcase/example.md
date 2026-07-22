# LLM Test Minimization Pipeline — General Flow

Pipeline dùng DFG (Data Flow Graph) backward slicing để ràng buộc LLM
sinh test driver tối giản, vẫn giữ coverage tương đương so với driver
không bị ràng buộc.

## Tham số cần xác định trước mỗi lần chạy

| Tham số | Ý nghĩa | Ví dụ |
|---|---|---|
| `<SOURCE_FILE>` | File .cpp chứa hàm target | `../hjson-cpp/src/hjson_decode.cpp` |
| `<TARGET_FUNCTION>` | Tên hàm cần test | `_escapee` |
| `<TARGET_LINE>` | Dòng cụ thể trong 1 nhánh (case/if) cần slice | `15` |

## Bước 0 — Chọn hàm target
```
python find_high_cc_in_this_file.py
python find_exclusive_cc.py
```
Chọn hàm có `exclusivity_ratio` cao (gần 1.0) — ưu tiên hàm có cấu trúc
switch/if-else rẽ nhánh loại trừ lẫn nhau, vì đây là điều kiện để DFG
slicing theo từng nhánh có ý nghĩa (xem README/thảo luận trước về lý do
loại các hàm dạng vòng lặp tuần tự như parser).

## Bước 1 — Trích context tĩnh

```
python extract_AST.py <SOURCE_FILE> <TARGET_FUNCTION>
```
Output: struct/enum/function body liên quan, dùng làm `{context}` trong
prompt.

## Bước 2 — Sinh driver BASELINE (không có ràng buộc DFG)

Điền `prompt_initial.txt`:
```
{context} <- output Bước 1
{focal_function} <- <TARGET_FUNCTION>
{target_branch} <- mô tả mục tiêu (vd: "Maximize coverage for <TARGET_FUNCTION>")
{target_cpp_path} <- <SOURCE_FILE>
```

Đưa cho LLM (thủ công) → lưu `driver_<TARGET_FUNCTION>_baseline.cpp`

Nếu compile lỗi: điền `prompt_fix.txt` (`{previous_code}`, `{compiler_errors}`,
`{context}`) → đưa LLM → lưu đè → lặp lại tới khi pass.

Nếu compile pass nhưng coverage thấp: điền `prompt_reflect.txt`
(`{target_branch}`, `{previous_code}`, `{visited_trace}` — lấy từ GDB
tracer nếu cần chi tiết giá trị biến) → lặp lại.

## Bước 3 — Đo coverage BASELINE

```
python check_cov.py driver_<TARGET_FUNCTION>_baseline.cpp
```

Output: `coverage_data/driver_<TARGET_FUNCTION>_baseline/`
(`coverage.html`, `coverage.json`, `coverage.csv`, `summary.txt`)

Ghi lại: line coverage %, branch coverage %, số dòng trong `main()`,
số lần driver gọi `<TARGET_FUNCTION>()`.

## Bước 4 — Trích DFG slice cho từng nhánh cần test

Xác định các `<TARGET_LINE>` ứng với từng case/nhánh muốn cắt giảm
(đọc source từ Bước 1, chọn dòng đầu tiên bên trong mỗi case/if-branch
quan tâm).

Với mỗi `<TARGET_LINE>`:
```
python extract_dfg_slice.py <SOURCE_FILE> <TARGET_FUNCTION> <TARGET_LINE>
```

Output: `dfg_slice_line<TARGET_LINE>.json`, chứa `relevant_vars` — tập
biến thực sự cần thiết để tới đúng nhánh đó.

## Bước 5 — Sinh driver STRICT (có ràng buộc DFG)

Gộp `relevant_vars` từ mọi `dfg_slice_line*.json` liên quan, điền vào
`prompt_initial_strict.txt`:

```
{context} <- output Bước 1
{focal_function} <- <TARGET_FUNCTION>
{dfg_slice} <- relevant_vars gộp từ Bước 4, ghi rõ theo từng nhánh
{target_cpp_path} <- <SOURCE_FILE>
```
Đưa LLM → lưu `driver_<TARGET_FUNCTION>_strict.cpp`

Cùng cơ chế lặp `prompt_fix.txt` / `prompt_reflect.txt` như Bước 2 nếu
cần.

## Bước 6 — Đo coverage STRICT
```
python check_cov.py driver_<TARGET_FUNCTION>_strict.cpp
```

Ghi lại cùng các chỉ số như Bước 3.

## Bước 7 (tuỳ chọn, nếu còn thời gian) — Verify bằng thực nghiệm
```
python prune.py driver_<TARGET_FUNCTION>_strict.cpp <TARGET_FUNCTION> <TARGET_LINE>
```

Thử xoá thêm từng dòng còn lại trong driver strict, verify bằng compile
+ chạy + đo coverage thật (`gcov`), không tin suông vào slice tĩnh.

## Bước 8 — So sánh kết quả

| | baseline | strict |
|---|---|---|
| Dòng trong `main()` | | |
| Số lần gọi hàm target | | |
| Line coverage % | | |
| Branch coverage % | | |

Kết luận mong đợi: strict có số dòng/số lần gọi ít hơn rõ rệt, coverage
% xấp xỉ baseline (không giảm đáng kể).

## Lặp lại cho hàm target khác

Quay lại Bước 0, chọn hàm mới, lặp lại toàn bộ — mọi tham số
`<SOURCE_FILE>`/`<TARGET_FUNCTION>`/`<TARGET_LINE>` được thay theo hàm mới,
không có phần nào trong flow phụ thuộc cứng vào 1 hàm cụ thể.