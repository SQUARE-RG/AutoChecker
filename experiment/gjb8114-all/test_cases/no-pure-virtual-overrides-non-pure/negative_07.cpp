struct Base {
    virtual void run() noexcept {}
    virtual ~Base() = default;
};

struct Derived : Base {
    virtual void run() noexcept override = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-3]
};

int main() {
    Base* p = nullptr;
    p->run();
    return 0;
}
