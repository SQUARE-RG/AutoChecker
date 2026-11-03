class IntBox {
public:
    explicit IntBox(int v) : value(v) {}
    operator int*() { return &value; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-3]
private:
    int value;
};

int main() {
    IntBox box(3);
    int* p = box;
    *p = 7;
    return 0;
}
