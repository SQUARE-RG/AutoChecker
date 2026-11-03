struct Base {
    virtual void update(int value = 1) {
        (void)value;
    }
    virtual ~Base() = default;
};

struct Derived : Base {
    void update(int value) = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-3]
};

int main() {
    return 0;
}
