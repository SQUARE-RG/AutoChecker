#include <cstring>

class InClassBuffer {
public:
    InClassBuffer() = default;

    InClassBuffer(const InClassBuffer& other) : data(new char[16]) {
        std::strncpy(data, other.data, 16);
        data[15] = '\0';
    }

    InClassBuffer& operator=(const InClassBuffer& other) {
        if (this != &other) {
            char* replacement = new char[16];
            std::strncpy(replacement, other.data, 16);
            replacement[15] = '\0';
            delete[] data;
            data = replacement;
        }
        return *this;
    }

    ~InClassBuffer() { delete[] data; }

    void mark(char value) { data[0] = value; }

private:
    char* data = new char[16];
};

int main() {
    InClassBuffer first;
    first.mark('A');
    InClassBuffer second(first);
    InClassBuffer third;
    third = second;
    return 0;
}
