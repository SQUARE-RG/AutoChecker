class Base {
public:
    virtual ~Base() = default;
};

struct Derived : virtual Base {  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-1-1]
    ~Derived() override = default;
};
