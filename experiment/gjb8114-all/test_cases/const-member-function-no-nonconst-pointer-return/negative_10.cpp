#include <array>

class Store {
public:
    int* data() const { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-2]
        return values_.data();
    }

private:
    mutable std::array<int, 4> values_ = {1, 2, 3, 4};
};

int main() {
    const Store store;
    int* p = store.data();
    p[0] = 99;
    return 0;
}
