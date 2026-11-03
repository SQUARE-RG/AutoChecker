#include <functional>

int scale(int value)
{
    return value * 3;
}

int main()
{
    auto scaled = std::bind(scale, 14);
    scaled(); // CHECK-MESSAGES: :[[@LINE]]:5: warning: {{.*}} [ucassaat-r-1-7-11]
    return 0;
}
