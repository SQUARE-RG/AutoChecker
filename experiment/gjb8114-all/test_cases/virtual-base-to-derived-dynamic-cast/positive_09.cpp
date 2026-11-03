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
    D* pd = dynamic_cast<D*>(pb.get());
    if (pd == nullptr) {
        return 1;
    }
    return 0;
}
