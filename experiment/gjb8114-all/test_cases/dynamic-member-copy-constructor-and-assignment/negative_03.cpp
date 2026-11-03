#include <cstddef>

class IntHolder { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-1]
public:
    explicit IntHolder(int value);
    ~IntHolder();
    IntHolder& operator=(const IntHolder& other);
    int value() const { return *value_; }
private:
    int* value_;
};

IntHolder::IntHolder(int value) : value_(new int(value)) {}

IntHolder::~IntHolder() { delete value_; }

IntHolder& IntHolder::operator=(const IntHolder& other) {
    if (this != &other) {
        *value_ = *other.value_;
    }
    return *this;
}

int main() {
    IntHolder a(1);
    IntHolder b(2);
    b = a;
    return b.value();
}
