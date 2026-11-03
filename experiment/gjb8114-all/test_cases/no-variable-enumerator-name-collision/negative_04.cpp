#include <iostream>

enum Weekday { monday, tuesday, wednesday };

int main()
{
    int values[] = { 1, 2, 3 };
    for (int monday : values) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-5]
    {
        std::cout << monday << '\n';
    }
    return 0;
}
