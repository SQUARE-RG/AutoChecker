class Base {
public:
    Base() = default;
    explicit Base(int value) : value_(value) {}
    int value() const { return value_; }
private:
    int value_ = 0;
};

class Derived : public Base { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-2]
public:
    using Base::Base;
};

int main() {
    Derived d(42);
    return d.value();
}
