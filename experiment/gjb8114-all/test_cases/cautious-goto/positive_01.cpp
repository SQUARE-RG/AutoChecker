// positive_01.cpp
// 场景：提前返回避免使用 goto 向前跳转。
int work(bool skip) {
    if (skip) {
        return 0;
    }
    return 42;
}

int main() {
    return work(true);
}
