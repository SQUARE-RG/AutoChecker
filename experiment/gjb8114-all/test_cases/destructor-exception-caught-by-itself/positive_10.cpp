enum class CleanupCode {
    Failure
};

class Foo {
public:
    ~Foo() noexcept(false);
};

Foo::~Foo() noexcept(false) {
    try {
        throw CleanupCode::Failure;
    } catch (CleanupCode) {
    }
}

int main() {
    Foo f;
    return 0;
}
