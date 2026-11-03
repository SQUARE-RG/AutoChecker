class Buffer {
public:
    Buffer() : Buffer(16) {}
    explicit Buffer(int size);
    int size() const;
private:
    int size_;
};

Buffer::Buffer(int size) : size_(size > 0 ? size : 1) {}

int Buffer::size() const {
    return size_;
}

int main() {
    Buffer b;
    return b.size() == 16 ? 0 : 1;
}
