#include <iostream>

class Buffer {
public:
    Buffer();
    ~Buffer() { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-7-1]
        open = false;
    }

    bool isOpen() const;

private:
    bool open;
};

Buffer::Buffer() {
    open = true;
}

bool Buffer::isOpen() const {
    return open;
}

int main() {
    Buffer b;
    std::cout << (b.isOpen() ? "open" : "closed") << std::endl;
    return 0;
}
