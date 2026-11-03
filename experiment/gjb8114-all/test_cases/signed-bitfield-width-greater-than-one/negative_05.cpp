struct Outer {
    struct {
        signed int flag : 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-10]
    } inner;
};

int main() {
    Outer obj{};
    obj.inner.flag = -1;
    return 0;
}
