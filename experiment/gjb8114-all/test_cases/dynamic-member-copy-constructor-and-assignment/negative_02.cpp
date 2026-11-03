#include <cstring>

class IntArray { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-1]
public:
    explicit IntArray(int n) : size_(n), data_(new int[n]) {
        for (int i = 0; i < size_; ++i) {
            data_[i] = 0;
        }
    }
    IntArray(const IntArray& other) : size_(other.size_), data_(new int[other.size_]) {
        for (int i = 0; i < size_; ++i) {
            data_[i] = other.data_[i];
        }
    }
    ~IntArray() {
        delete[] data_;
    }
private:
    int* data_;
    int size_;
};

int main() {
    IntArray a(3);
    return 0;
}
