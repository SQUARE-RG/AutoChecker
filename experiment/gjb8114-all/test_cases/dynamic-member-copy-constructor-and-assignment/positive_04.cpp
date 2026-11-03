#include <algorithm>
#include <cstddef>
#include <utility>

class TextBuffer {
public:
    explicit TextBuffer(const char* text);
    TextBuffer(const TextBuffer& other);
    TextBuffer(TextBuffer&& other) noexcept;
    TextBuffer& operator=(const TextBuffer& other);
    TextBuffer& operator=(TextBuffer&& other) noexcept;
    ~TextBuffer();

    std::size_t size() const { return size_; }
private:
    char* data_;
    std::size_t size_;
};

TextBuffer::TextBuffer(const char* text) : data_(nullptr), size_(0) {
    size_ = 0;
    while (text[size_] != '\0') {
        ++size_;
    }
    data_ = new char[size_ + 1];
    std::copy(text, text + size_ + 1, data_);
}

TextBuffer::TextBuffer(const TextBuffer& other)
    : data_(new char[other.size_ + 1]), size_(other.size_) {
    std::copy(other.data_, other.data_ + size_ + 1, data_);
}

TextBuffer::TextBuffer(TextBuffer&& other) noexcept
    : data_(other.data_), size_(other.size_) {
    other.data_ = nullptr;
    other.size_ = 0;
}

TextBuffer& TextBuffer::operator=(const TextBuffer& other) {
    if (this != &other) {
        char* new_data = new char[other.size_ + 1];
        std::copy(other.data_, other.data_ + other.size_ + 1, new_data);
        delete[] data_;
        data_ = new_data;
        size_ = other.size_;
    }
    return *this;
}

TextBuffer& TextBuffer::operator=(TextBuffer&& other) noexcept {
    if (this != &other) {
        delete[] data_;
        data_ = other.data_;
        size_ = other.size_;
        other.data_ = nullptr;
        other.size_ = 0;
    }
    return *this;
}

TextBuffer::~TextBuffer() { delete[] data_; }

int main() {
    TextBuffer a("hello");
    TextBuffer b(a);
    b = a;
    TextBuffer c(std::move(a));
    return static_cast<int>(c.size());
}
