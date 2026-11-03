struct Base {
    virtual void method() {}
    virtual ~Base() = default;
};

struct Left : virtual Base {};
struct Right : virtual Base {};

struct Derived : Left, Right {
    void method() override = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-3]
};

int main() {
    return 0;
}
