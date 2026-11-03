#include <cstddef>

class ConstDynamicHolder { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-1]
public:
    ConstDynamicHolder() : data(new int[4]{1, 2, 3, 4}) {}
    ConstDynamicHolder(const ConstDynamicHolder& other) : data(new int[4]) {
        for (std::size_t i = 0; i < 4; ++i) {
            data[i] = other.data[i];
        }
    }
    ~ConstDynamicHolder() { delete[] data; }
private:
    int* const data;
};

int main() {
    ConstDynamicHolder original;
    ConstDynamicHolder copy(original);
    (void)copy;
    return 0;
}
