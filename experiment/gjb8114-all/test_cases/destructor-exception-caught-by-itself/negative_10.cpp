enum class CleanupCode {
    Failure
};

class Foo {
public:
    ~Foo() noexcept(false);
};

Foo::~Foo() noexcept(false) {
    throw CleanupCode::Failure; // CHECK-MESSAGES: :[[@LINE]]:5: warning: {{.*}} [ucassaat-r-2-3-2]
}

int main() {
    try {
        Foo f;
    } catch (CleanupCode) {
    }
    return 0;
}
