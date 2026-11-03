#include <cstring>

class InClassBuffer { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-1]
public:
    InClassBuffer() = default;
    ~InClassBuffer() { delete[] data; }
    void mark(char value) { data[0] = value; }
private:
    char* data = new char[16];
};

int main() {
    InClassBuffer first;
    first.mark('A');
    return 0;
}
