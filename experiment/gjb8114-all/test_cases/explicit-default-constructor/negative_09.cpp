#include <cstddef>

class Buffer { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-2]
public:
    Buffer(Buffer&& other) noexcept;
    ~Buffer();
    Buffer& operator=(Buffer&& other) noexcept;
    std::size_t size() const;
private:
    int* data_;
    std::size_t size_;
};

Buffer::Buffer(Buffer&& other) noexcept : data_(other.data_), size_(other.size_) {
    other.data_ = nullptr;
    other.size_ = 0;
}

Buffer::~Buffer() {
    delete[] data_;
}

Buffer& Buffer::operator=(Buffer&& other) noexcept {
    if (this != &other) {
        delete[] data_;
        data_ = other.data_;
        size_ = other.size_;
        other.data_ = nullptr;
        other.size_ = 0;
    }
    return *this;
}

std::size_t Buffer::size() const {
    return size_;
}

int main() {
    return 0;
}
