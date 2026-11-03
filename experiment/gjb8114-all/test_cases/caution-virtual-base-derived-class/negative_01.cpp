class Base {
public:
    virtual ~Base() = default;
};

class Derived : virtual public Base {  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-1-1]
public:
    ~Derived() override = default;
};
