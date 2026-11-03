#include <cstddef>

class IntBuffer {
public:
    IntBuffer(int* data, std::size_t size) : data_(data), size_(size) {}

    int& at(std::size_t index) const { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-2]
        return data_[index];
    }

private:
    int* data_;
    std::size_t size_;
};

int main() {
    int values[3] = {1, 2, 3};
    const IntBuffer buffer(values, 3);
    buffer.at(0) = 42;
    return 0;
}
