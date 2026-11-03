struct Base {
    virtual void foo() const {}
    virtual ~Base() = default;
};

struct Derived : Base {
    virtual void foo() const = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-3]
};

int main() {
    return 0;
}
