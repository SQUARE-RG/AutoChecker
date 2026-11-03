#include <iostream>
#include <stdexcept>

class ResourceOwner {
public:
    explicit ResourceOwner(bool shouldFail) : shouldFail_(shouldFail) {}

    ~ResourceOwner() try {
        release();
    } catch (const std::exception& e) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-1]
        std::cout << "cleanup error: " << e.what() << std::endl;
    }

private:
    void release() {
        if (shouldFail_) {
            throw std::runtime_error("cleanup failed");
        }
    }

    bool shouldFail_;
};

int main() {
    ResourceOwner owner(false);
    (void)owner;
    return 0;
}
