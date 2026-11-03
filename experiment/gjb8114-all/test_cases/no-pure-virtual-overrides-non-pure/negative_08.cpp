struct Base {
    virtual ~Base() {}
};

struct Derived : Base {
    virtual ~Derived() = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-3]
};

Derived::~Derived() {}

int main() {
    Base* p = nullptr;
    delete p;
    return 0;
}
