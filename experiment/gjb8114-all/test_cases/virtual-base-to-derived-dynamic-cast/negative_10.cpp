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
    D d;
    B& b = d;
    D* pd = reinterpret_cast<D*>(std::addressof(b)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-2]
    (void)pd;
    return 0;
}
