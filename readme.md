# llm-trace-fidelity

Kiểm chứng: LLM sinh test case đạt đúng coverage/nhánh mục tiêu (outcome
đúng) không có nghĩa là nó suy luận đúng giá trị biến ở từng bước thực
thi (trace đúng). Đo bằng cách so hai chuỗi trace: một từ LLM tự suy
luận, một lấy từ chương trình chạy thật (ground truth qua GDB).

## Các bước

**1. Chọn hàm target**
Lấy một hàm thật (ví dụ một hàm parser trong HJSON/JSON, hoặc dùng
tạm `target.cpp` có sẵn trong repo này để chạy thử trước). Điều kiện:
có vòng lặp + biến trạng thái thay đổi theo điều kiện (dễ sai). Chỉnh
`target.cpp`/build command cho khớp hàm bạn chọn, miễn compile chạy
được với `-g -O0`.
```bash
g++ -g -O0 -o target target.cpp
```
`-O0` bắt buộc — tối ưu hoá compiler sẽ xáo trộn dòng lệnh/loại bỏ
biến, làm sai lệch không còn là lỗi của LLM nữa mà là do compiler.

**2. LLM outcome**
Đưa code hàm này cho LLM, yêu cầu nó sinh một input (test case) đạt
một nhánh/coverage cụ thể (ví dụ: input làm `depth` âm, hoặc input đi
qua nhánh escape). Lưu lại input này — dùng input NÀY cho bước 3 và 4,
không dùng input khác.

**3. GDB — lấy ground-truth trace**
```bash
gdb -q -batch -x gdb_tracer.py --args ./target '<input LLM vừa sinh>'
```
→ ghi ra `truth_trace.json`.

**4. LLM trace**
Cùng input đó, yêu cầu LLM mô phỏng thực thi từng dòng, in ra state
biến theo đúng format JSON như `truth_trace.json` (prompt mẫu ở cuối
`compare_trace.py`). Lưu kết quả vào `llm_trace.json`.

**5. So sánh**
```bash
python3 compare_trace.py truth_trace.json llm_trace.json
```
Ra % khớp theo từng (dòng, biến), phân loại lỗi: sai nhánh/thứ tự dòng
(`WRONG_LINE`), sai giá trị biến (`WRONG_VALUE`), thiếu biến
(`MISSING_VAR`).

**Diễn giải:** nếu bước 2 đúng (input đạt coverage) nhưng bước 5 tỷ lệ
khớp thấp / lỗi tăng theo số bước → outcome đúng không đến từ việc mô
phỏng đúng ngữ nghĩa thực thi, mà nhiều khả năng từ pattern-matching
cấu trúc code. Tránh kết luận "LLM không hiểu chương trình" (quá mạnh);
bám vào số liệu: "độ chính xác outcome không tương quan với độ chính
xác trace".

## Literature liên quan 

- *What I cannot execute, I do not understand: Training and Evaluating
  LLMs on Program Execution Traces* — arxiv.org/abs/2503.05703
- *Reasoning Runtime Behavior of a Program with LLM: How Far Are We?* —
  arxiv.org/abs/2403.16437
- *A Tool for In-depth Analysis of Code Execution Reasoning of Large
  Language Models (ExeRScope)* — arxiv.org/abs/2501.18482
- *Demystifying Errors in LLM Reasoning Traces* — arxiv.org/abs/2512.00215
- *The Double Life of Code World Models* — arxiv.org/abs/2512.13821# llm-trace-fidelity

