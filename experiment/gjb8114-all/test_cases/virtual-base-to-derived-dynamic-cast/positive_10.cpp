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
    D* pd = dynamic_cast<D*>(std::addressof(b));
    if (pd == nullptr) {
        return 1;
    }
    return 0;
}
