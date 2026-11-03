struct Outer {
    struct {
        signed int flag : 2;
    } inner;
};

int main() {
    Outer obj{};
    obj.inner.flag = -1;
    return 0;
}
