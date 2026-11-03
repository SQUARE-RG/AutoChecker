#include <cstring>

class NameHolder {
public:
    void assign(const char* value) {
        std::strcpy(name_, value);  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-4]
    }

private:
    char name_[32];
};

int main() {
    NameHolder holder;
    holder.assign("text");
    return 0;
}
