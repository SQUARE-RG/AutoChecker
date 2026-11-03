#include <cstring>

class Text {
public:
    explicit Text(const char* s) {
        data_ = new char[64];
        std::strncpy(data_, s, 63);
        data_[63] = '\0';
    }
    Text(const Text& other) {
        data_ = new char[64];
        std::strncpy(data_, other.data_, 63);
        data_[63] = '\0';
    }
    Text& operator=(const Text& other) {
        if (this != &other) {
            char* new_data = new char[64];
            std::strncpy(new_data, other.data_, 63);
            new_data[63] = '\0';
            delete[] data_;
            data_ = new_data;
        }
        return *this;
    }
    ~Text() {
        delete[] data_;
    }
private:
    char* data_;
};

int main() {
    Text a("alpha");
    Text b(a);
    b = a;
    return 0;
}
