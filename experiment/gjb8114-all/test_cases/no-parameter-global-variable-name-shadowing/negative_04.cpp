#include <cstring>

const char* name = "default";

int length(const char* name) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-2]
{
    return name == nullptr ? 0 : static_cast<int>(std::strlen(name));
}

int main()
{
    return length("hello");
}
