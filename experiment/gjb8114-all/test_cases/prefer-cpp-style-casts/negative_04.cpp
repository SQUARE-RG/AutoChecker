struct Base {
    virtual ~Base() = default;
};

struct Derived : Base {
    int value = 0;
};

int main() {
    Base* base = new Derived;
    Derived* derived = (Derived*)base; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-5-1]
    derived->value = 7;
    delete base;
    return 0;
}
