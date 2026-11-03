#include <algorithm>

class PointerAssignment {
public:
    PointerAssignment() : data(new int[3]{0, 0, 0}) {}
    PointerAssignment(const PointerAssignment& other) : data(new int[3]) {
        std::copy(other.data, other.data + 3, data);
    }
    ~PointerAssignment() { delete[] data; }

    PointerAssignment& operator=(PointerAssignment* other) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-1]
        if (other != nullptr) {
            std::copy(other->data, other->data + 3, data);
        }
        return *this;
    }

private:
    int* data;
};

int main() {
    PointerAssignment a;
    PointerAssignment b(a);
    a = &b;
    return 0;
}
