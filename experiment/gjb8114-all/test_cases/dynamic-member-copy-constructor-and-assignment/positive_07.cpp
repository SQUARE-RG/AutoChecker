#include <algorithm>
#include <cstddef>
#include <utility>

template <typename T>
class Buffer {
public:
    explicit Buffer(std::size_t n = 1) : data(new T[n]), size(n) {}
    Buffer(const Buffer& other) : data(new T[other.size]), size(other.size) {
        std::copy(other.data, other.data + other.size, data);
    }
    Buffer& operator=(const Buffer& other) {
        if (this != &other) {
            Buffer tmp(other);
            swap(tmp);
        }
        return *this;
    }
    ~Buffer() { delete[] data; }
    void swap(Buffer& other) noexcept {
        std::swap(data, other.data);
        std::swap(size, other.size);
    }
private:
    T* data;
    std::size_t size;
};

int main() {
    Buffer<int> a(3);
    Buffer<int> b(a);
    a = b;
    return 0;
}
