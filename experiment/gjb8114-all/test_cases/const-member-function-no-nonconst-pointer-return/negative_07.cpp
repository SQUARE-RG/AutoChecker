#include <cstddef>

class IntBuffer {
public:
    explicit IntBuffer(std::size_t n) : size(n), data(new int[n]{}) {}
    ~IntBuffer() { delete[] data; }
    IntBuffer(const IntBuffer&) = delete;
    IntBuffer& operator=(const IntBuffer&) = delete;

    using IntPtr = int*;
    IntPtr get_data() const; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-2]

private:
    std::size_t size;
    int* data;
};

IntBuffer::IntPtr IntBuffer::get_data() const {
    return data;
}

int main() {
    IntBuffer buffer(4);
    const IntBuffer& view = buffer;
    view.get_data()[0] = 42;
    return 0;
}
