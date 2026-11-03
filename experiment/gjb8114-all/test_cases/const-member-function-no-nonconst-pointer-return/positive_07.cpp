#include <cstddef>

class IntBuffer {
public:
    explicit IntBuffer(std::size_t n) : size(n), data(new int[n]{}) {}
    ~IntBuffer() { delete[] data; }
    IntBuffer(const IntBuffer&) = delete;
    IntBuffer& operator=(const IntBuffer&) = delete;

    using ConstIntPtr = const int*;
    ConstIntPtr get_data() const;

private:
    std::size_t size;
    int* data;
};

IntBuffer::ConstIntPtr IntBuffer::get_data() const {
    return data;
}

int main() {
    IntBuffer buffer(4);
    const IntBuffer& view = buffer;
    int first = view.get_data()[0];
    (void)first;
    return 0;
}
