class Base {
public:
    Base() : id_(0) {}
    explicit Base(int id) : id_(id) {}
    int id_;
};

class Derived : public Base {
public:
    int value;

    Derived() // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-5]
    {
        value = 1;
    }
};

int main() {
    Derived d;
    return 0;
}
