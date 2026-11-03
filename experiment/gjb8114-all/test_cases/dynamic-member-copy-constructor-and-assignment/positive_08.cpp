#include <algorithm>
#include <cstddef>

class IntArray {
public:
    explicit IntArray(std::size_t n = 1) : data(new int[n]()), size(n) {}
    IntArray(const IntArray& other)
        : data(new int[other.size]()), size(other.size) {
        std::copy(other.data, other.data + other.size, data);
    }
    IntArray& operator=(const IntArray& other) {
        if (this != &other) {
            int* next = new int[other.size]();
            std::copy(other.data, other.data + other.size, next);
            delete[] data;
            data = next;
            size = other.size;
        }
        return *this;
    }
    ~IntArray() { delete[] data; }
private:
    int* data;
    std::size_t size;
};

int main() {
    IntArray a(3);
    IntArray b(a);
    a = b;
    return 0;
}
