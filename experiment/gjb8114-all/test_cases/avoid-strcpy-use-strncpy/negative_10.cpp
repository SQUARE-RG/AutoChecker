#include <cstring>

class DeviceName {
public:
    explicit DeviceName(const char* name) : buffer_{} {
        using namespace std;
        strcpy(buffer_, name); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-4]
    }

    const char* c_str() const {
        return buffer_;
    }

private:
    char buffer_[32];
};
