#include <cstring>

class DynamicBuffer { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-1]
public:
    explicit DynamicBuffer(const char* text) {
        data_ = new char[32];
        std::strncpy(data_, text, 31);
        data_[31] = '\0';
    }
    ~DynamicBuffer() {
        delete[] data_;
    }
private:
    char* data_;
};

int main() {
    DynamicBuffer buffer("example");
    return 0;
}
