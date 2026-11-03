#include <memory>

class B {
public:
    virtual ~B() = default;
};

class D : public virtual B {
public:
    ~D() override = default;
};

int main() {
    std::unique_ptr<B> pb(new D);
    D* pd = reinterpret_cast<D*>(pb.get()); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-2]
    (void)pd;
    return 0;
}
