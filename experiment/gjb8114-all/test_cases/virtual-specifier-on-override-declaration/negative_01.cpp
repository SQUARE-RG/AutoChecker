class Base {
public:
    virtual ~Base() = default;
    virtual int value(int x = 0) const { return x; }
};

class Derived : public Base {
public:
    int value(int x = 0) const; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-2]
};

int Derived::value(int x) const {
    return x + 1;
}

int main() {
    Derived d;
    const Base& b = d;
    return b.value();
}
