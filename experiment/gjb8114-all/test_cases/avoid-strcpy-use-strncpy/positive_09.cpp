#include <cstring>

class DeviceName {
public:
    explicit DeviceName(const char* name) : buffer_{} {
        if (name == nullptr) {
            return;
        }
        std::strncpy(buffer_, name, sizeof(buffer_) - 1);
        buffer_[sizeof(buffer_) - 1] = '\0';
    }

    const char* c_str() const {
        return buffer_;
    }

private:
    char buffer_[32];
};
