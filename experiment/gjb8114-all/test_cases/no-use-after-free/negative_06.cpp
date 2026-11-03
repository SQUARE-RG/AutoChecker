#include <memory>

int main()
{
    auto sp = std::make_shared<int>(42);
    int *raw = sp.get();
    sp.reset();

    int y = *raw; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-16]
    return y;
}
