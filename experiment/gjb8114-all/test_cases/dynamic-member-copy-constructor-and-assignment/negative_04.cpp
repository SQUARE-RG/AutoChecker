#include <cstddef>
#include <utility>

class RawBuffer { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-1]
public:
    explicit RawBuffer(std::size_t n);
    RawBuffer(RawBuffer&& other) noexcept;
    RawBuffer& operator=(RawBuffer&& other) noexcept;
    ~RawBuffer();
    std::size_t size() const { return size_; }
private:
    int* data_;
    std::size_t size_;
};

RawBuffer::RawBuffer(std::size_t n) : data_(new int[n]), size_(n) {}

RawBuffer::RawBuffer(RawBuffer&& other) noexcept : data_(other.data_), size_(other.size_) {
    other.data_ = nullptr;
    other.size_ = 0;
}

RawBuffer& RawBuffer::operator=(RawBuffer&& other) noexcept {
    if (this != &other) {
        delete[] data_;
        data_ = other.data_;
        size_ = other.size_;
        other.data_ = nullptr;
        other.size_ = 0;
    }
    return *this;
}

RawBuffer::~RawBuffer() { delete[] data_; }

int main() {
    RawBuffer a(4);
    RawBuffer b(std::move(a));
    return static_cast<int>(b.size());
}
