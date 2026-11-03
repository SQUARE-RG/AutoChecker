#include <cstddef>

class IntBuffer {
public:
    IntBuffer(int* data, std::size_t size) : data_(data), size_(size) {}

    const int& at(std::size_t index) const {
        return data_[index];
    }

private:
    int* data_;
    std::size_t size_;
};

int main() {
    int values[3] = {1, 2, 3};
    const IntBuffer buffer(values, 3);
    int value = buffer.at(0);
    return value;
}
