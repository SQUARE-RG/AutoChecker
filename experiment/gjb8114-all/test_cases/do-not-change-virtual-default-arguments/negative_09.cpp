class Base {
public:
    virtual ~Base() = default;
    virtual const char* label(const char* prefix = "base") const { return prefix; }
};

class Derived : public Base {
public:
    const char* label(const char* prefix = "derived") const override; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-1]
};

const char* Derived::label(const char* prefix) const {
    return prefix;
}

int main() {
    Derived d;
    const char* result = d.label();
    (void)result;
    return 0;
}
