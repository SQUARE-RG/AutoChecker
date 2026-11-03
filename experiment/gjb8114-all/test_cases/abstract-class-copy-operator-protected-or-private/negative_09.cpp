class B {
public:
    virtual ~B() = default;
    virtual void f() = 0;
    void operator=(B const& rhs) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-4]
        kind = rhs.kind;
    }
private:
    int kind = 0;
};
