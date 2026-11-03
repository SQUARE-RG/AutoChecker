struct Base {
    virtual ~Base() = default;
};

struct Derived : Base {};

Base* make_base() {
    Derived d;
    return static_cast<Base*>(&d); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-4]
}

int main() {
    return 0;
}
