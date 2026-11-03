#include <cstddef>

class ArrayBox {
public:
    ArrayBox(int values[3]) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-1]
    {
        for (std::size_t i = 0; i < 3; ++i) {
            stored_[i] = values[i];
        }
    }

    int at(std::size_t index) const {
        return stored_[index];
    }

private:
    int stored_[3] = {0, 0, 0};
};

int main() {
    int source[3] = {4, 5, 6};
    ArrayBox box(source);
    return box.at(0);
}
