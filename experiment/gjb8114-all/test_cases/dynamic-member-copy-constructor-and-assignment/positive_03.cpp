#include <cstddef>

class ScalarBox {
public:
    explicit ScalarBox(int v);
    ScalarBox(const ScalarBox& other);
    ScalarBox& operator=(const ScalarBox& other);
    ~ScalarBox();
    int value() const { return *value_; }
private:
    int* value_;
};

ScalarBox::ScalarBox(int v) : value_(new int(v)) {}

ScalarBox::ScalarBox(const ScalarBox& other) : value_(new int(*other.value_)) {}

ScalarBox& ScalarBox::operator=(const ScalarBox& other) {
    if (this != &other) {
        *value_ = *other.value_;
    }
    return *this;
}

ScalarBox::~ScalarBox() { delete value_; }

int main() {
    ScalarBox a(5);
    ScalarBox b(a);
    b = a;
    return b.value();
}
